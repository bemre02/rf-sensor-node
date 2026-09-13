# Link Budget (Menzil / Hassasiyet Hesabı)

Bir RF linkinin "kapanıp kapanmadığını" alet olmadan kağıt üzerinde tahmin etme aracı.
EHB307 (Haberleşme I) ile birebir örtüşür. Değerleri doldurup marjı gör.

## Temel denklem

```
P_rx (dBm) = P_tx (dBm) + G_tx (dBi) + G_rx (dBi) - PathLoss (dB) - kayıplar
Link Marjı (dB) = P_rx - Alıcı_Hassasiyeti (dBm)
```

Marj > 0 ise link (teorik olarak) kapanır. Pratikte ~10 dB+ marj hedeflenir (fading için).

## Serbest uzay yol kaybı (FSPL)

```
FSPL (dB) = 20*log10(d_km) + 20*log10(f_MHz) + 32.44
```

Örnek: 868 MHz, 100 m (0.1 km) → FSPL ≈ 20*log10(0.1) + 20*log10(868) + 32.44 ≈ 71.2 dB

## Hesap tablosu (doldur)

| Parametre | Değer | Not |
|---|---|---|
| P_tx | __ dBm | SX1262 (TR sınırı 25 mW e.r.p. ≈ +14 dBm e.r.p.) |
| G_tx (anten) | __ dBi | PCB iz anteni tipik ~0–2 dBi |
| G_rx (anten) | __ dBi | |
| Mesafe (hedef) | __ m | |
| FSPL | __ dB | formülden |
| Diğer kayıplar | __ dB | konnektör, mismatch, gövde/engel |
| **P_rx (hesap)** | __ dBm | |
| Alıcı hassasiyeti | __ dBm | SX1262 LoRa'da SF/BW'ye göre −124…−148 dBm mertebesi |
| **Link marjı** | __ dB | P_rx − hassasiyet |

## Notlar
- LoRa'nın büyük avantajı: yüksek SF → çok düşük hassasiyet (uzun menzil), ama düşük hız.
  SF/BW seçimi LINK_PROTOCOL.md ile birlikte kararlaştırılacak.
- Mismatch kaybı (kötü matching) doğrudan buraya "kayıp" olarak girer → RF tasarımının
  menzile etkisini burada sayısal görürsün.
