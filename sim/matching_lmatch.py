#!/usr/bin/env python3
"""
matching_lmatch.py - 868 MHz L-match tasarim ve gorsellestirme araci (scikit-rf).

NE YAPAR
  - Verilen (kompleks) anten empedansini  ZL = R + jX  sistem empedansi Z0'a (50 Ohm)
    uyumlayan iki elemanli L-match agini hesaplar.
  - RL<Z0 ve RL>Z0 durumlari icin dogru topolojiyi otomatik secer.
  - Ideal L/C degerlerini en yakin E12 standart degerine yuvarlar ve ideal <-> E12
    farkini S11 (donus kaybi) ve Smith abagi grafiklerinde kiyaslar.

KAVRAM
  Uyumsuz yuk -> yansima (S11). Matching, yansimayi tek bir frekansta (f0) L/C ile
  sifira cekmektir. Smith abagi bu donusumun haritasidir. (CAN 120 Ohm sonlandirma
  sezgisinin frekansa bagli genellemesi.)

ORNEK KULLANIM
  python matching_lmatch.py                      # varsayilan ZL=40-30j, PNG uret
  python matching_lmatch.py --show               # grafik penceresi ac (interaktif)
  python matching_lmatch.py --zl 15              # dirensel yuk (15 Ohm)
  python matching_lmatch.py --zl 20-40j --show   # kompleks yuk + pencere
  python matching_lmatch.py --f0 433e6           # baska frekans (433 MHz)
  python matching_lmatch.py --help               # tum secenekler

Ciktilar (--no-save verilmedikce) sim/out/ altina PNG olarak kaydedilir.
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass

import numpy as np

# Backend secimi pyplot'tan ONCE yapilmali. --show yoksa headless "Agg" (sadece PNG);
# bulut/CI ortaminda ekran olmadigi icin varsayilan budur.
_WANT_SHOW = ("--show" in sys.argv) or (os.environ.get("SIM_SHOW") == "1")
import matplotlib
if not _WANT_SHOW:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import skrf as rf  # noqa: E402
from skrf.media import DefinedGammaZ0  # noqa: E402


# E12 standart deger serisi (on yilda 12 adim) = gercekte satin alinabilir degerler.
E12 = np.array([1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2])


def en_yakin_e12(x: float) -> float:
    """x'e en yakin E12 degerini dondurur (tum decade'ler taranir)."""
    dec = 10.0 ** np.floor(np.log10(x))
    aday = np.concatenate([E12 * dec / 10, E12 * dec, E12 * dec * 10])
    return float(aday[np.argmin(np.abs(aday - x))])


@dataclass
class Tasarim:
    """Bir L-match tasariminin sonucu. seri/sunt = ('L'|'C', deger[SI])."""
    Q: float
    seri: tuple
    sunt: tuple
    topoloji: str
    RL: float


def tasarla_lmatch(ZL: complex, Z0: float, f0: float) -> Tasarim:
    """ZL yukunu Z0'a uyumlayan iki elemanli L-match'i hesaplar.

    Kural: sunt eleman direnci BUYUK tarafa, seri eleman KUCUK tarafa gelir.
    Kompleks yukte yukun reaktansi seri kolda 'yutulur'.
    """
    if ZL.real <= 0:
        raise ValueError("Yukun direnc kismi R pozitif olmali (ZL = R + jX).")

    w0 = 2 * np.pi * f0
    RL, XL = ZL.real, ZL.imag

    if RL <= Z0:
        # Yuk kucuk: sunt eleman kaynakta, seri eleman yukte.
        Q = np.sqrt(Z0 / RL - 1.0)
        X_seri = Q * RL - XL      # seri kolun net reaktansi; yukun XL'ini yutar
        B_sunt = Q / Z0           # sunt kolun susseptansi
        topoloji = "sunt@kaynak -> seri@yuk"
    else:
        # Yuk buyuk: roller ters. Admittans (Y=1/Z) uzerinden coz.
        GL = RL / (RL**2 + XL**2)
        BL = -XL / (RL**2 + XL**2)
        Btot = np.sqrt(GL * (1.0 / Z0 - GL))
        B_sunt = Btot - BL
        X_seri = Btot * Z0 / GL
        Q = np.sqrt(RL / Z0 - 1.0)
        topoloji = "seri@kaynak -> sunt@yuk"

    # Isaretine gore elemani L ya da C olarak sec.
    seri = ('L', X_seri / w0) if X_seri >= 0 else ('C', -1.0 / (w0 * X_seri))
    sunt = ('C', B_sunt / w0) if B_sunt >= 0 else ('L', -1.0 / (w0 * B_sunt))
    return Tasarim(Q=float(Q), seri=seri, sunt=sunt, topoloji=topoloji, RL=RL)


def yuvarla_e12(tas: Tasarim) -> Tasarim:
    """Tasarimin L/C degerlerini en yakin E12'ye yuvarlanmis KOPYASINI dondurur."""
    def _yuv(el):
        t, v = el
        birim = 1e9 if t == 'L' else 1e12
        return (t, en_yakin_e12(v * birim) / birim)
    return Tasarim(Q=tas.Q, seri=_yuv(tas.seri), sunt=_yuv(tas.sunt),
                   topoloji=tas.topoloji, RL=tas.RL)


