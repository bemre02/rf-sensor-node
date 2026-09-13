# rf-sensor-node

Sıfırdan tasarlanan, **RF tasarımını öğrenmeye** odaklı bir kablosuz sensör düğümü.
İki farklı mikrokontrolcü, **kendi tasarladığım RF linki** üzerinden haberleşir.

> Bu proje bir "telemetri ürünü" değil, bir **RF tasarım egzersizidir**.
> Radyo teknolojisi (sub-GHz / LoRa) yalnızca bir taşıyıcıdır; asıl amaç RF ön-ucunu
> (matching + harmonik filtre + anten + 50 Ω hat) kendim tasarlayıp doğrulamaktır.

---

## Amaç

RF (radyo frekans) tasarımını **pratikle** öğrenmek: iletim hatları, empedans uyumlama
(matching), Smith abağı, harmonik filtreleme, anten ve 50 Ω tek-uçlu microstrip. Mevcut
gömülü + PCB (STM32, Altium, CAN/USB empedans-kontrollü diferansiyel routing) birikiminin
üzerine, eksik olan **analog/RF kasını** eklemek.

## Mimari

```
   ┌─────────────────────────┐         RF link (868 MHz)         ┌─────────────────────────┐
   │  NODE (uç birim)         │      kendi tasarladığım          │  BASE (baz istasyonu)    │
   │  STM32 + SX1262          │  ~~~~~~~ RF ön-uç ~~~~~~~~>       │  ESP32-S3 + SX1262       │
   │  + sensör                │      (matching+filtre+anten)     │  + Wi-Fi köprü → PC/tel. │
   └─────────────────────────┘                                  └─────────────────────────┘
        SPI ile SX1262 sürülür                                       SPI + Wi-Fi/soft-AP
```

İki **farklı** MCU (STM32 ↔ ESP32-S3), aralarındaki **RF hattı üzerinden** konuşur.
RF, sistemin kalbidir.

## Kilitli kararlar

| Konu | Karar |
|---|---|
| Transceiver | Semtech **SX1262** (sub-GHz, LoRa + GFSK, +22 dBm) |
| Band | **868 MHz** (TR'de lisanssız SRD, 25 mW e.r.p.) |
| Node MCU | STM32 (tanıdık; SPI ile SX1262) |
| Base MCU | **ESP32-S3** (yeni MCU + Wi-Fi köprüsü) |
| Yaklaşım | **Simülasyon-öncelikli, alet-minimum** |
| Doğrulama | (1) ücretsiz sim, (2) çipin RSSI/SNR'ı + menzil testi, (3) sonra ITÜ lab VNA'sı |
| Sim giriş | **scikit-rf** (Python) → QucsStudio / SonnetLite / openEMS |

> Not: VNA/spektrum analizörü **satın alınmayacak**. Gerekince ITÜ EHB RF/mikrodalga
> laboratuvarının VNA'sı kullanılacak.

## Repo yapısı

```
rf-sensor-node/
├── hardware/            Altium projeleri (node + base) + çıktılar
├── firmware/
│   ├── node-stm32/      STM32 + SX1262 SPI sürücü + uygulama
│   └── base-esp32/      ESP32-S3 + SX1262 + Wi-Fi köprü (ESP-IDF)
├── sim/                 scikit-rf / QucsStudio çalışmaları (matching, filtre, anten)
├── docs/
│   ├── SESSION_KICKOFF.md   Yeni session için hazır aktarım brief'i
│   ├── RF_DESIGN.md         RF tasarım defteri (hesaplar + ölçümler)
│   ├── LINK_PROTOCOL.md     Paket formatı (CRC, sequence)
│   └── LINK_BUDGET.md       Menzil/hassasiyet hesabı
└── README.md
```

## Yol haritası (aşamalar)

- [ ] **Faz A — RF temelleri (sim, ücretsiz):** matching + Smith (`sim/`), 50 Ω microstrip,
      harmonik filtre (S21), anten. Her kavram bir PCB kararına bağlanır.
- [ ] **Faz B — PCB tasarımı (Altium):** SX1262 + RF ön-uç + anten (node & base). Sipariş + dizim.
- [ ] **Faz C — Firmware:** STM32 SX1262 sürücüsü, ESP32-S3 köprüsü, link protokolü.
- [ ] **Faz D — Fonksiyonel doğrulama:** RSSI/SNR okuma, menzil testi, anten/matching varyant kıyası.
- [ ] **Faz E (opsiyonel):** sensör/kontrol katmanı, ileride ITÜ lab VNA ile S11/S21.

## Nasıl devam edilir

Yeni bir Cursor session'ında **ilk iş `docs/DEVIR_TESLIM_PROMPT.md`'yi baştan sona oku** —
kullanıcının kim olduğunu, birikimini, hedefini ve projeyi eksiksiz anlatır (yeni ortam eski
repolara erişemez, tüm bağlam bu dosyadadır). Kısa özet için `docs/SESSION_KICKOFF.md`.
İlk somut iş: `sim/matching_lmatch.py` çalıştırıp Smith abağını görmek ve üzerine inşa etmek.

---
*Bu iskelet, planlama oturumunda hazırlandı. Kararlar `docs/SESSION_KICKOFF.md`'de özetlidir.*
