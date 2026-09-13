# RF Sensor Node — Session Kickoff (Aktarım Brief'i)

> Bu dosyayı yeni bir Cursor session'ının ilk mesajında referans ver; bağlamı sıfırdan
> anlatmana gerek kalmaz. (DEVAM_PROMPT tarzı handoff.)

## Kim
2. sınıf İTÜ Elektronik ve Haberleşme Müh. öğrencisi (Burak Emre). İleri seviye STM32
firmware (G4/H7/F1; bare-metal + FreeRTOS + H745 dual-core, HSEM/SRAM4) ve Altium PCB
deneyimi var: CAN/USB için empedans-kontrollü diferansiyel routing yapıyor; GPS26'da
50 Ω tek-uçlu anten izi + stackup/empedans ayarlarını Altium'da yaptı (ama analitik
derinlikte değil). SPI ile onlarca sensör sürdü. Python biliyor (PyQt6 log viewer).
**Eksik/öğrenmek istediği: RF TASARIMI** (matching, Smith, filtre, anten, 50 Ω hat).

## Öğrenme tarzı (önemli)
- Simülasyon/Python gibi işleri AI ile **birlikte** yapmayı seviyor: mimariyi ve amacı
  anlatır, üzerine iterasyon yapar (UI projelerini böyle geliştirdi). Adım adım, elle
  tutulur ilerlemek ister; salt teori yığını değil, **deneyim/pratik + biraz ileri teori**.
- Bütçe: kart çizip sipariş/dizim OK; **ekstra ölçüm aleti alınmayacak** (NanoVNA/TinySA yok).
  Doğrulama simülasyon + çipin RSSI/SNR'ı + (sonradan) ITÜ lab VNA'sı ile.

## Proje
İki farklı MCU'nun, **kendi tasarladığı RF linki** üzerinden konuştuğu sıfırdan sistem:
- **Node:** STM32 + SX1262 (RF ön-ucu ELLE tasarlanacak) + sensör
- **Base:** ESP32-S3 + SX1262 + Wi-Fi köprü (telefona/PC'ye)
- RF sistemin kalbi; radyo teknolojisi (LoRa/sub-GHz) sadece taşıyıcı.

## Kilitli kararlar
- Transceiver: **Semtech SX1262**; band **868 MHz** (TR lisanssız SRD, 25 mW e.r.p.)
- Simülasyon-öncelikli. Sim giriş noktası: **scikit-rf** (Python). Yanına QucsStudio,
  SonnetLite (ücretsiz planar EM), openEMS (ücretsiz FDTD), KiCad hat/empedans hesaplayıcı.
- Doğrulama: (1) ücretsiz sim, (2) kart dizilince RSSI/SNR + menzil testi, (3) ITÜ lab VNA.

## Öğrenme sırası (Faz A)
1. **Matching + Smith** — `sim/matching_lmatch.py` (ilk somut iş; CAN sonlandırma/GPS26
   sezgisinden köprü kur). Önce dirençsel yük, sonra kompleks anten empedansı (TODO).
2. **50 Ω microstrip** — seçilen stackup'tan iz genişliği (GPS26'da elle yaptığını hesapla).
3. **Harmonik filtre** — SX1262 çıkışında 2. ve yüksek mertebe harmonik bastırma (S21 sim).
4. **Anten** — PCB iz anteni (en çok öğretir) veya chip anten + referans; SonnetLite/openEMS.
5. **SX1262 RF referans tasarımı** — Semtech app-note + Johanson IPD (0900FM15x0039) vs ayrık
   L/C; her komponenti anla. 50 Ω hat, GND via yerleşimi, kristal etrafı termal void, TCXO.
6. → **Altium PCB** → sipariş/dizim → **RSSI/SNR fonksiyonel doğrulama**.

## İLK GÖREV
`sim/` içinde scikit-rf ile 868 MHz'de bir L-matching ağı tasarla, Smith abağı + S11 (dönüş
kaybı) çiz. `matching_lmatch.py` başlangıç noktasıdır — çalıştır, anla, sonra kompleks anten
empedansı ve L/high-pass varyantları için genişlet. Ardından RF_DESIGN.md'yi doldurmaya başla.

## Referans notlar
- SX1262: sub-GHz 150–960 MHz, LoRa (0.018–62.5 kbps) + GFSK (≤300 kbps), +22 dBm, SPI.
- TR band: 433.05–434.79 MHz (10 mW, ≤%10 duty) veya 863–868 MHz (25 mW). 868 seçildi.
- RF ön-uç = empedans matching + 2. harmonik filtre + yüksek mertebe filtre + RF switch → anten.
- Elektriksel kısa iz kuralı: iz < ~λ/10 ise uyumsuzluk toleranslı. 868 MHz FR4'te λ≈20 cm.
