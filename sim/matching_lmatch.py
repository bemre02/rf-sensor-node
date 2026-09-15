"""
868 MHz L-match tasarimi: KOMPLEKS yuk + otomatik E12 yuvarlama + Smith/S11.

Bu betik, ilk surumun genisletilmis halidir. Onceki surum yalnizca dirensel bir
yuku (RL=15 Ohm) uyumluyordu. Bu surum:
  - KOMPLEKS anten empedansini (ZL = R + jX) uyumlar; yukun reaktansini seri
    elemanda "yutar",
  - RL<Z0 ve RL>Z0 durumlari icin dogru L-match topolojisini otomatik secer,
  - ideal L/C degerlerini en yakin E12 standart degerine yuvarlar ve ideal ile
    E12'yi ayni grafikte kiyaslar (gerceklikte dip siglasir ve kayar).

CAN sezgisi koprusu: uyumsuz yuk -> yansima (S11). Matching, yansimayi tek bir
frekansta (868 MHz) L/C ile sifira cekmektir. Smith abagi bu donusumun haritasi.

Calistir (PNG uret):        python matching_lmatch.py
Calistir (pencere ac):      python matching_lmatch.py --show
Ciktilar her durumda sim/out/ altina PNG olarak da kaydedilir.
"""

import os
import sys
import numpy as np
import matplotlib

# Yerelde pencere acip interaktif gormek icin:  python matching_lmatch.py --show
# (Smith uzerinde gezinme/zoom yapabilirsin). Bayrak yoksa headless "Agg" backend
# ile SADECE PNG uretir (bulut/CI ortaminda ekran olmadigi icin varsayilan budur).
GOSTER = ("--show" in sys.argv) or (os.environ.get("SIM_SHOW") == "1")
if not GOSTER:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
import skrf as rf
from skrf.media import DefinedGammaZ0

# ----------------------------------------------------------------------------
# 1) Hedef parametreler
# ----------------------------------------------------------------------------
F0 = 868e6            # calisma frekansi [Hz]
Z0 = 50.0             # sistem empedansi [Ohm]
# Yuk artik KOMPLEKS olabilir: ZL = R + jX. Ornek: kucuk bir anten ~ 40 - j30 Ohm
# (dirensel + kapasitif). Saf dirensel ders ornegi icin: ZL = 15 + 0j.
ZL = 40.0 - 30.0j

w0 = 2 * np.pi * F0

# ----------------------------------------------------------------------------
# 2) E12 standart deger serisi ve "en yakin" secim
#    Gercek dunyada 4.201 nH satin alinamaz; en yakin standart degere yuvarlanir.
# ----------------------------------------------------------------------------
E12 = np.array([1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2])

def en_yakin_e12(x):
    """x'e en yakin E12 degerini dondurur (tum decade'ler taranir)."""
    dec = 10.0 ** np.floor(np.log10(x))
    aday = np.concatenate([E12 * dec / 10, E12 * dec, E12 * dec * 10])
    return float(aday[np.argmin(np.abs(aday - x))])

# ----------------------------------------------------------------------------
# 3) Genel L-match tasarimi (kompleks yuk + topoloji secimi)
#    Kural: sunt eleman DIRENCI BUYUK olan tarafa, seri eleman KUCUK olan tarafa.
# ----------------------------------------------------------------------------
def tasarla_lmatch(ZL, Z0):
    """ZL yukunu Z0'a uyumlayan iki elemanli L-match'i hesaplar.
    Donen 'seri'/'sunt': ('L'|'C', deger) ciftleri. Isaret pozitifse eleman
    bir indukturdur (L), negatifse kondansatordur (C)."""
    RL, XL = ZL.real, ZL.imag
    if RL <= Z0:
        # Yuk kucuk (RL<=Z0): sunt eleman kaynakta, seri eleman yukte.
        Q = np.sqrt(Z0 / RL - 1.0)
        X_seri = Q * RL - XL      # seri kolun net reaktansi; yukun XL'ini yutar
        B_sunt = Q / Z0           # sunt kolun susseptansi (+ -> kondansator)
        topoloji = "sunt@kaynak -> seri@yuk"
    else:
        # Yuk buyuk (RL>Z0): roller ters. Admittans uzerinden coz.
        GL = RL / (RL**2 + XL**2)
        BL = -XL / (RL**2 + XL**2)
        Btot = np.sqrt(GL * (1.0 / Z0 - GL))
        B_sunt = Btot - BL
        X_seri = Btot * Z0 / GL
        Q = np.sqrt(RL / Z0 - 1.0)
        topoloji = "seri@kaynak -> sunt@yuk"

    seri = ('L', X_seri / w0) if X_seri >= 0 else ('C', -1.0 / (w0 * X_seri))
    sunt = ('C', B_sunt / w0) if B_sunt >= 0 else ('L', -1.0 / (w0 * B_sunt))
    return dict(Q=Q, seri=seri, sunt=sunt, topoloji=topoloji, RL=RL)

