from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import pandas as pd
from konlpy.tag import Okt
import re
import json
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# MySQL 연결 정보
username = os.getenv('sql_username')
password = os.getenv('sql_password')
host = os.getenv('sql_host')
port = os.getenv('sql_port')
database = 'team5'

engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")

# 불용어 리스트
STOPWORDS = ["및", "이러한", "그", "의", "를", "에", "은", "는", "이", "가", "하다", "있다", "되다", "것", "수", "들", "에서", "과", "다", "로"]

# 네이버 데이터랩 API 인증 정보
NAVER_CLIENT_ID = "zpSgqWzM1vozm9ZOAmNi"
NAVER_CLIENT_SECRET = "k0_3ltGDBx"

def convert_to_datetime(date_str):
    if not isinstance(date_str, str) or not date_str.strip():
        return None
    date_str = re.sub(r"오전", "AM", date_str)
    date_str = re.sub(r"오후", "PM", date_str)
    try:
        date_obj = pd.to_datetime(date_str, format="%Y.%m.%d. %p %I:%M")
        return date_obj.strftime("%Y-%m-%d %H:%M:%S")  # 문자열로 변환
        
    except ValueError as e:
        print(f"Error parsing date: {date_str}, Error: {e}")
        return None

def extract_keywords(text, top_n=5):
    okt = Okt()
    if not isinstance(text, str):
        return []
    nouns = okt.nouns(text)
    if not nouns:
        return []
    filtered_keywords = [noun for noun in nouns if noun not in STOPWORDS]
    return list(set(filtered_keywords[:top_n]))

def validate_keywords(keywords):
    return [kw for kw in keywords if kw]

def get_trend_data(keywords, start_date, end_date):
    url = "https://openapi.naver.com/v1/datalab/search"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "keywordGroups": [{"groupName": f"Keyword_{i+1}", "keywords": [kw]} for i, kw in enumerate(keywords)],
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(body))
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching trend data: {response.status_code}, Response: {response.text}")
            return {}
    except Exception as e:
        print(f"Exception during API call: {e}")
        return {}

def calculate_trend_index(keywords, article_date, baseline_date="2023-01-01"):
    valid_keywords = validate_keywords(keywords)
    if not valid_keywords:
        return 0.0

    # article_date가 str이라면, datetime 객체로 변환
    if isinstance(article_date, str):
        article_date = pd.to_datetime(article_date, errors='coerce')
    
    if pd.isna(article_date):  # 날짜가 제대로 파싱되지 않으면 처리
        return 0.0

    start_date = pd.to_datetime(baseline_date).strftime("%Y-%m-%d")
    end_date = (article_date - timedelta(days=1)).strftime("%Y-%m-%d")
    
    trend_data = get_trend_data(valid_keywords, start_date, end_date)
    try:
        trend_scores = []
        for result in trend_data.get("results", []):
            for data in result.get("data", []):
                if data["period"] == end_date:
                    trend_scores.append(data["ratio"])
        return sum(trend_scores) / len(trend_scores) if trend_scores else 0.0
    except Exception as e:
        print(f"Error calculating trend index: {e}")
        return 0.0


def fetch_news_links_by_date(sid, date, max_links=10):
    links = []
    for page in range(1, 11):
        url = f"https://news.naver.com/main/list.naver?mode=LSD&mid=shm&sid1={sid}&date={date}&page={page}"
        try:
            html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if html.status_code != 200:
                break
            soup = BeautifulSoup(html.text, "lxml")
            news_items = soup.select("ul.type06_headline > li, ul.type06 > li")
            if not news_items:
                break
            for item in news_items:
                if len(links) >= max_links:
                    break
                link = item.select_one("a")["href"]
                links.append(link)
            if len(links) >= max_links:
                break
            time.sleep(0.5)
        except Exception as e:
            print(f"Exception fetching news links: {e}")
            break
    return links

def fetch_article_details(url):
    try:
        html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if html.status_code != 200:
            return {"title": np.nan, "date": np.nan, "main": np.nan, "url": url}
        soup = BeautifulSoup(html.text, "lxml")
        title_selector = "#title_area > span"
        date_selector = "#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div:nth-child(1) > span"
        main_selector = "#dic_area"
        title = soup.select(title_selector)
        date = soup.select(date_selector)
        main = soup.select(main_selector)
        raw_date = " ".join([d.text.strip() for d in date]) if date else np.nan
        parsed_date = convert_to_datetime(raw_date)
        return {
            "title": " ".join([t.text.strip() for t in title]) if title else np.nan,
            "date": parsed_date,
            "main": " ".join([m.text.strip() for m in main]) if main else np.nan,
            "url": url
        }
    except Exception as e:
        print(f"Exception fetching article details: {e}")
        return {"title": np.nan, "date": np.nan, "main": np.nan, "url": url}