def bicim(el) -> str:
    t, v = el
    return f"{v*1e9:.2f} nH" if t == 'L' else f"{v*1e12:.2f} pF"


def kur_devre(media, tas: Tasarim, ZL: complex, Z0: float, isim: str) -> rf.Network:
    """Tasarimi scikit-rf Network'e cevirir (topolojiye gore dogru sirayla)."""
    def _seri(el):
        t, v = el
        return media.inductor(v) if t == 'L' else media.capacitor(v)

    def _sunt(el):
        t, v = el
        return media.shunt_inductor(v) if t == 'L' else media.shunt_capacitor(v)

    gamma_L = (ZL - Z0) / (ZL + Z0)
    load = media.load(gamma_L)
    if tas.RL <= Z0:
        net = _sunt(tas.sunt) ** _seri(tas.seri) ** load
    else:
        net = _seri(tas.seri) ** _sunt(tas.sunt) ** load
    net.name = isim
    return net


def s11_db_f0(net: rf.Network, f0: float) -> float:
    idx = int(np.argmin(np.abs(net.frequency.f - f0)))
    return 20 * np.log10(np.abs(net.s[idx, 0, 0]))


def dip_bilgi(net: rf.Network):
    """Egrinin en derin noktasini dondurur: (frekans_MHz, S11_dB)."""
    mag = 20 * np.log10(np.abs(net.s[:, 0, 0]))
    i = int(np.argmin(mag))
    return net.frequency.f[i] / 1e6, float(mag[i])


