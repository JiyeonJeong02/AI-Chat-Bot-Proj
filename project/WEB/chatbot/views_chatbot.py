from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pandas as pd
from openai import OpenAI
import urllib.parse
import requests
from bs4 import BeautifulSoup
from chatbot.sql import engine
from opensearchpy import OpenSearch
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenSearch(
    hosts = [{'host': os.getenv("OPENSEARCH_HOST"), 'port': os.getenv("OPENSEARCH_PORT")}]
)
openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 쿼리문 실행
def execute_query_to_dataframe(query):
    try:
        # pandas의 read_sql 함수를 사용하여 쿼리 실행 및 DataFrame 생성
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

table_query = """
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, TABLE_NAME
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'team5'
"""
result_df = execute_query_to_dataframe(table_query)

# 임베딩
def get_embedding(text):
    if not text:
        return None
    text = str(text).replace("\n", "")
    res = openai.embeddings.create(input=[text], model="text-embedding-3-small")
    embedding = res.data[0].embedding
    return embedding

## 쿼리문 짜기
# MySQL
def generate_query(query):
    # 필드 정보 추출
    table_info = result_df.groupby('TABLE_NAME').apply(
        lambda x: ", ".join(x['COLUMN_NAME'] + " (" + x['DATA_TYPE'] + ", 결측값: " + x['IS_NULLABLE'] + ")")
    ).to_dict()

    # 테이블 정보 포맷팅
    table_info_str = "\n".join([f"{table}: {columns}" for table, columns in table_info.items()])

    # 프롬프트 생성
    prompt = f"The database has the following tables and fields:\n{table_info_str}\nWrite an only MySQL query for the following question: {query}"

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an excellent MySQL query creator, Only Provide MySQL Query"},
            {"role": "user", "content": prompt}
        ]
    )
    
    generated_query = response.choices[0].message.content
    generated_query = generated_query.replace("```sql","").replace("```","").strip()
    return generated_query

# 법령데이터 OpenSearch 검색
def search_documents(query):
    query_embedding = get_embedding(query)
    index_name = 'korean_law_data'
    body = {
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, doc['embedding_vector']) + 1.0",
                    "params": {
                        "query_vector": get_embedding(query)
                    }
                }
            }
        },
        "size": 3
    }
    results = client.search(index=index_name, body=body)
    return [hit["_source"]['content'] for hit in results["hits"]["hits"]]

# new_trend 오픈서치 검색
def generate_opensearch_query(query) :
    index_name = 'new_trend'
    # 매핑정보 가져오기
    mapping = client.indices.get_mapping(index=index_name)
    # 필드 정보 추출
    fields = list(mapping[index_name]['mappings']['properties'].keys())
    fields_info = ", ".join(fields)
    # 프롬포트 생성
    prompt = f"The index {index_name} has the following fields : {fields_info}, Write an only OpenSearch query for the following question : {query}"
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an excellent OpenSearch query creator, Only Provide OpenSearch Query"},
            {"role": "user", "content": prompt}
        ]
    )
    generate_query = response.choices[0].message.content
    generate_query = generate_query.replace("```json","").replace("```","").strip()

    relevant_docs = client.search(
    index=index_name,
    body = generate_query)
    
    return relevant_docs


## POWER MODE 코드
# 위키피디아 검색
def get_wikipedia_content(keyword):
    try:
        encoded_keyword = urllib.parse.quote(keyword)
        url = f'https://ko.wikipedia.org/wiki/{encoded_keyword}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find('div', {'id': 'mw-content-text'})
        # print(content)
        if content:
            for unwanted in content.find_all(['script', 'style', 'sup', 'table']):
                unwanted.decompose()
            
            text = content.get_text(strip=True)
            text = ' '.join(text.split())
            
            return text[:1000]  # 컨텍스트 길이 제한
        
        return "내용을 찾을 수 없습니다."
        
    except Exception as e:
        return f"Wikipedia 검색 중 오류 발생: {str(e)}"
    
# 구글 검색
def extract_keywords(text):
    """사용자 메시지에서 핵심 키워드 추출"""
    prompt = f"""
    다음 텍스트에서 Wikipedia 검색에 사용할 핵심 키워드 1개만 추출해주세요.
    긴 문장이나 설명은 제외하고 명사형 키워드만 추출해주세요.
    
    텍스트: {text}
    
    키워드:"""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a keyword extraction expert. Extract only one main keyword in Korean."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50
    )
    
    keyword = response.choices[0].message.content.strip()
    return keyword

def get_google_search_content(keyword):
    try:
        # 구글 검색 URL 생성
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(keyword)}"
        
        # 헤더 설정
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        # 검색 결과 페이지 가져오기
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 검색 결과 추출 (구글 검색 결과의 스니펫)
        search_results = []
        for div in soup.find_all('div', class_=['VwiC3b', 'yXK7lf', 'MUxGbd', 'yDYNvb', 'lyLwlc']):
            if div.get_text(strip=True):
                search_results.append(div.get_text(strip=True))
        
        if not search_results:
            return "검색 결과를 찾을 수 없습니다."
        
        # 결과 합치기 (최대 1000자)
        combined_results = ' '.join(search_results)
        return combined_results[:1000]
        
    except requests.RequestException as e:
        return f"검색 요청 중 오류 발생: {str(e)}"
    except Exception as e:
        return f"검색 중 오류 발생: {str(e)}"


