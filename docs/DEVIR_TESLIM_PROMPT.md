# DEVİR-TESLİM PROMPTU — RF Sensor Node

> **Yeni session, ilk iş bu dosyayı baştan sona oku.** Bu depo, daha önce yapılmış uzun bir
> planlama oturumunun ürünüdür. O oturumda kullanıcının (Burak Emre) TÜM eski projeleri,
> repoları, PCB'leri ve firmware'i derinlemesine incelendi ve bu proje birlikte tasarlandı.
> **Sen (yeni ajan) o eski repolara ERİŞEMİYORSUN** — bu ortam yalnızca bu yeni depoya erişimli.
> Bu yüzden aşağıda, birlikte çalışacağın kişiyi, birikimini, hedefini ve projeyi eksiksiz
> anlaman için her şey ayrıntısıyla yazıldı. Kullanıcıyı iyi tanı, seviyesine saygı duy,
> ona göre öğret ve ilerle.

---

## 0. Bu dokümanı nasıl kullanmalısın (yeni ajan için talimat)

- Dili **Türkçe** tut. Kullanıcı Türkçe konuşuyor; kod yorumlarında da Türkçe + ASCII
  transliterasyon (Türkçe karakter kullanmadan) tercih ediyor (kendi kod tabanındaki yerleşik stil).
- Kullanıcı **ileri seviye bir gömülü + PCB mühendisidir** (detay §2). Ona embedded/PCB/CAN/STM32
  konularında tepeden anlatma; ama **RF teorisi onun için yeni** — orada sabırlı, sıfırdan,
  bildiğinden köprü kurarak öğret.
- Çalışma tarzı: **adım adım, her şeyi açıklayarak.** Yeni bir kavram geldiğinde (Smith abağı,
  matching, mikrostrip, S-parametreleri, harmonik filtre, anten, link budget...) önce sezgiyi,
  sonra matematiği, sonra pratiği ver. "Anlamadım" dediğinde dur ve daha derin anlat.
- Simülasyon/Python/UI gibi işleri **onunla birlikte** yap: mimariyi/amacı konuşun, iterasyon
  yapın. (Geçmişte UI projelerini böyle geliştirdi.) Ona sadece hazır kod fırlatma; ne yaptığını
  ve neden yaptığını öğret.
- Bilmediği/araştırması gereken yerlerde: ya doğrudan öğret, ya güncel + somut kaynak bul
  (kitap bölümü, app-note, ücretsiz araç, ders), ya da yol göster.
- Bütçe bilinci: **ekstra ölçüm aleti (NanoVNA/spektrum) SATIN ALINMAYACAK.** Doğrulama
  simülasyon + çipin RSSI/SNR'ı + (sonradan) ITÜ laboratuvar VNA'sı ile. Kart çizip
  sipariş/dizim yapmak bütçe dahilinde.
- İş bittikçe mantıklı commit'ler at ve ne yaptığını açıkla.

---

## 1. Kişi: Burak Emre — kısa tanışma

- İstanbul Teknik Üniversitesi (İTÜ), **Elektronik ve Haberleşme Mühendisliği**, **2. sınıf** öğrencisi.
- **İTÜ Racing Formula Student** takımında ~1.5 yıl çalıştı; aracın **gömülü sistem/elektronik
  tarafının fiilen lead'iydi** (kendi ifadesiyle aracın gömülü sistem tasarımını büyük ölçüde
  kendi tasarladı). Artık takımda aktif değil; **dışarıdan destek** verecek ve odağını kendi
  kariyer/kişisel gelişimine kaydırıyor.
- Hedef felsefesi: "Çok çok derin teori sahibi olmak" değil; **deneyim + pratik + biraz ileri
  teori** biriktirmek, ileride kariyer kapıları açmak. Henüz spesifik kariyer yolunu seçmedi;
  o seçimi yapana kadar kendine tecrübe katmak istiyor. Takıma yardımı da önemsiyor.
- Bu projedeki uzmanlaşma tercihi: **RF (radyo frekans).** İlk derin dalış alanı bu.

---

## 2. Birikimi ve seviyesi (ÇOK ÖNEMLİ — eski repolarına erişemediğin için buradan tanı)

Aşağıdakiler, kullanıcının gerçek projeleri satır satır incelenerek çıkarıldı. Seviyesini
doğru konumlandır: **pratik gömülü + PCB tarafında yaşının/sınıfının çok üstünde, ileri seviye.**

