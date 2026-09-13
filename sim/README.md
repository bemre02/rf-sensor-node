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
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python matching_lmatch.py
```

## Dosyalar
- `matching_lmatch.py` — İLK GÖREV: 868 MHz'de L-match tasarımı + Smith + S11. Başlangıç
  noktası; üzerine kompleks anten empedansı, high-pass L-match, Pi/T varyantları eklenecek.
- `requirements.txt` — bağımlılıklar.

## Öğrenme köprüsü
CAN/USB'de empedans uyumsuzluğu → yansıma sezgin var (120 Ω sonlandırma). RF matching, bunun
frekansa bağlı (L/C ile) genellemesi. Smith abağı = "empedansı 50 Ω'a nasıl çekerim" haritası.
