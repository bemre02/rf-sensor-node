# firmware/base-esp32

Baz istasyonu firmware: **ESP32-S3 + SX1262** (SPI) → RF alır, **Wi-Fi** ile PC/telefona köprüler.

## Plan (yeni MCU öğrenme fırsatı)
- Framework: **ESP-IDF** (Arduino değil — doğrudan IDF ile FreeRTOS/ağ öğren).
- SX1262 sürücüsü: node ile aynı komut seti (ortak bir sürücü paylaşmayı düşün).
- Wi-Fi: soft-AP veya STA; alınan paketleri (+RSSI/SNR + kayıp oranı) yayınla.
  - Taşıma seçeneği (⚠ karar): JSON over WebSocket / UDP / basit HTTP sayfası.
- Basit web arayüzü (AI ile birlikte yapılabilir — UI projelerindeki tarzınla).

## Yapılacaklar
- [ ] ESP-IDF kurulum + boş proje derleme (yeni ekosistem).
- [ ] SX1262 RX + getRSSI/getSNR.
- [ ] Wi-Fi köprü + canlı veri (rssi, snr, seq, kayıp %).
- [ ] Node ↔ Base uçtan uca link testi (menzil, RSSI kıyası).
