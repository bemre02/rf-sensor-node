# Link Protokolü (Node → Base)

RF link üzerinden gönderilen paket formatı. RF öğrenme projesinde payload küçük tutulur;
asıl olay linkin kendisidir. Format sonradan genişletilebilir. (⚠ = açık soru / karara bağlı.)

## Fiziksel katman
- Modülasyon: **LoRa** (başlangıç; sağlam, RSSI/SNR verir) — alternatif GFSK (daha yüksek hız).
- Band/kanal: 868 MHz, ⚠ tam frekans + SF/BW/CR seçilecek (menzil vs hız dengesi).
- Duty cycle: TR SRD kuralına uy (863–868 MHz genel: 25 mW e.r.p.).

## Paket yapısı (öneri, v0)

| Ofset (bayt) | Alan | Tip | Açıklama |
|---|---|---|---|
| 0 | `node_id` | u8 | Düğüm kimliği |
| 1 | `seq` | u8 | Artan sıra sayacı (paket kaybı tespiti) |
| 2 | `msg_type` | u8 | 0=telemetri, 1=heartbeat, ⚠ genişletilebilir |
| 3..N | `payload` | ... | Sensör verisi (⚠ hangi sensör? IMU/sıcaklık/pot) |
| N+1 | `crc8` | u8 | CRC-8 (poly 0x07) — senin BMS UI'daki gibi |

- LoRa'nın kendi CRC'si var; yine de uçtan uca `crc8` eklenmesi (senin alışkanlığın) önerilir.
- Base tarafı her pakette RSSI + SNR'ı loglar (link kalitesi metriği, alet gerektirmez).

## Base → PC/telefon (Wi-Fi köprüsü)
- ESP32-S3 soft-AP veya STA; ⚠ JSON over WebSocket / UDP / basit HTTP?
- Alanlar: node_id, seq, payload çözümü, **rssi, snr**, paket kayıp oranı.

## Açık sorular
- ⚠ Sensör seçimi (öğrenme için basit; takıma fayda için anlamlı bir şey?).
- ⚠ SF/BW/CR (spreading factor / bandwidth / coding rate) — menzil/hız/duty dengesi.
- ⚠ İki yönlü mü (base→node komut) yoksa tek yön telemetri mi?
