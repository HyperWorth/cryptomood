import logging
import shutil
import os
from fetch_filtered_hrefs import fetch_filtered_hrefs, fetch_article_content
from database import create_table
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import threading
import time

# Logging setup
logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logging.info("🔄 Web Scraper başlatıldı.")

# Yedekleme fonksiyonu
def backup_database():
    backup_folder = 'yedek_database'
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    # Veritabanı dosyasının yedeğini almak için dosya yolunu ayarlayın
    db_file = 'articles.db'  # Veritabanı dosyanızın adı

    # Yedek dosya ismi zaman damgası ile oluşturuluyor
    timestamp = time.strftime("%Y%m%d%H%M%S")
    backup_file = os.path.join(backup_folder, f"yedek_{timestamp}.db")

    try:
        shutil.copy(db_file, backup_file)
        logging.info(f"✅ Yedek alındı: {backup_file}")

        # Yedeklerin sayısını kontrol et
        backups = sorted(os.listdir(backup_folder))
        if len(backups) > 5:
            # Fazla yedek varsa, en eski yedeği sil
            oldest_backup = backups[0]
            oldest_backup_path = os.path.join(backup_folder, oldest_backup)
            os.remove(oldest_backup_path)
            logging.info(f"❌ Eski yedek silindi: {oldest_backup}")

    except Exception as e:
        logging.error(f"❌ Yedek alınırken hata oluştu: {e}")

# Veritabanı yedeğini her 1 saatte bir almak için threading kullanıyoruz
def schedule_backup():
    while True:
        backup_database()
        time.sleep(3600)  # 1 saat (3600 saniye) bekle

def create_table_and_scrape():
    try:
        create_table()
        logging.info("✅ Veritabanı tablosu oluşturuldu veya zaten mevcut.")
    except Exception as e:
        logging.error(f"❌ Veritabanı oluşturulurken hata oluştu: {e}")

    # URL listesi ve her URL için filtreler
    url_filters = {
        "https://www.coindesk.com/business": ['/business/'],
        "https://www.coindesk.com/markets": ['/markets/'],
        "https://cryptonews.com/news/": ['news/'],
    }

    # Base URL'leri tanımla
    base_urls = {
        "https://www.coindesk.com/business": "https://www.coindesk.com",
        "https://www.coindesk.com/markets": "https://www.coindesk.com",
        "https://cryptonews.com/news/": "https://cryptonews.com",
    }

    content_div_classes = {
        "https://www.coindesk.com": ".document-body.font-body-lg p",
        "https://cryptonews.com": ".article-single__content.category_contents_details p",
    }

    unwanted_filters = [
        '/page/', 
        '/sitemap/', 
        '?page=', 
        'ethereum-news/', 
        'blockchain-news/', 
        'altcoin-news/', 
        'bitcoin-news/', 
        'price-analysis/', 
        'twitter.com', 
        'defi-news/', 
        'nft-news/'
    ]

    article_urls = []
    article_content = []

    # Her URL için belirli filtreleri çalıştır
    for url, filters in url_filters.items():
        base_url = base_urls.get(url, url)  
        try:
            logging.info(f"🔍 {url} sitesinden makale linkleri çekiliyor...")
            fetched_urls = fetch_filtered_hrefs(url, filters, base_url, unwanted_filters)
            article_urls.extend(fetched_urls)
            logging.info(f"✅ {len(fetched_urls)} makale URL'si bulundu.")
        except Exception as e:
            logging.error(f"❌ {url} için linkler çekilirken hata oluştu: {e}")

    for url in article_urls:
        base_url = next((k for k in content_div_classes if url.startswith(k)), None)

        if base_url:
            content_div_class = content_div_classes[base_url]
            try:
                logging.info(f"📄 {url} içeriği çekiliyor...")
                content = fetch_article_content(url, base_url, content_div_class)
                article_content.append(content)
                logging.info(f"✅ {url} içeriği başarıyla alındı.")
            except Exception as e:
                logging.error(f"❌ {url} içeriği alınırken hata oluştu: {e}")

    logging.info("🎉 Web Scraper işlemi tamamlandı.")

def schedule_scraping():
    while True:
        logging.info("⏰ Web scraping işlemi başlatılıyor...")
        create_table_and_scrape()
        time.sleep(1800)  # 30 dakika (1800 saniye) bekle


def create_image():
    # Basit bir simge oluşturuluyor
    image = Image.new('RGB', (64, 64), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.text((10, 25), "🖥", fill=(0, 0, 0))  # Basit bir metin ekliyoruz (simge için)
    return image

def on_quit(icon, item):
    icon.stop()

def run_scraper_in_background():
    # Scraper'ı arka planda bir thread ile çalıştırıyoruz
    scraper_thread = threading.Thread(target=create_table_and_scrape)
    scraper_thread.daemon = True
    scraper_thread.start()

def setup_tray():
    # Tray simgesi ayarlanıyor
    icon = pystray.Icon("scraper", create_image(), menu=( 
        item("Başlat", lambda icon, item: run_scraper_in_background()),
        item("Çıkış", on_quit)
    ))

    # Yedekleme işlemi arka planda başlatılıyor
    backup_thread = threading.Thread(target=schedule_backup)
    backup_thread.daemon = True
    backup_thread.start()

    # Web scraping işlemi arka planda başlatılıyor
    scraping_thread = threading.Thread(target=schedule_scraping)
    scraping_thread.daemon = True
    scraping_thread.start()

    icon.run()

if __name__ == "__main__":
    setup_tray()
