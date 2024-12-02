import os
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from collections import Counter
from konlpy.tag import Okt
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine
from opensearchpy import OpenSearch

# .env 파일에서 환경 변수 로드
load_dotenv()
# MySQL 연결 정보 설정
username = os.getenv('sql_username')
password = os.getenv('sql_password')
host = os.getenv('sql_host')
port = os.getenv('sql_port')
engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/team5")


NAVER_CLIENT_ID = os.getenv("NAVER_API_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_API_SECRET")

# OpenSearch 설정
op_host = os.getenv("HOST")
op_port = os.getenv("PORT")

client = OpenSearch(
    hosts=[{'host': op_host, 'port': op_port}])

def fetch_news_by_category(sid):
    """주어진 카테고리 ID에 대한 뉴스 기사를 크롤링하여 제목, 날짜, 본문 및 링크를 수집하는 함수."""
    url = f"https://news.naver.com/section/{sid}"  # 카테고리별 뉴스 섹션 URL
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    
    if html.status_code != 200:
        print(f"Error fetching news from {url}: {html.status_code}")
        return []

    soup = BeautifulSoup(html.text, "lxml")
    articles = []

    # 뉴스 기사 선택
    news_items = soup.select("li.sa_item._LAZY_LOADING_WRAP")  # 뉴스 기사 선택
    
    print(f"Found {len(news_items)} news items in category SID: {sid}")
    
    for item in news_items:
        link = item.select_one("a.sa_text_title")['href']
        title = item.select_one("strong.sa_text_strong").get_text(strip=True)
        
        # 각 기사 세부 정보 크롤링
        article_details = crawl_article_details(link)
        articles.append({
            "title": title,
            "link": link,
            **article_details  # 제목, 날짜, 본문 추가
        })
    
    print(f"Collected {len(articles)} articles from category SID: {sid}")
    return articles

def crawl_article_details(url):
    """주어진 URL에서 기사 제목, 날짜, 본문을 크롤링하여 딕셔너리로 반환하는 함수."""
    article_details = {}
    
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    
    if html.status_code != 200:
        print(f"Error fetching article details from {url}: {html.status_code}")
        return {"date": "날짜 없음", "main": "본문 없음"}

    soup = BeautifulSoup(html.text, "lxml")
    
    # 날짜 수집 (연도-월-일 형식으로 변환)
    date = soup.select_one("span.media_end_head_info_datestamp_time")
    if date:
        article_details["date"] = date['data-date-time'].split(" ")[0]  # "2024-11-17" 형식으로 저장
    else:
        article_details["date"] = "날짜 없음"
    
    # 본문 수집
    main_content = soup.select_one("article#dic_area")
    article_details["main"] = main_content.text.strip() if main_content else "본문 없음"
    
    return article_details

def preprocess_text(text):
    """텍스트를 전처리하여 명사만 추출하는 함수."""
    okt = Okt()
    tokens = okt.nouns(text)
    return [word for word in tokens if len(word) > 1]

def fetch_monthly_trend_data(word):
    """네이버 Datalab API에서 월별 트렌드 지수를 가져오는 함수."""
    url = "https://openapi.naver.com/v1/datalab/search"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
        "Content-Type": "application/json"
    }
    today = datetime.today()
    start_date = (today.replace(year=today.year - 1)).strftime('%Y-%m-%d')  # 1년 전
    end_date = today.strftime('%Y-%m-%d')  # 오늘

    body = json.dumps({
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "month",
        "keywordGroups": [{"groupName": word, "keywords": [word]}]
    })

    response = requests.post(url, headers=headers, data=body)
    
    if response.status_code != 200:
        print(f"Error fetching trend data for {word}: {response.status_code}")
        return []

    data = response.json()
    monthly_data = data.get('results', [])
    
    if monthly_data:
        print(f"Monthly trend data for {word}: {monthly_data[0]['data']}")
    else:
        print(f"No trend data found for {word}")
    
    return monthly_data[0]['data'] if monthly_data else []

def calculate_average_growth(trend_data):
    """트렌드 지수의 평균 증감율을 계산하는 함수."""
    if not trend_data or len(trend_data) < 2:
        return 0  # 데이터가 부족하면 0%로 처리
    
    growth_rates = []
    for i in range(1, len(trend_data)):
        prev_ratio = trend_data[i - 1]['ratio']
        current_ratio = trend_data[i]['ratio']
        growth_rate = ((current_ratio - prev_ratio) / prev_ratio) * 100 if prev_ratio != 0 else 0

        growth_rates.append(growth_rate)
    
    average_growth_rate = sum(growth_rates) / len(growth_rates)
    return average_growth_rate

