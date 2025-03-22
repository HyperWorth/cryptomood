import logging
import time
import json
from google import genai
from google.genai import types
from pydantic import BaseModel
from database import get_user_start_date

# Logger ayarları
logging.basicConfig(
    filename="sentiment.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

try:
    client = genai.Client(api_key="Gemini Api")
    logging.info("Google Gemini istemcisi başarıyla oluşturuldu.")
except Exception as e:
    logging.error("Google Gemini istemcisi oluşturulurken hata oluştu: %s", str(e))
    raise

class Sentiment(BaseModel):
    score_key: str
    score_value: int

def analyze_sentiment_with_Gemini(coin, contex):
    results = []
    for url, created_at, article_text in contex:
        try:
            logging.info("İşleniyor: %s", url)
            time.sleep(20)

            prompt = f"""
        Rules:
        1. Focus only on the specified cryptocurrency: {coin}.  
        2. Assign a score between -100 and +100 based on the impact of the news on {coin}.  
            - A positive score indicates a positive impact of the news on {coin} (potential increase in value).  
            - A negative score indicates a negative impact of the news on {coin} (potential decrease in value).  
            - A score of 0 means no significant impact on {coin}.  
        3. Output format: score_key : score_value (e.g., "score" : 50).  
        4. Do not provide any other output format other than the example above.  

        News Summary:
        {article_text}
        """
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': list[Sentiment],
                },
                contents=prompt
            )
            results.extend([(url, created_at, article_text, dict(response.parsed).values())])
            logging.info("İşlenen makale: %s", url)
        except Exception as e:
            logging.error("Makalede hata oluştu: %s", str(e))
    return results

def save_results_to_json(results, filename="sentiment_analysis_results.json"):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        logging.info("Sonuçlar %s dosyasına kaydedildi.", filename)
    except Exception as e:
        logging.error("JSON kaydedilirken hata oluştu: %s", str(e))

iterations = 1000
coin = input("Enter the cryptocurrency: ")
contex =   get_user_start_date()

results = []
for i in range(iterations):
    logging.info("Deneme numarası: %d", i)
    try:
        result = analyze_sentiment_with_Gemini(coin, contex)
        for url, created_at, article_text, response in result:
            results.append({
                "Adress": url,
                "Date": created_at,
                "News": article_text[:100],
                tuple(list(response)[0])[0]: tuple(list(response)[0])[1]
            })
        save_results_to_json(results)
        break
    except Exception as e:
        logging.error("Genel hata: %s", str(e))

        