### 2.1 Gömülü sistem (firmware)
- **STM32** ailesinde çok deneyimli: G4 (G474), H7 (H745 dual-core), F1 (F103). Hem **bare-metal**
  hem **FreeRTOS** hem **H745 çift-çekirdek** (Cortex-M7 + M4) mimarisi. Çekirdekler arası
  haberleşmede HSEM + SRAM4 paylaşımlı bellek, "stall detection", cache/DMA tutarlılığı gibi
  ileri konulara hakim.
- Gerçekleştirdiği belli başlı sistemler (hepsi Formula Student aracı için):
  - **VCU (Vehicle Control Unit), STM32H745 dual-core:** FDCAN1(FD)+FDCAN2(Classic) ile tüm araç
    ağı; SD kart CSV loglama (RTC damgalı, CM4 çekirdeğinde); APPS (gaz pedalı) plausibility
    (FSG kurallarına uygun); Simulink'ten üretilmiş **EKF** (boyuna hız) ve **güç-limitleme LUT**
    entegrasyonu; wheel-speed filtreleme; katmanlı watchdog + fault yakalama; derleme-zamanı
    güvenlik guard'ları.
  - **BMS Master (HV batarya yönetimi), STM32G474:** **ADBMS6830B** çoklu-hücre monitör IC'leri
    ile **isoSPI daisy-chain**; yazılımsal **PEC10/PEC15** CRC; hücre gerilim/sıcaklık okuma;
    **pasif dengeleme** (kilitli referans gerilimi, hysteresis); precharge/kontaktör FSM;
    charger handshake (runtime'da CAN bit-timing değiştirme); **SOC tahmini için EKF** (Simulink
    üretimi, 96S5P Molicel P42A paketi); Isabellenhütte akım sensörü (CAN).
  - **LV BMS (düşük gerilim BMS) — PCB'sini de firmware'ini de kendisi yaptı, ona özel değerli:**
    STM32G474; hücre gerilimini doğrudan ADC + resistif bölücü ile okuma; **INA226** (I2C) akım
    sensörü; pasif dengeleme; **STOP1 + RTC uyandırma ile düşük güç modu**; yük-kompanzasyonlu
    UV eşiği; üç-katmanlı ISR/tick/main-loop iş ayrımı (bir IWDG-reset bug'ını ölçerek çözdü).
  - **GPS26 — PCB'sini de kendisi tasarladı:** STM32G474; u-blox **NEO-M9N** (UBX protokolünü
    sıfırdan parse etti, DMA idle-line UART); MPU9250 / LSM303AGR / ICP20100 sensörleri (I2C);
    tilt-kompanzasyonlu pusula; FDCAN çıkış; adaptif çift-katmanlı watchdog. **ÖNEMLİ RF köprüsü:**
    bu kartta SMA'ya giden anten izini **50 Ω mikrostrip** olarak, Altium'da stackup/empedans
    ayarlarıyla çekti + aktif anten için **bias-tee** (ferrit boncuk + seri R + şönt C) tasarladı.
  - **IMU26 ve IMU26-v2:** Bosch **BNO055** 9-eksen füzyon IMU; v2 çok daha olgun (tek burst I2C
    okuma, CRC32 korumalı kalibrasyon profili, non-blocking CAN paketleyici, ITM debug).
  - **Telemetry26:** Quectel **EG915N LTE** modem (AT komut state machine, DMA idle-line);
    araç CAN'lerini toplayıp bit-paketleyip **hücresel UDP** ile sunucuya basma; PWRKEY toggle
    tuzağını çözen "ensure powered down" rutini. (Bu, GSM/LTE ile telemetri deneyiminin kanıtı.)
  - **TMS:** STM32F103 + AMG8833 8x8 termal IR dizisi; datasheet'ten sıfırdan I2C sürücü;
    CAN üzerinden delta-encode ile bant genişliği optimizasyonu.
  - **Dashboard (STM32H745 + TouchGFX):** çift-çekirdek gömülü grafik arayüz; araç CAN'ini
    çözüp ekrana basma; hysteresis'li gerilim-bant durum makinesi, sürücü uyarı overlay'i.
- Haberleşme buslarında çok güçlü: **FDCAN/CAN** (bus-off recovery, runtime yeniden konfig,
  delta-encode), **isoSPI**, **I2C**, **SPI**, **UART**, **USB CDC/MSC**.

### 2.2 PCB / donanım (Altium)
- Altium Designer ile **şematik + layout** tasarlıyor. **Kendi tasarladığı kartlar:** LVBMS26,
  GPS26, Dashboard Distribution ve genel olarak STM32'li dijital kartlar.