# 최종 응답
def answer_question_with_context(query, context=None):
    # Search for relevant documents
    # mysql
    search_query = generate_query(query)
    relevant_docs = execute_query_to_dataframe(search_query)
    
    # 오픈서치
    os_relevant_docs = search_documents(query)
    newtrend_docs = generate_opensearch_query(query)
    
    # 컨텍스트가 있는 경우와 없는 경우에 따라 프롬프트 구성
    context_text = f"\nAdditional context from Wikipedia:\n{context}" if context else ""
    
    prompt = f"""
    The following is a table of data extracted from an OpenSearch query:\n\n{os_relevant_docs}\n\n{relevant_docs}\n\n{newtrend_docs}\n 
    {context_text}\n
    Based on this data and context, provide an effective and detailed answer to the following natural language query: {query}
    
    Please follow these guidelines when answering:
    1. Provide accurate and concise answers based on both the data and Wikipedia context if available.
    2. Only mention information relevant to the question.
    3. If using Wikipedia information, integrate it naturally with the database information.
    4. Write your answer in Korean and keep it under 800 characters.
    
    Answer: """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Your name is 우대리, You are an excellent assistant proficient in data analysis"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800
    )
    return response.choices[0].message.content


# 대시보드 인사이트 요약 챗봇 (mini)
@csrf_exempt
def chatbot_response(request):
    # GET 및 POST 요청을 처리하여 대시보드와 챗봇의 인사이트 및 대화 기능을 제공
    if request.method == 'GET':
        # GET 요청 처리: 차트 데이터를 기반으로 인사이트 생성
        chart_id = request.GET.get('chartId')
        # chartId를 GET 파라미터로 받아서 차트 식별
        if chart_id:
            try:
                # OpenAI 클라이언트 초기화 및 인사이트 생성기 설정
                insight_generator = InsightGenerator(openai)
                
                # 차트 데이터 조회
                chart_data = insight_generator.get_chart_data(chart_id)
                
                if not chart_data or "No data available" in chart_data:
                    return JsonResponse({
                        'status': 'success',
                        'insight': '이 차트에 대한 데이터를 찾을 수 없습니다.'
                    })  # 데이터 없으면 기본 메세지 반환
                
                # 인사이트 생성
                insight = insight_generator.generate_chart_insight(chart_id, chart_data)
                # generate_chart_insight 메서드로 분석 및 인사이트 생성 (Json 형태로 반환)
                return JsonResponse({
                    'status': 'success',
                    'insight': insight
                })
                
            except Exception as e:
                print(f"Error generating insight: {str(e)}")  # 디버깅용
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=500)
    
    # POST 요청 처리 (기존 챗봇 대화)
    elif request.method == 'POST':
        # 사용자가 챗봇에 질문 던질때 답변 제공용
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            is_power_mode = data.get('isPowerMode', False)

            search_context = None
            if is_power_mode:
                keyword = extract_keywords(user_message)
                print(f"추출된 키워드: {keyword}")  # 디버깅용
                
                search_context = get_google_search_content(keyword)
                print(f"Google 검색 컨텍스트: {search_context[:100]}...")  # 디버깅용
            
            bot_response = f"우대리: {answer_question_with_context(user_message, search_context)}"
            
            return JsonResponse({
                'status': 'success',
                'response': bot_response
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'response': f'오류가 발생했습니다: {str(e)}'
            })
            
    return JsonResponse({'status': 'error'}, status=400)