# ----------------------------------------------------------------------------
# 4) scikit-rf devre kurucu
# ----------------------------------------------------------------------------
freq = rf.Frequency(700, 1050, 701, unit="mhz")
media = DefinedGammaZ0(frequency=freq, z0=Z0)

def _seri(t, v):
    return media.inductor(v) if t == 'L' else media.capacitor(v)

def _sunt(t, v):
    return media.shunt_inductor(v) if t == 'L' else media.shunt_capacitor(v)

def kur_devre(tas, ZL, isim):
    """Tasarimi bir scikit-rf Network'e cevirir (dogru eleman sirasiyla)."""
    gamma_L = (ZL - Z0) / (ZL + Z0)     # yukun yansima katsayisi
    load = media.load(gamma_L)
    if tas['RL'] <= Z0:
        net = _sunt(*tas['sunt']) ** _seri(*tas['seri']) ** load
    else:
        net = _seri(*tas['seri']) ** _sunt(*tas['sunt']) ** load
    net.name = isim
    return net

def bicim(t, v):
    return f"{v*1e9:.2f} nH" if t == 'L' else f"{v*1e12:.2f} pF"

def s11_f0_db(net):
    return 20 * np.log10(np.abs(net[f"{F0/1e6:.0f}mhz"].s[0, 0, 0]))

# ----------------------------------------------------------------------------
# 5) Tasarla -> E12'ye yuvarla -> yazdir
# ----------------------------------------------------------------------------
tas = tasarla_lmatch(ZL, Z0)
st, sv = tas['seri']
ut, uv = tas['sunt']

# Ideal degerlerin E12'ye yuvarlanmis kopyasi
sv_e = en_yakin_e12(sv * 1e9) * 1e-9 if st == 'L' else en_yakin_e12(sv * 1e12) * 1e-12
uv_e = en_yakin_e12(uv * 1e9) * 1e-9 if ut == 'L' else en_yakin_e12(uv * 1e12) * 1e-12
tas_e = dict(tas, seri=(st, sv_e), sunt=(ut, uv_e))

net_ideal = kur_devre(tas, ZL, "ideal")
net_e12 = kur_devre(tas_e, ZL, "E12")

print("=" * 60)
print(f"Yuk ZL = {ZL.real:.0f} {'+' if ZL.imag >= 0 else '-'} j{abs(ZL.imag):.0f} Ohm"
      f"   f0={F0/1e6:.0f} MHz   Z0={Z0:.0f} Ohm")
print(f"Topoloji: {tas['topoloji']}   Q={tas['Q']:.3f}")
print("-" * 60)
print(f"IDEAL : seri {st}={bicim(st, sv)}   sunt {ut}={bicim(ut, uv)}")
print(f"E12   : seri {st}={bicim(st, sv_e)}   sunt {ut}={bicim(ut, uv_e)}")
print("-" * 60)
print(f"f0'da S11:  ideal={s11_f0_db(net_ideal):7.1f} dB   E12={s11_f0_db(net_e12):7.1f} dB")
print("Not: ideal cok derin (idealize); E12 gercekci -> siglasir ve biraz kayar.")
print("=" * 60)

# ----------------------------------------------------------------------------
# 6) Grafikler: S11(dB) ve Smith (ideal vs E12)
# ----------------------------------------------------------------------------
outdir = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(outdir, exist_ok=True)

plt.figure()
net_ideal.plot_s_db(m=0, n=0, label=f"ideal ({bicim(st, sv)} / {bicim(ut, uv)})")
net_e12.plot_s_db(m=0, n=0, label=f"E12 ({bicim(st, sv_e)} / {bicim(ut, uv_e)})")
plt.axvline(F0, color="k", ls="--", lw=0.8)
plt.title("Donus kaybi S11 - ideal vs E12")
plt.grid(True)
plt.legend()
plt.savefig(os.path.join(outdir, "s11_db.png"), dpi=130, bbox_inches="tight")

plt.figure()
net_ideal.plot_s_smith(m=0, n=0, draw_labels=True, label="ideal")
net_e12.plot_s_smith(m=0, n=0, label="E12")
plt.title("Smith abagi - ideal vs E12")
plt.legend()
plt.savefig(os.path.join(outdir, "smith.png"), dpi=130, bbox_inches="tight")

print(f"Grafikler kaydedildi: {outdir}/s11_db.png , {outdir}/smith.png")

# Yerel interaktif mod: pencereleri ac (bulutta --show verilmez, bu satir atlanir).
if GOSTER:
    plt.show()

# ----------------------------------------------------------------------------
# TODO (sonraki oturumlar):
#  - Eleman Q'su ve self-rezonans (SRF): ideal L/C yerine kayipli model ya da
#    ureticinin .s2p S-parametre dosyasi (Murata/Coilcraft) ile gercekci sim.
#  - Yuksek-geciren L-match (seri C + sunt L) ve Pi/T aglari; bant genisligi kiyasi.
#  - Sonuclari docs/RF_DESIGN.md'ye isle (komponent secimi + gerekce).
# ----------------------------------------------------------------------------
