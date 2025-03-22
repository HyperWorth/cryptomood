# CryptoMood
# Crypto News Scraper & Sentiment Analysis

Bu proje, belirlenen kripto haber sitelerinden haberleri çekerek bir veritabanına kaydeden ve isteğe bağlı olarak **Gemini** kullanarak duygu analizi yapan bir sistemdir.

## Özellikler
- **Web Scraping**: Kripto haber sitelerinden haber başlıklarını ve içeriklerini toplar.
- **Veri Tabanı Yönetimi**: Çekilen haberleri SQLite veritabanına kaydeder.
- **Duygu Analizi**: Google Gemini AI ile haberlerin duygu analizi yapılabilir.

## Gereksinimler
Bu projeyi çalıştırmak için aşağıdaki bağımlılıkları yüklemeniz gerekmektedir.

```bash
pip install -r requirements.txt
```

### Kullanılan Teknolojiler
- **Python**
- **SQLite** (Veri depolama için)
- **Playwright** (Web scraping için)
- **Google Gemini AI** (İsteğe bağlı duygu analizi için)

## Kurulum
1. **Depoyu Klonlayın**
```bash
git clone <repository_url>
cd cryptomood
```

2. **Gerekli Paketleri Yükleyin**
```bash
pip install -r requirements.txt
```

3. **Veritabanını Başlatın**
```python
from database import create_table
create_table()
```

4. **Haberleri Çekme ve Kaydetme**
```python
python main.py
```

## Kullanım
- **Haberleri Çekmek İçin**: `main.py` dosyasını çalıştırın.
- **Duygu Analizi Yapmak İçin**: AI modülünü etkinleştirin ve analiz yapmak istediğiniz veriyi girin.

## Katkıda Bulunma
Projeye katkıda bulunmak isterseniz, lütfen bir **pull request** oluşturun veya issue açarak geri bildirimde bulunun.

## Lisans
Bu proje MIT lisansı altında sunulmaktadır.

# Crypto News Scraper & Sentiment Analysis

Bu proje, belirlenen kripto haber sitelerinden haberleri çekerek bir veritabanına kaydeden ve isteğe bağlı olarak **Gemini** kullanarak duygu analizi yapan bir sistemdir.

## Özellikler
- **Web Scraping**: Kripto haber sitelerinden haber başlıklarını ve içeriklerini toplar.
- **Veri Tabanı Yönetimi**: Çekilen haberleri SQLite veritabanına kaydeder.
- **Duygu Analizi**: Google Gemini AI ile haberlerin duygu analizi yapılabilir.

## Gereksinimler
Bu projeyi çalıştırmak için aşağıdaki bağımlılıkları yüklemeniz gerekmektedir.

```bash
pip install -r requirements.txt
```

### Kullanılan Teknolojiler
- **Python**
- **SQLite** (Veri depolama için)
- **Playwright** (Web scraping için)
- **Google Gemini AI** (İsteğe bağlı duygu analizi için)

## Kurulum
1. **Depoyu Klonlayın**
```bash
git clone <repository_url>
cd cryptomood
```

2. **Gerekli Paketleri Yükleyin**
```bash
pip install -r requirements.txt
```

3. **Veritabanını Başlatın**
```python
from database import create_table
create_table()
```

4. **Haberleri Çekme ve Kaydetme**
```python
python main.py
```

## Kullanım
- **Haberleri Çekmek İçin**: `main.py` dosyasını çalıştırın.
- **Duygu Analizi Yapmak İçin**: AI modülünü etkinleştirin ve analiz yapmak istediğiniz veriyi girin.

## Katkıda Bulunma
Projeye katkıda bulunmak isterseniz, lütfen bir **pull request** oluşturun veya issue açarak geri bildirimde bulunun.

## Lisans
Bu proje MIT lisansı altında sunulmaktadır.

