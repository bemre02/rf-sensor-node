# sim/ — RF Simülasyonu (ücretsiz, alet gerektirmez)

RF ön-ucunu **ekranda** tasarlayıp doğruladığımız yer. Alet almadan öğrenmenin ana yolu.

## Araçlar
- **scikit-rf** (Python) — Smith abağı, matching, S-parametre kaskadı, filtre. Giriş noktası.
- **QucsStudio** (ücretsiz, Windows) — RF devre + küçük EM çözücü (filtre/matching).
- **SonnetLite** (ücretsiz, sınırlı planar EM) — microstrip filtre/anten alan simülasyonu.
- **openEMS** (ücretsiz FDTD) — anten/3B (eğrisi dik ama güçlü).
- **KiCad** hat/empedans hesaplayıcı — 50 Ω microstrip genişliği.

## Kurulum (scikit-rf)
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python matching_lmatch.py            # PNG uret (sim/out/)
python matching_lmatch.py --show     # grafik penceresi ac (interaktif)
```

## Kullanım (komut satırı)
Dosyayı düzenlemeden parametre verebilirsin:
```bash
python matching_lmatch.py --zl 40-30j        # kompleks anten empedansı
python matching_lmatch.py --zl 15            # dirençsel yük
python matching_lmatch.py --zl 80 --show     # RL>Z0 (topoloji ters) + pencere
python matching_lmatch.py --f0 433e6         # farklı frekans (433 MHz)
python matching_lmatch.py --lseri 9.1 --csunt 1.8   # elle ayar (tune) deneyi
python matching_lmatch.py --q 40             # kayıplı bobin modeli (Q=40) + antene ulaşan güç
python matching_lmatch.py --help             # tüm seçenekler
```
Öne çıkan seçenekler: `--zl R+Xj`, `--z0`, `--f0`, `--fmin/--fmax/--points`, `--lseri/--csunt` (elle ayar), `--q` (bobin kaybı), `--show`, `--no-save`.
Konsol her eğri için S11(f0), dip yeri/derinliği ve **antene ulaşan gücü** (verim) yazar.

## Dosyalar
- `matching_lmatch.py` — L-match tasarım/görselleştirme aracı: (kompleks) yük empedansını
  50 Ω'a uyumlar, topolojiyi otomatik seçer, ideal↔E12 farkını S11 + Smith'te kıyaslar.
  Sıradaki: eleman Q/SRF (kayıplı model / `.s2p`), high-pass L-match, Pi/T varyantları.
- `requirements.txt` — bağımlılıklar.

## Öğrenme köprüsü
CAN/USB'de empedans uyumsuzluğu → yansıma sezgin var (120 Ω sonlandırma). RF matching, bunun
frekansa bağlı (L/C ile) genellemesi. Smith abağı = "empedansı 50 Ω'a nasıl çekerim" haritası.