def load_sentiment_model():
    # 로컬 디렉토리 경로
    model_directory = "./dags/package/Kc"

    # 토크나이저와 모델 로드
    tokenizer = AutoTokenizer.from_pretrained(model_directory)
    model = AutoModelForSequenceClassification.from_pretrained(model_directory)
    
    # Sentiment Analysis 파이프라인 반환
    return pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

def analyze_sentiment(text, sentiment_analyzer):
    if not text or not isinstance(text, str):
        return {"label": "neutral", "score": 0.0}
    try:
        result = sentiment_analyzer(text[:512])
        return result[0]
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return {"label": "neutral", "score": 0.0}

def fetch_today_articles(section_lst, max_links=10):
    today = datetime.now().strftime("%Y%m%d")
    all_articles = []
    sentiment_analyzer = load_sentiment_model()
    for sid in section_lst:
        links = fetch_news_links_by_date(sid, today, max_links=max_links)
        for link in tqdm(links, desc=f"Fetching articles for SID {sid}"):
            article = fetch_article_details(link)
            article["category"] = sid
            article["keywords"] = validate_keywords(extract_keywords(article["main"]))
            article["trend_index"] = (
                calculate_trend_index(article["keywords"], article["date"])
                if article["date"] and article["keywords"] else 0.0
            )
            sentiment_result = analyze_sentiment(article["main"], sentiment_analyzer)
            article["sentiment_label"] = sentiment_result["label"]
            article["sentiment_score"] = sentiment_result["score"]
            all_articles.append(article)
    return all_articles

def save_trend_predictions_to_db(results):
    rows = []
    for category_id, data in results.items():
        if "error" in data:
            rows.append({
                "category_id": category_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "predicted_trend": None,
                "today_trend": None,
                "urls": None,
                "error": data["error"]
            })
        else:
            rows.append({
                "category_id": category_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "predicted_trend": data["predicted_trend"],
                "today_trend": data["today_trend"],
                "urls": json.dumps(data["urls"]),  # URL 리스트를 JSON 형식으로 저장
                "error": None
            })
    df = pd.DataFrame(rows)
    df.to_sql('trend_predictions', con=engine, if_exists='replace', index=False)
    print(f"{len(df)}개의 예측 결과가 'trend_predictions' 테이블에 업로드되었습니다.")


def predict_trends(**kwargs):
    # 바로 fetch_today_articles에서 받아온 데이터를 사용
    articles = kwargs['ti'].xcom_pull(task_ids='fetch_articles')

    # DataFrame으로 변환
    data = pd.DataFrame(articles)
    category_means = data.groupby("category")[["sentiment_score", "trend_index"]].mean().reset_index()
    optimal_lags = {100: 129, 101: 167, 102: 40, 103: 158, 104: 29, 105: 175}
    scaler = MinMaxScaler()
    scaler.fit(category_means[["sentiment_score", "trend_index"]])
    results = {}
    for category_id in optimal_lags.keys():
        model_path = f"./dags/package/models/best_model_category_{category_id}.h5"
        lag = optimal_lags[category_id]
        try:
            category_data = category_means[category_means["category"] == category_id]
            if category_data.empty:
                raise ValueError(f"No data for category {category_id}")
            sentiment_score = category_data["sentiment_score"].values[0]
            trend_index = category_data["trend_index"].values[0]
            input_data = np.array([[sentiment_score, trend_index]])
            input_data = scaler.transform(input_data)
            input_data = input_data.reshape((1, 2))  # 배치 차원 수정

            model = load_model(model_path, compile=False)
            predicted_trend = model.predict(input_data, batch_size=1)[0][0]
            results[category_id] = {
                "predicted_trend": float(predicted_trend),
                "today_trend": float(trend_index),
                "urls": data[data["category"] == category_id]["url"].tolist()
            }
        except Exception as e:
            results[category_id] = {"error": str(e)}
    save_trend_predictions_to_db(results)
    return results

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["your_email@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="trend_analysis_dag",
    default_args=default_args,
    description="Daily trend analysis",
    schedule_interval="0 9 * * *",
    start_date=datetime(2023, 11, 1),
    catchup=False,
    tags=["trend_analysis"],
) as dag:
    fetch_articles_task = PythonOperator(
        task_id="fetch_articles",
        python_callable=fetch_today_articles,
        op_kwargs={"section_lst": [100, 101, 102, 103, 104, 105]},
    )

    predict_trends_task = PythonOperator(
        task_id="predict_trends",
        python_callable=predict_trends,
        provide_context=True,
    )

    fetch_articles_task >> predict_trends_task