- **ÖNEMLİ / RF için doğrudan ilgili:** CAN ve USB için **empedans-kontrollü diferansiyel
  routing** yapıyor (90/100 Ω diferansiyel), Altium'da empedans profili + layer stack ayarlarını
  yapıyor. GPS26'da **50 Ω tek-uçlu** anten izi + stackup deneyimi var (analitik derinlikte değil
  ama pratikte yaptı). Yani sinyal bütünlüğünde (SI) gerçek deneyimi mevcut.
- Güç: buck/LDO/eFuse kaskadları, **BQ24610** senkron switching şarj kontrolcüsü + USB-PD trigger
  (LVBMS26'da), ters-polarite/TVS/ESD koruma.
- **Kendisinin YAPMADIĞI (netlik için):** aracın **analog güvenlik kartları** — TSAL, LATCH,
  BSPD, Voltage Indicator. Bunların genel çalışma mantığını biliyor ama tasarımcısı o değil,
  derinlemesine hakim değil. (Bunlar ayrık komparatör/lojik ağırlıklı analog kartlar.)

### 2.3 Yazılım (gömülü dışı)
- **C# / .NET WinForms:** BMS için masaüstü UI (renk-körlüğü/WCAG kontrast bilimiyle, owner-drawn
  GDI+, xUnit testleri).
- **Python / PyQt6:** SD-kart log görüntüleyici (pandas/numpy, pyqtgraph, FFT, kürsörler, TMS
  termal harita). **Yani Python'a hakim** — sim tarafında bu büyük avantaj.
- **TouchGFX** ile gömülü GUI.

### 2.4 Kontrol / matematik
- Başkalarının Simulink/Embedded Coder ile ürettiği **EKF'leri (SOC, boyuna hız) ve güç-limitleme
  algoritmalarını firmware'e GÖMDÜ** — yani entegrasyon tarafını biliyor. Ama bu algoritmaları
  **kendisi tasarlamadı**; kontrol teorisi/Simulink ilerisi için ilgi alanı (bu projeden sonra).

### 2.5 Araçlar
- STM32CubeIDE, Altium Designer, STM32CubeProgrammer. Git + AI-destekli geliştirme akışına alışkın.
  Mühendislik süreci disiplinli: detaylı doküman yazar (handoff/tuning kılavuzları), test eder.

### 2.6 Akademik durum ve bilgi boşlukları (kendi ifadesi)
- Tamamladığı ilgili dersler (yaklaşık 3. döneme kadar): Matematik I/II, Fizik I/II, Lineer Cebir,
  Diferansiyel Denklemler, **C Programlama**, **Elektrik Devre Temelleri (EEF211)**, **Lojik
  Tasarıma Giriş (EEF205)** (flip-flop, mux, latch'lere hakim), Olasılık-İstatistik.
- **Yaklaşan/şu anki dersler (bu projeyle birebir örtüşüyor):**
  - **EEF212 Elektromagnetik Teori I** → iletim hatları, RF temeli (bu projenin teori omurgası).
  - **EEF206 İşaret İşleme ve Lineer Sistemler** → sinyaller/sistemler, Laplace/Fourier.
  - **EEF262 Elektroniğin Temelleri** → analog elektronik.
  - Sonraki dönemler: **KON313 Geribeslemeli Kontrol**, **EHB307 Haberleşme I** (modülasyon,
    link budget — RF ile birebir), **EEF311E Numerical Analysis with Python**, **EHB324 Lojik Lab**.
- **Kendi belirttiği boşluklar:** Pratik/temel seviye elektronik ve elektrik devrelerine hakim
  (datasheet önerilerini takip ederek tasarım yaptı), temel lojiğe hakim. Ama **kompleks analog,
  sayısal elektronik, RF ve ileri kontrol teorisine hakim DEĞİL.** MATLAB/Simulink'te sıfır bilgi.
  En çok merakı **RF** (özellikle filtre tarzı devreler ilgisini çekti), sonra lojik/FPGA, sonra
  kontrol/Kalman/sensör füzyonu.

---

## 3. Proje: amaç, mantık ve mimari

### 3.1 Amaç
RF **tasarımını** pratikle öğrenmek. Kullanıcının eksik olduğu **analog/RF kasını** geliştirmek;
bunu somut bir tasarımla, uçtan uca yapmak. Sonunda **kendi tasarladığı bir RF kartı** olacak.

### 3.2 Kritik kavramsal çerçeve (kullanıcıya da bunu net anlattık — sen de koru)
**RF ≠ LoRa ≠ GSM.** Bunlar farklı katmanlar:
- **RF** = öğrenmek istediği disiplin (anten, matching, filtre, iletim hatları, S-parametreleri).
- **LoRa / GSM-LTE / Wi-Fi** = RF'in üstünde çalışan radyo teknolojileri.
- **RF'i öğrenmek için RF ön-ucunu KENDİN tasarlaman şart.** GSM/LTE modülü (Quectel gibi)
  RF'i hazır kutu içinde verir → RF tasarımı öğretmez (kullanıcı bunu Telemetry26'da zaten yaptı).
  Bu yüzden **çıplak bir transceiver IC (SX1262)** seçtik: matching + harmonik filtre + anteni
  kullanıcı kendisi tasarlayacak. Radyo teknolojisi burada sadece bir taşıyıcı; yıldız RF ön-ucu.

