import platform
import subprocess

system_name = platform.system()

if system_name == "Darwin":
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    import re
    import random 
    import pandas as pd
    from io import StringIO
    import platform
    import subprocess
    import psutil
    import time

    def find_pid_by_app_name(app_name):
        """
        Uygulama adına (Mac uygulama adı) göre süreç kimliğini (PID) bulur.
        """
        for proc in psutil.process_iter(['name', 'pid']):
            # Mac'te 'Google Chrome Helper' gibi ek süreçler de olduğu için
            # Uygulama adının süreç adında geçip geçmediğini kontrol ediyoruz.
            if app_name.lower() in proc.info['name'].lower():
                return proc.info['pid']
        return None

    def apply_renice(pid, priority_level):
        """
        Belirtilen PID'ye renice komutunu uygulayarak CPU önceliğini değiştirir.
        NOT: renice çalıştırmak için 'sudo' veya kullanıcı izni gerekebilir.
        Öncelik Seviyeleri: -20 (En yüksek öncelik) ile 19 (En düşük öncelik) arası.
        """
        if pid is None:
            print("Optimizasyon: PID bulunamadı, öncelik değiştirilemedi.")
            return

        # Renice komutunu -n (öncelik seviyesi) ve -p (PID) ile çalıştır.
        try:
            # Öncelik seviyesini string'e çevir.
            priority_str = str(priority_level)
            
            # subprocess.run ile renice komutunu çalıştırma
            # Sudo kullanılması, Mac'in izin vermesi için zorunlu olabilir.
            subprocess.run(["sudo", "renice", priority_str, "-p", str(pid)], 
                        check=True, 
                        capture_output=True, 
                        text=True)
            
            print(f"Optimizasyon: PID {pid} için CPU önceliği {priority_level} olarak ayarlandı.")
            
        except subprocess.CalledProcessError as e:
            # Eğer sudo parolası girilmezse veya izin reddedilirse bu hata oluşur.
            print(f"HATA: Renice komutu başarısız oldu. İzin veya sudo hatası.")
            # print(f"Detay: {e.stderr.strip()}")
        except Exception as e:
            print(f"Beklenmedik renice hatası: {e}")

    def get_active_window_info():
        """
        Mac'in AppleScript'i kullanarak aktif uygulamanın adını ve pencere başlığını döndürür.
        Bu versiyon, hata durumlarında uygulamanın adını döndürmeye odaklanır.
        """
        
        applescript_command = """
        tell application "System Events"
            set frontmost_app to first process whose frontmost is true
            set app_name to name of frontmost_app
            
            try
                set window_name to name of front window of frontmost_app
            on error
                -- Eğer pencere başlığı alınamazsa, boş bırak.
                set window_name to ""
            end try
        end tell
        
        return app_name & "|" & window_name
        """
        
        try:
            result = subprocess.run(['osascript', '-e', applescript_command], 
                                    capture_output=True, 
                                    text=True, 
                                    check=False)

            output = result.stdout.strip()
            
            if result.returncode != 0:
                simple_script = "tell application \"System Events\" to return name of first process whose frontmost is true"
                simple_result = subprocess.run(['osascript', '-e', simple_script], capture_output=True, text=True)
                return simple_result.stdout.strip() or "Bilinmiyor", "Hata (Fallback)"

            if "|" in output:
                app_name, window_title = output.split("|", 1)
            else:
                app_name = output.replace("|", "")
                window_title = ""
                
            return app_name.strip(), window_title.strip()
            
        except Exception as e:
            return "Bilinmiyor", f"Python Hata: {e}"

    # +++ EKLENECEK FONKSİYON BİTTİ +++

    def list_running_applications():
        """
        Mac'in AppleScript'i kullanarak şu anda açık (çalışan) olan tüm uygulamaların
        adlarını döndüren fonksiyon.
        """
        
        # AppleScript komutu: 'System Events'e, çalışan tüm süreçlerin adlarını sormayı emret
        applescript_command = """
        tell application "System Events"
            set app_list to name of every process where background only is false
            set list_string to ""
            repeat with app_name in app_list
                set list_string to list_string & app_name & ","
            end repeat
            return list_string
        end tell
        """
        
        try:
            # Komutu çalıştır
            result = subprocess.run(['osascript', '-e', applescript_command], 
                                    capture_output=True, 
                                    text=True, 
                                    check=False) # Hata olursa durdurmasın

            output = result.stdout.strip()

            if result.returncode != 0:
                # Kritik AppleScript hatası durumunda
                print(f"Hata: AppleScript açık uygulamaları listeleyemedi. Kod: {result.returncode}")
                return []
                
            # Virgülle ayrılmış dizeyi Python listesine dönüştür
            app_list = [app.strip() for app in output.split(',') if app.strip()]
            
            return app_list
            
        except Exception as e:
            print(f"Python Hatası: Uygulama listesi alınamadı. {e}")
            return []

    VERI_SETI_METIN = """
    Pencere Başlığı, Etiket
    Zoom Meeting, TOPLANTI
    Microsoft Teams, TOPLANTI
    Safari - Netflix, EĞLENCE
    iTerm2, KODLAMA
    Visual Studio Code, KODLAMA
    PyCharm, KODLAMA
    Terminal, KODLAMA
    Google Chrome, DİĞER
    Finder, SİSTEMc
    Sistem Ayarları, SİSTEM
    App Store, DİĞER
    """

    # Metin verisini Pandas DataFrame'e dönüştür
    df_baglam = pd.read_csv(StringIO(VERI_SETI_METIN))
    #print(df_baglam)
    # Yeni eklenecek satır: Sütun adlarındaki tüm boşlukları temizler
    df_baglam.columns = df_baglam.columns.str.strip()
    # Eğitim setini X (girdiler) ve y (etiketler) olarak ayır
    X = df_baglam['Pencere Başlığı']
    y = df_baglam['Etiket']

    # Model Eğitimi (TF-IDF Vektörleştirme ve Naive Bayes Sınıflandırıcı)
    # Pipeline, adımları sırayla otomatikleştiren yapıdır.
    model_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(token_pattern=r'\b\w+\b', stop_words=None)),
        ('clf', MultinomialNB())
    ])

    # Modeli Eğit
    model_pipeline.fit(X, y)
    print("Sınıflandırma Modeli Eğitildi!")

    # -------------------------------------------------------------------------
    # Yeni Fonksiyon: Bağlamı Sınıflandırma
    # -------------------------------------------------------------------------

    def classify_context(app_name, window_title):
        """
        Uygulama adı ve pencere başlığını kullanarak bağlamı sınıflandırır.
        """
        
        # Girdi metnini oluştur (Model için)
        input_text = f"{app_name} - {window_title}"
        
        try:
            # Modeli kullanarak tahmin yap
            tahmin = model_pipeline.predict([input_text])[0]
            
            # Güvenilirlik hesaplama (Opsiyonel ama faydalı)
            probabilities = model_pipeline.predict_proba([input_text])[0]
            max_prob = max(probabilities)
            
            if max_prob < 0.5: # Yeterince emin değilse
                # Basit anahtar kelime kontrolü ile DİĞER'e düşebilir.
                if "Google" in input_text or "Safari" in input_text:
                    return "WEB BROWSING"
                return "DİĞER"
                
            return tahmin
        
        except Exception as e:
            # Model yüklenmemişse veya hata varsa DİĞER döndür
            return "DİĞER"
        
    HIGH_PRIORITY = -10
    LOW_PRIORITY = 10
    NORMAL_PRIORITY = 0

    def main_optimization_loop():
        print("--- WIX Akıllı Optimize Edici Başlatıldı ---")
        
        while True:
            try:
                # 1. BİLGİ TOPLAMA
                app, title = get_active_window_info() 
                
                # Eğer sadece Terminal'i görüyorsa, izinleri tekrar kontrol edin.
                if app == "Bilinmiyor" or app == "iTerm2" or app == "Terminal":
                    time.sleep(5)
                    continue

                # 2. BAĞLAM SINIFLANDIRMA (AI Çekirdeği)
                context = classify_context(app, title)

                print(f"\n[Döngü] Aktif: {app} | Bağlam: {context}")
                
                # 3. AKTİF UYGULAMANIN PID'SİNİ BULMA
                active_pid = find_pid_by_app_name(app)
                
                if active_pid:
                    # 4. DİNAMİK KAYNAK YÖNETİMİ
                    
                    if context in ["TOPLANTI", "KODLAMA"]:
                        # Toplantı ve Kodlama için YÜKSEK öncelik
                        apply_renice(active_pid, HIGH_PRIORITY)
                        
                        # Opsiyonel: Diğer uygulamaları LOW_PRIORITY'e çekme
                        # Bu, ek psutil döngüsü gerektirir ve daha karmaşıktır.
                        
                    elif context in ["EĞLENCE", "WEB BROWSING"]:
                        # Eğlence veya Web için NORMAL öncelik
                        apply_renice(active_pid, NORMAL_PRIORITY)
                        
                    elif context in ["SİSTEM", "DİĞER"]:
                        # Sistem uygulamalarını (Finder, Ayarlar) NORMAL/DÜŞÜK tut
                        apply_renice(active_pid, LOW_PRIORITY)
                    
                    else:
                        # Tanımlı olmayan her şey için normal ayar
                        apply_renice(active_pid, NORMAL_PRIORITY)
                
                # 5. BEKLEME
                # CPU'yu yormamak ve değişikliklerin uygulanması için beklenir.
                time.sleep(5) 

            except KeyboardInterrupt:
                print("\nOptimizasyon Döngüsü durduruldu.")
                break
            except Exception as e:
                print(f"Ana döngüde beklenmedik hata: {e}")
                time.sleep(5)
                continue

    # --- CANLI AKTİF BAĞLAM TAHMİNİ ---
    #app, title = get_active_window_info() 
    #live_context = classify_context(app, title)

    #print("\n------------------------------------")
    #print(f"CANLI VERİ: Uygulama: {app}")
    #print(f"CANLI VERİ: Başlık: {title}")
    #print(f"CANLI BAĞLAM TAHMİNİ: {live_context}")
    #print("------------------------------------")

    if __name__ == "__main__":
        main_optimization_loop()
        #Şu anki testiniz için:
        app, title = get_active_window_info() 
        live_context = classify_context(app, title)
        print(f"CANLI BAĞLAM TAHMİNİ: {live_context}")
        main_optimization_loop() #çalıştırılmadan önce bu satırların kaldırılması gerekir.
        
        # Tüm testler bittikten sonra:
        main_optimization_loop()

elif system_name == "Windows":
    pass

elif system_name == "Linux":
    pass