def parse_empedans(s: str) -> complex:
    try:
        return complex(s.replace(" ", ""))
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Gecersiz empedans '{s}'. Ornek: 40-30j, 15, 20+10j")


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="868 MHz L-match tasarim ve gorsellestirme araci.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--zl", type=parse_empedans, default=complex(40, -30),
                   metavar="R+Xj", help="Anten empedansi ZL (ornek: 40-30j, 15, 20+10j)")
    p.add_argument("--z0", type=float, default=50.0, help="Sistem empedansi [Ohm]")
    p.add_argument("--f0", type=float, default=868e6, help="Calisma frekansi [Hz]")
    p.add_argument("--fmin", type=float, default=None, help="Supurme alt frekans [Hz] (bos=0.8*f0)")
    p.add_argument("--fmax", type=float, default=None, help="Supurme ust frekans [Hz] (bos=1.2*f0)")
    p.add_argument("--points", type=int, default=701, help="Supurme nokta sayisi")
    p.add_argument("--lseri", type=float, default=None,
                   help="Seri bobini ELLE ayarla [nH] (tune deneyi; E12 uzerine yazar)")
    p.add_argument("--csunt", type=float, default=None,
                   help="Sont kondansatoru ELLE ayarla [pF] (tune deneyi; E12 uzerine yazar)")
    p.add_argument("--show", action="store_true", help="Grafik pencerelerini ac (interaktif)")
    p.add_argument("--no-save", action="store_true", help="PNG kaydetme")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    ZL, Z0, f0 = args.zl, args.z0, args.f0
    fmin = args.fmin if args.fmin else 0.8 * f0
    fmax = args.fmax if args.fmax else 1.2 * f0

    # 1) Tasarla + E12'ye yuvarla
    tas = tasarla_lmatch(ZL, Z0, f0)
    tas_e = yuvarla_e12(tas)

    # Egriler: ideal + E12 (+ istege bagli ELLE ayar 'manuel')
    egriler = [("ideal", tas), ("E12", tas_e)]
    if args.lseri is not None or args.csunt is not None:
        st, sv = tas_e.seri   # tune, E12 degerleri uzerinden baslar
        ut, uv = tas_e.sunt
        if args.lseri is not None:
            sv = args.lseri * 1e-9
        if args.csunt is not None:
            uv = args.csunt * 1e-12
        egriler.append(("manuel", Tasarim(Q=tas.Q, seri=(st, sv), sunt=(ut, uv),
                                          topoloji=tas.topoloji, RL=tas.RL)))

    # 2) scikit-rf ortami ve devreler
    freq = rf.Frequency(fmin / 1e6, fmax / 1e6, args.points, unit="mhz")
    media = DefinedGammaZ0(frequency=freq, z0=Z0)
    netler = [(isim, kur_devre(media, t, ZL, Z0, isim)) for isim, t in egriler]

    # 3) Konsol ozeti
    xi = ZL.imag
    print("=" * 68)
    print("  L-MATCH TASARIMI")
    print(f"  Yuk ZL = {ZL.real:.1f} {'+' if xi >= 0 else '-'} j{abs(xi):.1f} Ohm"
          f"    Z0 = {Z0:.0f} Ohm    f0 = {f0/1e6:.1f} MHz")
    print(f"  Topoloji : {tas.topoloji}    Q = {tas.Q:.3f}")
    print("-" * 68)
    print(f"  {'egri':8s}{'seri':>11s}{'sunt':>11s}{'S11(f0)':>12s}{'dip':>18s}")
    for (isim, t), (_, net) in zip(egriler, netler):
        fdip, mdip = dip_bilgi(net)
        print(f"  {isim:8s}{bicim(t.seri):>11s}{bicim(t.sunt):>11s}"
              f"{s11_db_f0(net, f0):>9.1f} dB{mdip:>8.1f} dB@{fdip:6.1f}MHz")
    print("=" * 68)

    # 4) Grafikler
    etiket = {isim: t for isim, t in egriler}
    fig_s11 = plt.figure()
    for isim, net in netler:
        t = etiket[isim]
        net.plot_s_db(m=0, n=0, label=f"{isim} ({bicim(t.seri)}/{bicim(t.sunt)})")
    plt.axvline(f0, color="k", ls="--", lw=0.8)
    plt.title("Donus kaybi S11")
    plt.grid(True)
    plt.legend()

    fig_smith = plt.figure()
    for isim, net in netler:
        net.plot_s_smith(m=0, n=0, draw_labels=(isim == "ideal"), label=isim)
    plt.title("Smith abagi")
    plt.legend()

    if not args.no_save:
        outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
        os.makedirs(outdir, exist_ok=True)
        fig_s11.savefig(os.path.join(outdir, "s11_db.png"), dpi=130, bbox_inches="tight")
        fig_smith.savefig(os.path.join(outdir, "smith.png"), dpi=130, bbox_inches="tight")
        print(f"Grafikler kaydedildi: {outdir}/s11_db.png , {outdir}/smith.png")

    if args.show:
        plt.show()
    return 0


if __name__ == "__main__":
    sys.exit(main())