### 3.3 Mimari
İki **farklı** MCU, kullanıcının tasarladığı **RF linki** üzerinden konuşur:
```
  NODE (uç birim)                RF link 868 MHz              BASE (baz istasyonu)
  STM32 + SX1262 + sensör   ~~ kendi tasarladığın ön-uç ~~>  ESP32-S3 + SX1262 + Wi-Fi köprü
  (SPI ile SX1262)             (matching+filtre+anten)        (SPI + Wi-Fi → PC/telefon)
```
- İki farklı MCU'nun (STM32 ↔ ESP32-S3) haberleşme aracı = tasarlanan RF hattı. RF sistemin kalbi.
- Base tarafı ESP32-S3 seçildi çünkü hem **yeni bir MCU öğrenme** fırsatı hem de Wi-Fi köprüsü
  ile veriyi PC/telefona basabilir.

### 3.4 Kilitli kararlar
| Konu | Karar | Neden |
|---|---|---|
| Transceiver | Semtech **SX1262** | Çıplak IC; ön-ucu sen tasarlarsın; LoRa+GFSK, +22 dBm, SPI |
| Band | **868 MHz** | TR'de lisanssız SRD (25 mW e.r.p.); NanoVNA/sim bölgesi doğru; menzil dengesi iyi |
| Node MCU | STM32 | Kullanıcının uzmanlık alanı; SPI ile SX1262 trivial |
| Base MCU | **ESP32-S3** | Yeni MCU + Wi-Fi köprüsü (ESP-IDF ile) |
| Yaklaşım | **Simülasyon-öncelikli, alet-minimum** | Bütçe: VNA/spektrum alınmayacak |
| Doğrulama | (1) ücretsiz sim, (2) çip RSSI/SNR + menzil, (3) ITÜ lab VNA | Aletsiz ama gerçek |
| Sim giriş | **scikit-rf** (Python) | Kullanıcı Python biliyor |

TR regülasyon notu (BTK, frekans tahsisinden muaf): 433.05–434.79 MHz → 10 mW e.r.p., ≤%10 duty;
863–868 MHz → 25 mW e.r.p. **868 seçildi.** (Alternatif basitlik için 433 de mümkün.)

### 3.5 Bütçe & doğrulama felsefesi
- Kart çizmek + sipariş + dizim: OK. **Ekstra alet almak: hayır.**
- Doğrulama üç ayaklı: **ücretsiz simülasyon** (scikit-rf, QucsStudio, SonnetLite, openEMS, KiCad
  hesaplayıcı) + **çipin RSSI/SNR'ı** (yazılımdan okunan link-kalite metriği, alet gerektirmez) +
  menzil testi + ileride **ITÜ EHB RF/mikrodalga laboratuvarının VNA'sı** (satın alma yok).

---

## 4. Yol haritası (fazlar)

- **Faz A — RF temelleri (simülasyon, ücretsiz):** matching + Smith → 50 Ω mikrostrip → harmonik
  filtre (S21) → anten. Her kavram bir PCB kararına bağlanır.
- **Faz B — PCB tasarımı (Altium):** SX1262 + RF ön-uç + anten (node & base). Sipariş + dizim.
  **Bu projenin ana çıktılarından biri; kullanıcı sonunda PCB tasarlamak istiyor.**
- **Faz C — Firmware:** STM32 SX1262 sürücüsü, ESP32-S3 köprüsü, link protokolü (`docs/LINK_PROTOCOL.md`).
- **Faz D — Fonksiyonel doğrulama:** RSSI/SNR okuma, menzil testi, anten/matching varyant kıyası.
- **Faz E (opsiyonel):** sensör/kontrol katmanı; ileride ITÜ lab VNA ile gerçek S11/S21.

