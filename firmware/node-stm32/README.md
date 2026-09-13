# firmware/node-stm32

Uç birim firmware: **STM32 + SX1262** (SPI) + sensör → RF ile veri gönderir.

## Plan
- MCU: STM32 (tanıdık; G4/G0 sınıfı yeterli). STM32CubeIDE veya CMake+arm-none-eabi.
- SX1262 sürücüsü: SPI + BUSY/DIO1 hat yönetimi, komut seti (SetPacketType=LoRa,
  SetRfFrequency=868M, SetTxParams, SetModulationParams SF/BW/CR, SetPacketParams, TX/RX).
- Uygulama: sensör oku → `docs/LINK_PROTOCOL.md`'deki paketi kur (crc8) → TX. Sequence sayacı.
- Düşük güç opsiyonel (SX1262 sleep + STM32 STOP) — LV_BMS26'daki güç yönetimi deneyimin işe yarar.

## Yapılacaklar
- [ ] Pin haritası (SPI, NRESET, BUSY, DIO1, ANT switch varsa).
- [ ] SX1262 minimal sürücü (init + TX + RX + getRSSI/getSNR).
- [ ] Paketleme + crc8 (BMS UI'daki CRC-8/0x07 ile aynı).
- [ ] Bench test modu (gerçek sensör olmadan sahte veri — Telemetry26'daki gibi).

> RF ön-ucu bu firmware'in konusu değil (o Altium/`hardware/` ve `sim/`'de). Buradaki iş
> çipi doğru sürüp linki kurmak ve link kalitesini (RSSI/SNR) raporlamak.
