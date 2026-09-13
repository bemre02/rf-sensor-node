# RF Tasarım Defteri

Bu dosya, RF ön-ucunun tasarım kararlarını + hesaplarını + (sonradan) ölçümlerini tutar.
Amaç: her komponentin **neden** orada olduğunu yazılı hale getirmek (senin GOMME_KILAVUZU /
CAN_MAPPING disiplininde). Boş bırakılan yerler Faz A/B'de doldurulacak.

## 0. Hedef parametreler
- Frekans: **868 MHz** (TR SRD, 25 mW e.r.p. sınırı)
- Sistem empedansı: **50 Ω** (tek-uçlu)
- Transceiver: **SX1262** (+14/+22 dBm çıkış ayarlanabilir; TR sınırına göre ayarlanacak)

## 1. Stackup ve 50 Ω microstrip
- [ ] PCB üretici + stackup seçilecek (kaç katman? 2L yeterli mi, yoksa 4L mi?).
  - SX1261 referansı 2L, SX1262 (+22 dBm) referansı **4L** (termal + RF referans düzlemi).
- [ ] Dielektrik: FR4 (εr ≈ 4.3, ama üreticinin gerçek değeri alınacak), bakır kalınlığı, prepreg.
- [ ] 50 Ω microstrip iz genişliği: __ mm  (hesap: KiCad calc / sim; GPS26'daki gibi Altium'da
      empedans profili ile teyit).
- Notlar:

## 2. Empedans uyumlama (matching)
- [ ] Anten ham empedansı (ZL) belirlenecek (datasheet/sim/ölçüm). İlk tasarım için varsayım: __
- [ ] Matching topolojisi: L-match / Pi / T? (başlangıç: L-match, `sim/matching_lmatch.py`)
- [ ] Komponent değerleri (L, C) + tolerans/self-rezonans notları:
- Smith abağı / S11 sim sonucu: (sim/ çıktısını buraya ekle)

## 3. Harmonik filtre
SX1262 PA çıkışı harmonik üretir; yasal emisyon için bastırılmalı.
- [ ] 2. harmonik (1736 MHz) ve yüksek mertebe için LC filtre tasarımı (S21 sim).
- [ ] Johanson IPD (0900FM15x0039) tek parça mı, ayrık L/C mi? (ikisini sim'de kıyasla)
- Notlar:

## 4. Anten
- [ ] Tip: PCB iz anteni (meander/IFA) / chip anten / SMA+harici? (öğrenme için PCB iz önerilir)
- [ ] Boyut/rezonans sim (SonnetLite/openEMS) + trim planı.
- Notlar:

## 5. Layout kuralları (SX1262 app-note)
- [ ] Tüm RF hatları 50 Ω.
- [ ] Matching/filtre komponentleri RF pinlerine mümkün olduğunca yakın.
- [ ] GND via yerleşimi (harmonik filtrede kritik).
- [ ] Kristal etrafında termal void (uzun paketlerde ısı → frekans kayması). +22 dBm'de TCXO düşün.
- [ ] RF switch (varsa) ve anten portu 50 Ω.

## 6. Doğrulama planı
- Sim: scikit-rf (matching/S11), QucsStudio (filtre S21), SonnetLite/openEMS (anten).
- Fonksiyonel: SX1262 **RSSI/SNR** okuma; anten/matching varyantlarını RSSI ile kıyasla; menzil testi.
- İleri: ITÜ EHB lab VNA ile gerçek S11/S21 (satın alma yok).