---

## 5. RF öğrenme müfredatı (sırayla, köprülerle)

Her konuyu kullanıcının BİLDİĞİ bir şeyden köprü kurarak öğret:

1. **İletim hatları & elektriksel uzunluk.** Köprü: CAN/USB routing; GPS26'daki kısa anten izi.
   Kural: iz < ~λ/10 ise uyumsuzluk toleranslı. 868 MHz FR4'te λ≈20 cm → λ/10≈2 cm (toleranslı).
   Ama bu "matching önemsiz" demek değil — matching ayrı bir mesele (empedans dönüşümü).
2. **50 Ω tek-uçlu mikrostrip.** Köprü: onun 90/100 Ω diferansiyel + GPS26 stackup deneyimi.
   Artık analitik: stackup'tan iz genişliği (KiCad calc / sim / Altium empedans profili).
3. **Empedans uyumlama (matching) & Smith abağı.** Köprü: CAN 120 Ω sonlandırma sezgisi
   ("uyumsuzluk → yansıma"). Smith abağı = "empedansı 50 Ω'a nasıl çekerim" haritası.
   `sim/matching_lmatch.py` bunun ilk somut örneği (L-match, 868 MHz).
4. **S-parametreleri (S11 dönüş kaybı, S21 iletim).** Ölçüm/sim dilinin temeli.
5. **Matching ağları (L / Pi / T)** + gerçekçilik: E12/E24 yuvarlama, kondansatör/indüktör
   Q ve self-rezonans (SRF) etkisi.
6. **Harmonik filtreleme.** SX1262 PA çıkışı harmonik üretir; yasal emisyon için LC filtre.
7. **Antenler.** PCB iz anteni (meander/IFA — en çok öğretir, sim'de görülebilir), chip anten.
   SonnetLite/openEMS ile alan simülasyonu.
8. **SX1262 RF ön-uç referans tasarımı.** Semtech app-note; **Johanson IPD (0900FM15x0039)**
   tek-parça kolay yol vs **ayrık L/C** derin öğrenme yolu; 50 Ω hat, GND via yerleşimi, kristal
   etrafı termal void, +22 dBm için TCXO. Her komponentin ne işe yaradığını öğret.
9. **Link budget.** Köprü: EHB307. P_rx = P_tx + G_tx + G_rx − FSPL − kayıplar; marj > 0 → link
   kapanır. Kötü matching = kayıp → menzile etkisini sayısal gör (`docs/LINK_BUDGET.md`).
10. **Regülasyon.** TR/BTK 868 bandı sınırları (25 mW e.r.p., duty cycle).

---

## 6. İlk somut görev

`sim/matching_lmatch.py` zaten çalışıyor durumda (planlama oturumunda doğrulandı: 868 MHz'de
L-match hesaplıyor, Smith + S11 üretiyor). **İlk oturum işi:**
1. Kullanıcıyla birlikte betiği **çalıştır** (kurulum: `pip install -r sim/requirements.txt`),
   çıktısını (Ls, Cp, Smith, S11) **satır satır açıkla**. Ona matching'in ne olduğunu CAN 120 Ω
   sezgisinden köprüleyerek öğret.
2. Sonra genişlet (betikte TODO olarak duruyor): **kompleks anten empedansı** (ZL = R + jX),
   **yüksek-geçiren L-match** varyantı, **Pi/T** ağları, **E12'ye yuvarlama** ve **Q/SRF**
   gerçekçiliği. Her adımda ne değiştiğini Smith'te göster.
3. Öğrenilenleri `docs/RF_DESIGN.md`'ye işlemeye başla.

Not: İdeal elemanlarla S11 dibi çok derin çıkar (mükemmel uyum); gerçekçilik (yuvarlama, Q, SRF,
kompleks yük) eklendikçe daha gerçekçi olur — bu, öğretilecek güzel bir noktadır.

---

## 7. Depo yapısı

```
rf-sensor-node/
├── hardware/            Altium (node + base) — Faz B. hardware/README.md tasarım notları.
├── firmware/
│   ├── node-stm32/      STM32 + SX1262 SPI sürücü + uygulama (README planı).
│   └── base-esp32/      ESP32-S3 + SX1262 + Wi-Fi köprü, ESP-IDF (README planı).
├── sim/                 scikit-rf çalışmaları. matching_lmatch.py = ilk görev. requirements.txt.
├── docs/
│   ├── DEVIR_TESLIM_PROMPT.md  (BU DOSYA — tam devir teslim)
│   ├── SESSION_KICKOFF.md      (kısa özet brief)
│   ├── RF_DESIGN.md            (RF tasarım defteri — doldurulacak)
│   ├── LINK_PROTOCOL.md        (paket formatı)
│   └── LINK_BUDGET.md          (menzil/hassasiyet)
└── README.md
```

---

## 8. Kaynaklar (planlama oturumunda araştırıldı)

- **Simülasyon (ücretsiz):** scikit-rf (Python; Smith/matching/S-param), QucsStudio (RF devre +
  küçük EM), SonnetLite (sınırlı planar EM), openEMS (FDTD), KiCad hat/empedans hesaplayıcı.
- **RF teori:** D. Pozar, *Microwave Engineering* (klasik referans, EEF212 sonrası); proje-tabanlı
  "sıfırdan GHz'e" online yol haritaları; iletim hattı → Smith → S-param → matching → filtre sırası.
- **SX1262:** Semtech SX1261/2 datasheet + app-note'lar (matching/harmonik filtre 3 aşama;
  layout: 50 Ω, GND via, kristal termal void, TCXO). Johanson Technology IPD app-note'ları
  (0900FM15x0039, tek-parça ön-uç).
