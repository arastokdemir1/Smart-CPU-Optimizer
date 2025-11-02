# Smart-CPU-Optimizer
Smart optimization tool that dynamically adjusts macOS CPU priority by classifying the active application with artificial intelligence.

# 💻 Smart Optimize: Akıllı Mac CPU Öncelik Yöneticisi

[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)
[![Scikit-learn](https://img.shields.io/badge/Machine%20Learning-Scikit--learn-orange)](https://scikit-learn.org/)
[![Platform](https://img.shields.io/badge/Platform-macOS%20Only-lightgrey)](https://www.apple.com/macos)

## ✨ Proje Hakkında

**Smart Optimize**, macOS sisteminizde aktif olarak kullandığınız uygulamayı ve bağlamı (context) otomatik olarak algılayan ve buna göre CPU önceliğini (priority) dinamik olarak ayarlayan yapay zeka destekli bir araçtır.

Amacı, yüksek öncelikli görevlerde (Kodlama, Toplantı) sistem kaynaklarının ilgili uygulamaya tahsis edilmesini sağlayarak takılmaları azaltmak ve genel performansı optimize etmektir.

## 🧠 Nasıl Çalışır? (AI Çekirdeği)

Proje, üç ana aşamada çalışır:

1.  **Bilgi Toplama:** `osascript` (AppleScript) ve `psutil` kütüphaneleri kullanılarak şu an ön planda olan uygulamanın adı ve pencere başlığı sürekli olarak toplanır.
2.  **Bağlam Sınıflandırma (ML Modeli):**
    * Toplanan metin verisi, önceden eğitilmiş bir **TF-IDF Vektörleştirme** ve **Multinomial Naive Bayes (MNB)** sınıflandırıcısı tarafından analiz edilir.
    * Uygulama, bağlamı otomatik olarak şu kategorilerden birine atar: `KODLAMA`, `TOPLANTI`, `EĞLENCE`, `SİSTEM`, `DİĞER`.
3.  **Dinamik Optimizasyon (renice):**
    * Sınıflandırma sonucuna göre, aktif uygulamanın PID'sine (Süreç Kimliği) `sudo renice` komutu uygulanır.
    * Öncelik Seviyeleri:
        * `KODLAMA` ve `TOPLANTI`: **Yüksek Öncelik** (`-10`)
        * `EĞLENCE` ve `WEB BROWSING`: **Normal Öncelik** (`0`)
        * `SİSTEM` ve `DİĞER`: **Düşük Öncelik** (`+10`)

## 🛠️ Kurulum ve Çalıştırma

### Ön Koşullar

* macOS (Bu script yalnızca macOS üzerinde çalışır.)
* Python 3.x

### Adım Adım Kurulum

1.  **Depoyu Klonlayın:**
    ```bash
    git clone [https://github.com/](https://github.com/)[KULLANICI-ADINIZ]/Smart-Optimize.git
    cd Smart-Optimize
    ```

2.  **Gerekli Kütüphaneleri Kurun:**
    ```bash
    pip install -r requirements.txt
    # veya ayrı ayrı:
    # pip install pandas scikit-learn psutil
    ```

3.  **Çalıştırın:**

    ⚠️ **DİKKAT:** Bu script, sistem süreçlerinin önceliğini değiştirmek için `sudo renice` komutunu kullanır ve bu nedenle çalıştırılırken **yönetici parolası** gerektirir.

    ```bash
    python main.py
    ```
    *Script çalıştıktan sonra, terminal sizden şifrenizi isteyecek ve sonrasında arka planda sürekli olarak optimizasyon yapmaya başlayacaktır.*

## ⚙️ Gereksinimler (`requirements.txt`)
