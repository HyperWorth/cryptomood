import sqlite3
import logging
from datetime import datetime

# Logger ayarları
logging.basicConfig(
    filename="database.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def create_connection():
    try:
        conn = sqlite3.connect('articles.db')
        logging.info("Veritabanına bağlandı.")
        return conn
    except sqlite3.Error as e:
        logging.error("Veritabanı bağlantı hatası: %s", str(e))
        return None

def create_table():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                created_at DATETIME NOT NULL,
                article_text TEXT NOT NULL
            )
            ''')
            conn.commit()
            logging.info("Tablo başarıyla oluşturuldu.")
        except sqlite3.Error as e:
            logging.error("Tablo oluşturulurken hata: %s", str(e))
        finally:
            conn.close()

def insert_article(url, created_at, article_text):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO articles (url, created_at, article_text)
            VALUES (?, ?, ?)
            ''', (url, created_at, article_text))
            conn.commit()
            logging.info("Makale başarıyla eklendi: %s", url)
        except sqlite3.IntegrityError:
            logging.warning("URL zaten mevcut: %s", url)
        except sqlite3.Error as e:
            logging.error("Veritabanı hatası: %s", str(e))
        finally:
            conn.close()

def get_articles_by_date_range(start_date):
    end_date = datetime.now().strftime('%Y-%m-%d')
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
            SELECT url, created_at, article_text FROM articles
            WHERE DATE(created_at) BETWEEN ? AND ?
            ''', (start_date, end_date))
            articles = cursor.fetchall()
            logging.info("%s ile %s arasındaki makaleler getirildi.", start_date, end_date)
            return articles
        except sqlite3.Error as e:
            logging.error("Sorgu hatası: %s", str(e))
        finally:
            conn.close()
    return []

def get_user_start_date():
    try:
        while True:
            start_date = input("Başlangıç tarihini girin (YYYY-MM-DD formatında): ")
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
                break
            except ValueError:
                logging.warning("Hatalı tarih formatı girildi: %s", start_date)
                print("Hatalı tarih formatı! Lütfen YYYY-MM-DD formatında girin.")
        articles = get_articles_by_date_range(start_date)
        if articles:
            logging.info("%s tarihinden itibaren %d makale bulundu.", start_date, len(articles))
            return articles
        else:
            logging.info("%s tarihinden itibaren makale bulunamadı.", start_date)
            print(f"{start_date} tarihinden itibaren makale bulunamadı.")
    except Exception as e:
        logging.error("Beklenmedik bir hata oluştu: %s", str(e))