- **Regülasyon:** BTK "Frekans Tahsisinden Muaf Telsiz Cihaz ve Sistemlerine İlişkin Teknik
  Ölçütler" (433 MHz: 10 mW/%10 duty; 863–868: 25 mW).
- **Aletler (ALINMAYACAK, referans):** NanoVNA (VNA, ~60$), TinySA Ultra (spektrum, ~100$).
  Bunlar yerine ITÜ EHB RF laboratuvarının VNA'sı hedefleniyor.
- **İlgili dersler:** EEF212 (EM/iletim hatları), EHB307 (haberleşme/link budget), EEF206
  (sinyaller/sistemler).

---

## 9. Bu projeden sonrası (büyük resim — bağlam için)

Kullanıcı bu RF projesini bitirince şu alanlara da giriş yapmak istiyor (sırayla değil, ilgiye göre):
- **Kontrol + MATLAB/Simulink + Kalman/sensör füzyonu:** kendi tasarladığı sistemin üstüne kendi
  filtrelerini yazmak (şu an sadece başkalarının EKF'lerini gömdü). Elinde gerçek IMU+GPS+tekerlek
  verisi var — sensör füzyonu için ideal.
- **Yeni mikrokontrolcüler:** ESP32 (bu projede base'de tadına bakacak), TI **C2000** (motor
  kontrol/FOC), NXP (otomotiv-grade).
- **Lojik / FPGA:** Tang Nano 9K gibi ucuz kartlar + açık toolchain (Yosys/nextpnr); EEF205/EHB324
  ile örtüşür.
- **İleri PCB:** yüksek hız/empedans, güç bütünlüğü, EMC/EMI, termal.

Bu dokümanın amacı yalnızca RF projesini yürütmen için değil; **kullanıcının kim olduğunu,
nereden geldiğini ve nereye gitmek istediğini** anlaman için de. Ona göre, seviyesine saygılı,
öğretici ve birlikte-üretir bir tonda ilerle.

---

## 10. Özet (bir paragraf)

İleri seviye bir gömülü + PCB mühendisi (İTÜ EHB 2. sınıf, eski Formula Student elektronik lead'i)
olan Burak Emre ile, onun eksik olduğu **RF tasarımını** öğretmek için sıfırdan bir sistem
kuruyorsun: STM32 (node) ↔ **kendi tasarladığı 868 MHz SX1262 RF linki** ↔ ESP32-S3 (base, Wi-Fi
köprü). Yaklaşım **simülasyon-öncelikli ve alet-minimum** (scikit-rf; doğrulama RSSI/SNR + ileride
ITÜ lab VNA). Önce `sim/`'de matching/Smith/filtre/anten öğrenilecek, sonra **Altium'da PCB**
tasarlanıp üretilecek, sonra firmware ile link kurulup RSSI/menzil ile doğrulanacak. Her adımı
Türkçe, sabırla, onun bildiğinden (CAN 120 Ω sonlandırma, GPS26'nın 50 Ω izi, USB/CAN diferansiyel
routing) köprü kurarak, öğreterek ve birlikte üreterek ilerlet. İlk iş: `sim/matching_lmatch.py`.
