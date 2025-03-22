import logging
import time
import pytz
import re
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin  # Base URL eklemek için
from datetime import datetime
from dateutil import parser  # Çeşitli tarih formatlarını işlemek için
from database import insert_article

# Logging ayarları
logging.basicConfig(
    filename='scraper.log', 
    level=logging.ERROR, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding="utf-8"
)

max_scroll_attempts = 20  # Maksimum scroll sayısı
scroll_delay = 2  # Scroll sonrası bekleme süresi (saniye)
timeout = 5000  # `wait_for_selector` için maksimum bekleme süresi (ms)

def fetch_filtered_hrefs(url, filters, base_url, unwanted_filters):
    Completed_Url_list = []
    """
    Belirli URL'ler için verilen filtrelerle href'leri alır.
    
    :param url: URL'yi belirtir.
    :param filters: URL'ye özel filtreler listesi (her URL için farklı filtreler belirlenebilir).
    :param base_url: Href'lerin eksik olduğu durumda eklenecek base URL.
    :param unwanted_filters: İstenmeyen URL'leri içeren filtreler listesi.
    """
    try:
        with sync_playwright() as p:
            # Chromium tarayıcısını başlat
            browser = p.chromium.launch(headless=True)  # headless=False yaparak tarayıcıyı görünür yapabilirsin
            # Yeni bir context (çalışma ortamı) oluşturun ve User-Agent'ı ayarlayın
            context = browser.new_context(
            storage_state=None,  # Çerezleri, önbelleği ve oturum verilerini saklamaz
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
            
            # Yeni bir sayfa oluşturun
            page = context.new_page()
            # Sayfayı yükle
            page.goto(url)
            page.wait_for_load_state('load')  # Sayfanın tamamen yüklenmesini bekleyelim
            time.sleep(5)  # Sayfanın yüklenmesini bekleyelim
            # 📌 1️⃣ Önce Sayfayı En Aşağı Kaydır
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)  # İçeriğin yüklenmesini bekleyelim
            # 📌 2️⃣ Sonra Sayfayı En Yukarı Kaydır
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)  # Sayfanın tekrar oturmasını bekleyelim
            for _ in range(max_scroll_attempts):
                # Önce <a> etiketlerinin yüklenip yüklenmediğini kontrol et
                if page.locator("a").count() > 0:
                    #print("✅ Linkler yüklendi, kaydırma işlemi durduruluyor.")
                    break  # Linkler yüklendiyse döngüyü kır
                    
                #print("❌ Linkler henüz yüklenmedi, kaydırmaya devam ediliyor...")

                # Sayfayı aşağı kaydır
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                time.sleep(scroll_delay)


            # Sayfadaki tüm <a> etiketlerini seç
            links = page.query_selector_all('a')

            # URL'leri saklamak için bir set oluştur
            url_set = set()

            # Her bir linki kontrol et
            for link in links:
                href = link.get_attribute('href')
                if href:
                    # Eğer href tam bir URL değilse (örn. /business/ gibi), base URL'yi ekle
                    if not href.startswith('http'):
                        href = urljoin(base_url, href)
                    
                    # Filtreleri kontrol et
                    for filter_pattern in filters:
                        if filter_pattern in href:  # `startswith` yerine `in` kullanarak daha geniş bir eşleşme sağlıyoruz
                            
                            if href == "https://cryptonews.com/news/":
                                #print(f"Istenmeyen tam eşleşen URL bulundu, atlanıyor: {href}")
                                break
                            # İstenmeyen URL'leri kontrol et
                            if any(unwanted in href for unwanted in unwanted_filters):
                                #print(f"Istenmeyen URL bulundu, atlanıyor: {href}")
                                break  # Bu URL'yi atla, diğer URL'lere geç
                            url_set.add(href)  # Set'e ekle (tekrar etmez)

            # Sonuç olarak kaç tane URL alındığını yazdır
            #print(f"Toplam alınan URL sayısı ({url}): {len(url_set)}")
            # Debug ekleyebilirsiniz
            # URL'leri yazdır
            for filtered_url in url_set:
                Completed_Url_list.append(filtered_url)
            context.close()
            browser.close()
            return Completed_Url_list
    except Exception as e:
        logging.error(f"URL çekme işlemi sırasında hata oluştu ({url}): {e}")
        return []