def analyze_articles_with_trends(articles):
    """기사 분석 후 네이버 Datalab API를 사용해 트렌드 증가율을 포함한 데이터를 생성."""
    word_counter = Counter()
    
    for article in articles:
        processed_text = preprocess_text(article['main'])
        word_counter.update(processed_text)

    filtered_data = []
    trend_data = {}  # 트렌드 데이터 저장

    for word, count in word_counter.most_common(15):  # 상위 15개 키워드만 처리
        print(f"Analyzing trend for word: {word}")
        # 네이버 Datalab API로 현재 검색량과 월별 트렌드 지수 가져오기
        monthly_trend_data = fetch_monthly_trend_data(word)
        if not monthly_trend_data:
            trend_growth = 0  # 트렌드 데이터가 없으면 증가율 0%
        else:
            trend_growth = calculate_average_growth(monthly_trend_data)

        # 월별 ratio 저장
        monthly_ratios = {entry['period']: entry['ratio'] for entry in monthly_trend_data}
        
        related_articles = [
            {
                'title': article['title'],
                'link': article['link'],
                'date': article['date']
            }
            for article in articles if word in preprocess_text(article['main'])
        ]
        
        filtered_data.append({
            'word': word,
            'count': count,
            'trend_growth': trend_growth,
            'monthly_ratios': monthly_ratios,  # 월별 ratio 추가
            **{k: v for art in related_articles for k, v in art.items()}  # 관련 기사 정보를 동일한 계층에 추가
        })

    return filtered_data

def upload_to_opensearch(data):
    """OpenSearch에 데이터를 새로운 필드 형태로 날짜별로 쌓아 업로드하는 함수."""
    index_name = "new_trend"  # 고정 인덱스 이름
    today = datetime.now().strftime('%Y-%m-%d')  # 오늘 날짜

    for category, items in data.items():
        for item in items:
            word = item['word']
            count = item['count']
            trend_growth = item['trend_growth']
            related_articles = item.get('related_articles', [])
            monthly_ratios = item['monthly_ratios']
            data = []
            for period, ratio in monthly_ratios.items():
                # 문서 데이터 구성
                document = {
                    'date_news_trend': f"{today}_news_trend",  # 날짜별 필드
                    'category': category,
                    'word': word,
                    'count': count,
                    'trend_growth': trend_growth,
                    'period': period,
                    'ratio': ratio,
                    'related_articles': related_articles,
                    'upload_date': today  # 업로드 날짜
                }
                data.append(document)
                print(f"Uploading {word} for period {period} with ratio {ratio}")
                client.index(index=index_name, body=document)
            df = pd.DataFrame(data)
            df.to_sql('new_trend', con=engine, if_exists='replace', index=False)  # MySQL에 저장
    print(f"All data uploaded to OpenSearch index {index_name}.")

def run_pipeline_with_trends_and_upload():
    """뉴스 크롤링, 트렌드 분석 및 OpenSearch 업로드를 수행하는 파이프라인 실행."""
    categories = {
        "정치": 100,
        "경제": 101,
        "사회": 102,
        "생활문화": 103,
        "세계" : 104,
        "IT/과학" : 105
    }
    
    all_articles = {}
    
    for category_name, sid in categories.items():
        print(f"Fetching news for category: {category_name} (SID: {sid})")
        articles_data = fetch_news_by_category(sid)
        
        # Analyze articles and get word frequency and trends
        analysis_results = analyze_articles_with_trends(articles_data)
        
        all_articles[category_name] = analysis_results  # 분석 결과만 저장
    
    upload_to_opensearch(all_articles)  # OpenSearch에 데이터 업로드
    
    print("Pipeline completed successfully.")

# Airflow DAG 정의
dag = DAG(
    '09_news_trend_analysis_and_upload',
    description='News trend analysis and upload to OpenSearch',
    schedule_interval='0 8 * * *',  # 매일 오전 8시에 실행
    start_date=datetime(2024, 11, 18),
    catchup=False
)

# Airflow 작업 정의
run_pipeline_task = PythonOperator(
    task_id='run_pipeline_with_trends_and_upload',
    python_callable=run_pipeline_with_trends_and_upload,
    dag=dag
)