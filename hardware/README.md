# hardware/ — Altium tasarımları

Node ve Base kartlarının Altium projeleri. RF ön-ucu (matching + filtre + anten) burada
somutlaşır; hesaplar `docs/RF_DESIGN.md`, simülasyon `sim/` altında.

## Kartlar
- `node/` — STM32 + SX1262 + sensör + RF ön-uç + anten.
- `base/` — ESP32-S3 + SX1262 + RF ön-uç + anten (+ USB, Wi-Fi anteni ESP modülünde).

## Tasarım notları
- SX1262 RF ön-uç: empedans matching + 2. harmonik + yüksek mertebe filtre + (RF switch) → anten.
  - Kolay yol: Johanson IPD **0900FM15x0039** (tek 0805). Öğrenme yolu: ayrık L/C.
- Tüm RF hatları **50 Ω** tek-uçlu microstrip (GPS26'daki 50 Ω iz deneyimin + artık analitik).
- Stackup: SX1261 ref 2L; **SX1262 (+22 dBm) ref 4L** (termal + RF referans düzlemi). Karar ver.
- Kristal etrafı termal void; +22 dBm uzun paket için TCXO düşün.
- GND via yerleşimi harmonik filtrede kritik (app-note'a uy).
- CAN/USB'deki empedans-kontrollü routing disiplinini RF'e taşı; Altium empedans profili kullan.

## Üretim
- Gerber + pick&place + BOM `hardware/<kart>/outputs/` altına (git'e outputs eklenmeyecek — .gitignore).