def convert_to_turkey_time(raw_date):
    """
    Farklı formatlarda gelen tarih bilgisini Türkiye saatine çevirir.

    :param raw_date: Çekilen tarih (string)
    :return: Türkiye saatine çevrilmiş tarih (string) veya hata durumunda orijinal hali
    """
    istanbul_tz = pytz.timezone("Europe/Istanbul")

    try:
        # Gereksiz metinleri (örneğin "Published") ve özel boşluk karakterlerini temizle
        raw_date = re.sub(r"(Published|Updated|on|at|)", "", raw_date).strip()  # "Published", "Updated" gibi metinleri temizle
        raw_date = raw_date.replace("\u202f", " ").strip()  # \u202f gibi özel boşlukları düzgün boşluğa çevir

        # GMT zaman dilimini kaldır (örneğin "GMT+3")
        raw_date = re.sub(r" GMT[+\-]\d+", "", raw_date).strip()

        # UTC ifadesini kaldır
        raw_date = raw_date.replace("UTC", "").strip()

        # "p.m." ve "a.m." gibi ifadeleri dönüştürme (önce küçük harfe, sonra doğru formatta)
        raw_date = raw_date.replace("p.m.", "PM").replace("a.m.", "AM")

        # Eğer tarih direkt ISO 8601 formatında (örneğin: 2025-03-20T15:30:00Z) geliyorsa
        if "T" in raw_date or "Z" in raw_date:
            date_obj = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))

        # Eğer tarih formatı "Mar 20, 2025, 6:06 p.m. UTC" şeklindeyse
        elif "," in raw_date and any(x in raw_date for x in ["AM", "PM"]):
            date_obj = datetime.strptime(raw_date, "%b %d, %Y, %I:%M %p")

        # Eğer tarih formatı "20 Mart 2025 18:15" şeklindeyse
        elif "Mart" in raw_date or "March" in raw_date:
            # Türkçe ay isimlerini kullanabilmek için locale ayarı yapılması gerekebilir.
            # Bunun için datetime'e yerel bir ayar eklemek gerekebilir.
            try:
                date_obj = datetime.strptime(raw_date, "%d %B %Y %H:%M")
            except ValueError:
                # Eğer Türkçe ay ismi hata verirse, string yerine sayılarla da işlem yapılabilir.
                raw_date = raw_date.replace("Mart", "March")
                date_obj = datetime.strptime(raw_date, "%d %B %Y %H:%M")

        # Tarih formatını otomatik algılamak için dateutil.parser'ı kullan
        else:
            date_obj = parser.parse(raw_date)

        # Eğer UTC veya başka bir zaman diliminde ise, Türkiye saatine çevir
        if date_obj.tzinfo is None:
            date_obj = pytz.utc.localize(date_obj)  # Eğer zaman dilimi yoksa UTC olarak kabul et

        date_obj = date_obj.astimezone(istanbul_tz)  # UTC'den Türkiye zaman dilimine çevir

        # Sonuç olarak Türkiye saatiyle formatlanmış tarihi döndür
        return date_obj.strftime("%Y-%m-%d %H:%M:%S")  # Format: YYYY-MM-DD HH:MM:SS

    except Exception as e:
        logging.error(f"❌ Tarih formatı dönüştürülürken hata oluştu: {raw_date} | Hata: {e}")
        return raw_date  # Hata durumunda orijinal formatı döndür

def fetch_article_date(page, base_url):
    """
    Sayfadaki makalenin yayınlanma tarihini çeker ve Türkiye saatine çevirir.

    :param page: Playwright sayfa nesnesi.
    :param base_url: Makalenin ait olduğu temel site URL'si.
    :return: Makalenin yayınlanma tarihi (string, Türkiye saati).
    """
    selector = date_selectors.get(base_url, None)

    if selector:
        try:
            date_element = page.locator(selector)
            if date_element.count() > 0:
                raw_date = date_element.inner_text().strip()
                return convert_to_turkey_time(raw_date)

        except Exception as e:
             logging.error(f"Hata: {e}")

    return "Tarih bulunamadı"

def fetch_article_content(article_url, base_url, content_div_class):
    """
    Verilen makale URL'sine giderek belirli bir div içindeki <p> etiketlerini toplar.
    
    :param article_url: Makale URL'si
    :param content_div_class: İçeriğin bulunduğu div'in class ismi
    :return: Makalenin içeriği (string)
    """
    try:
        with sync_playwright() as p:           
            try:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                storage_state=None,  
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
                page = context.new_page()

                # Makale sayfasına git
                page.goto(article_url)
                page.wait_for_load_state('load')
                time.sleep(5)  # Sayfanın yüklenmesini bekleyelim
                # 📌 1️⃣ Önce Sayfayı En Aşağı Kaydır
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(3)  # İçeriğin yüklenmesini bekleyelim
                # 📌 2️⃣ Sonra Sayfayı En Yukarı Kaydır
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(2)  # Sayfanın tekrar oturmasını bekleyelim

                for _ in range(max_scroll_attempts):
                    # Önce içeriğin yüklenip yüklenmediğini kontrol et
                    if page.locator(f"{content_div_class}").count() > 0:
                        #print("✅ Makale içeriği yüklendi, kaydırma işlemi durduruluyor.")
                        break  # İçerik yüklendiyse döngüyü kır
                        
                    #print("❌ İçerik henüz yüklenmedi, kaydırmaya devam ediliyor...")

                    # Sayfayı aşağı kaydır
                    page.evaluate("window.scrollBy(0, window.innerHeight)")
                    time.sleep(scroll_delay)
                
                article_date = fetch_article_date(page, base_url)

                # **Sadece belirli div içindeki <p> etiketlerini seçiyoruz**
                paragraphs = page.locator(f"{content_div_class}").all_text_contents()
                
                # Paragrafları tek bir string haline getir
                article_text = "\n".join(paragraphs)

                #print(f"\n✅ Makale Alındı: {article_url}\n")
                #print(article_text[:500])  # İlk 500 karakteri göster (kontrol için)

            except Exception as e:
                logging.error(f"❌ Hata oluştu ({article_url}): {e}")
                article_text = None
                article_date = None
                
            context.close()
            browser.close()
            insert_article(article_url, article_date, article_text)
            return article_url ,article_date, article_text
    except Exception as e:
        logging.error(f"Makale içeriği alınırken hata oluştu ({article_url}): {e}")
        return article_url, None, None


date_selectors = {
    "https://www.coindesk.com": ".font-metadata.flex.gap-4.text-charcoal-600.flex-col.md\:block > span.md\:ml-2",
    "https://cryptonews.com": ".single-post-new__author-top-value time",
}