class InsightGenerator:
    def __init__(self, openai_client):
        self.client = openai_client
        
    def get_chart_data(self, chart_id):
        """차트 ID에 따른 실제 데이터 조회"""
        try:            
            # 차트 ID별 쿼리 매핑
            query_map = {
                'bankrate_indicator_json': "SELECT bor FROM team5.korea_base_rate ORDER BY time DESC LIMIT 10",
                'K_GDP_indicator_json': "SELECT GDP FROM team5.korea_index ORDER BY TIME desc LIMIT 10",
                'K_cpi_indicator_json': "SELECT TOTAL FROM team5.cpi_data ORDER BY TIME DESC LIMIT 10",
                'K_pce_indicator_json': "SELECT DATA_VALUE FROM team5.pce_data ORDER BY TIME DESC LIMIT 10",
                'K_USD_indicator_json': "SELECT USD FROM team5.currency_rate ORDER BY TIME desc LIMIT 10",
                'K_growth_indicator_json': "SELECT 경제성장률 FROM korea_index ORDER BY TIME desc LIMIT 10",
                'economic_indicators_table_json': "WITH MaxDate AS (SELECT MAX(date) as latest_date FROM fred_data) SELECT * FROM fred_data WHERE date >= DATE_SUB((SELECT latest_date FROM MaxDate), INTERVAL 5 YEAR) AND date <= (SELECT latest_date FROM MaxDate) ORDER BY date ASC",
                'gdp_rates_json': "SELECT * FROM team5.gdp_rates ORDER BY date DESC LIMIT 10",
                'price_indicators_json': "SELECT * FROM team5.price_indicators ORDER BY date DESC LIMIT 10",
                'consumer_trends_json': "SELECT * FROM team5.consumer_trends ORDER BY date DESC LIMIT 10",
                'employment_trends_json': "SELECT * FROM team5.employment_trends ORDER BY date DESC LIMIT 10",
                'cpi_card_predict_json': "SELECT * FROM team5.cpi_card_predict ORDER BY date DESC LIMIT 10",
                'card_total_sales_ladar_json': "SELECT * FROM team5.card_sales ORDER BY date DESC LIMIT 10",
                'wooricard_sales_treemap_json': "SELECT * FROM team5.woori_card ORDER BY date DESC LIMIT 10",
                'gender_json': "SELECT * FROM team5.card_category_gender ORDER BY date DESC LIMIT 10",
                'create_card_heatmap_json': "SELECT * FROM team5.card_heatmap ORDER BY date DESC LIMIT 10",
                'tour_servey_json': "SELECT * FROM team5.tour_survey ORDER BY date DESC LIMIT 10",
                'travel_trend_line_json': "SELECT * FROM team5.travel_trend ORDER BY date DESC LIMIT 10",
                'currency_rates_json': "SELECT * FROM team5.currency_rates ORDER BY date DESC LIMIT 10",
                'visualize_travel_advice_json': "SELECT * FROM team5.travel_caution ORDER BY date DESC LIMIT 10"
            }
            
            if chart_id not in query_map:
                return "해당 차트의 데이터가 준비중입니다."
                
            df = pd.read_sql(query_map[chart_id], engine)
            engine.dispose()
            
            if df.empty:
                return "데이터가 없습니다."
                
            return df.to_string()
            
        except Exception as e:
            print(f"Error in get_chart_data: {str(e)}")
            return "분석 준비중입니다."
        
    def generate_chart_insight(self, chart_id, chart_data):
        """차트별 인사이트 생성"""
        # 차트별 컨텍스트 매핑
        context_map = {
            'bankrate_indicator_json': "금리 변동 추이",
            'K_GDP_indicator_json': "GDP 성장률 동향",
            'K_cpi_indicator_json': "소비자물가지수 변화",
            'K_pce_indicator_json': "개인소비지출 동향",
            'K_USD_indicator_json': "달러 환율 추이",
            'K_growth_indicator_json': "경제성장률 동향",
            'economic_indicators_table_json': "주요 경제지표 현황",
            'gdp_rates_json': "GDP 성장률 변화",
            'price_indicators_json': "물가 지표 변화",
            'consumer_trends_json': "소비자 동향 지표",
            'employment_trends_json': "고용 지표 변화",
            'cpi_card_predict_json': "물가와 카드 소비 연관성",
            'card_total_sales_ladar_json': "카드사별 총 매출 현황",
            'wooricard_sales_treemap_json': "우리카드 실제 매출 구조",
            'gender_json': "성별에 따른 카드 사용 패턴",
            'create_card_heatmap_json': "카드사별 세부 구성 비교",
            'tour_servey_json': "여행 관련 소비자 설문 결과",
            'travel_trend_line_json': "여행 트렌드 변화",
            'currency_rates_json': "주요 환율 동향",
            'visualize_travel_advice_json': "국가별 여행 주의 정보"
        }
        
        base_prompt = f"""
        다음은 {context_map.get(chart_id, '차트')}에 대한 최근 데이터입니다:
        {chart_data}
        
        다음 지침에 따라 데이터를 분석해주세요:

        1. 데이터 변화 요약 (15자 내외):
        - 최신 시간순으로 정렬된 데이터에서 가장 최근 값(현재)과 직전 값(이전)을 비교
        - 최신 시간순으로 정렬된 데이터에서 가장 변동성이 큰 값을 비교
        - 변화의 방향(증가/감소)과 크기를 정확히 파악
        - 최신 데이터와 변동성이 큰 데이터 중 더욱 변동성이 큰 값을 제시
        - 예시 형식: "이전 X에서 현재 Y로 증가/감소"
        - X와 Y 값의 적절한 단위(%, 원, 달러 등)를 추가하여 설명
        
        2. 카드 개발/마케팅 관점의 시사점 (20자 내외):
        - 관찰된 변화를 바탕으로 실질적인 전략 제시
        - 금리 변동이 소비자 행동에 미치는 영향 고려
        - 카드 상품 개발 및 마케팅 방향성 제안
        
        결과는 다음 형식으로 제시:
        [변화] (가장 최근 시점 기준으로 직전 대비 변화를 명시)
        [제안] (변화를 고려한 전략적 제안)
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a financial data analyst expert in card industry."},
                    {"role": "user", "content": base_prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return "분석 준비중입니다."