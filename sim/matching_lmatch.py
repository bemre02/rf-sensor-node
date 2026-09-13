"""
İLK GÖREV — 868 MHz'de L-match tasarımı + Smith abağı + S11 (dönüş kaybı).

Amaç: Empedans uyumlamayı (matching) "ekranda" görmek. CAN/USB'deki empedans-uyumsuzluğu
sezgisinin (120 Ohm sonlandirma -> yansima yok) RF'teki karsiligi budur: kaynagi (50 Ohm)
yuke (anten) uydurup yansimayi (S11) minimuma cekmek.

Bu betik BASLANGIC noktasidir. Once dirensel bir yuk (temiz ders kitabi ornegi) uydurulur.
Sonraki adimlar (TODO): kompleks anten empedansi, high-pass L-match, Pi/T varyantlari.

Calistir:  pip install -r requirements.txt  &&  python matching_lmatch.py
Ciktilar sim/out/ altina PNG olarak kaydedilir.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless: ekran olmadan da PNG uretir
import matplotlib.pyplot as plt
import skrf as rf
from skrf.media import DefinedGammaZ0

# ----------------------------------------------------------------------------
# 1) Hedef parametreler
# ----------------------------------------------------------------------------
F0 = 868e6           # calisma frekansi [Hz]
Z0 = 50.0            # sistem empedansi [Ohm]
RL = 15.0            # ornek anten direnci [Ohm] (RL < Z0). TODO: gercek/kompleks ZL kullan.

w0 = 2 * np.pi * F0

# ----------------------------------------------------------------------------
# 2) Alcak-geciren L-match (50 Ohm -> RL, RL < Z0)
#    Kaynak (yuksek-Z) tarafinda SUNT eleman, yuk (dusuk-Z) tarafinda SERI eleman.
#    Sunt C + seri L  ->  ayni zamanda biraz harmonik filtreleme saglar.
# ----------------------------------------------------------------------------
Q = np.sqrt(Z0 / RL - 1.0)
Xs = Q * RL          # seri reaktans (yuk tarafi)
Xp = Z0 / Q          # sunt reaktans (kaynak tarafi)

Ls = Xs / w0                 # seri indüktör [H]
Cp = 1.0 / (w0 * Xp)         # sunt kondansator [F]

print("=" * 56)
print(f"L-match  |  f0={F0/1e6:.1f} MHz  Z0={Z0:.0f}Ω  RL={RL:.0f}Ω")
print("-" * 56)
print(f"Q  = {Q:.3f}")
print(f"Seri  L (yuk tarafi)   = {Ls*1e9:6.2f} nH   (Xs={Xs:5.1f}Ω)")
print(f"Sunt  C (kaynak tarafi)= {Cp*1e12:6.2f} pF   (Xp={Xp:5.1f}Ω)")
print("=" * 56)

# ----------------------------------------------------------------------------
# 3) scikit-rf ile devreyi kur ve dogrula
# ----------------------------------------------------------------------------
freq = rf.Frequency(700, 1050, 701, unit="mhz")
media = DefinedGammaZ0(frequency=freq, z0=Z0)

# Dirensel yuk -> yansima katsayisi (Z0'a gore)
gamma_L = (RL - Z0) / (RL + Z0)
load = media.load(gamma_L)

# Kaynaktan yuke: SUNT C  ->  SERI L  ->  YUK
network = media.shunt_capacitor(Cp) ** media.inductor(Ls) ** load
network.name = "L-match + RL"

# f0'da donus kaybi
s11_f0_db = 20 * np.log10(np.abs(network[f"{F0/1e6:.0f}mhz"].s[0, 0, 0]))
print(f"f0'da |S11| = {s11_f0_db:6.2f} dB  (ne kadar negatif, o kadar iyi uyum)")
print("Not: dip tam f0'da mi? Degilse L/C degerlerini/round'u gozden gecir.\n")

# ----------------------------------------------------------------------------
# 4) Grafikler: S11(dB) ve Smith
# ----------------------------------------------------------------------------
outdir = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(outdir, exist_ok=True)

plt.figure()
network.plot_s_db(m=0, n=0)
plt.axvline(F0, color="k", ls="--", lw=0.8)
plt.title("Donus kaybi S11 (dB)")
plt.grid(True)
plt.savefig(os.path.join(outdir, "s11_db.png"), dpi=130, bbox_inches="tight")

plt.figure()
network.plot_s_smith(m=0, n=0, draw_labels=True)
plt.title("Smith abagi (girise bakan empedans)")
plt.savefig(os.path.join(outdir, "smith.png"), dpi=130, bbox_inches="tight")

print(f"Grafikler kaydedildi: {outdir}/s11_db.png , {outdir}/smith.png")

# ----------------------------------------------------------------------------
# TODO (yeni session'da AI ile birlikte):
#  - RL yerine KOMPLEKS anten empedansi ZL = R + jX kullan (once L'nin reaktansini yut).
#  - Alcak-geciren yerine YUKSEK-geciren L-match (seri C + sunt L) varyantini ekle ve kiyasla.
#  - Pi ve T eslesme aglari (ekstra serbestlik derecesi, bant genisligi kontrolu).
#  - Komponentleri E12/E24 standart degerlere yuvarla, tekrar simule et (gercekci).
#  - Kondansator/indüktör self-rezonans (SRF) ve Q etkisini modele kat.
#  - Sonuclari docs/RF_DESIGN.md'ye isle.
# ----------------------------------------------------------------------------
