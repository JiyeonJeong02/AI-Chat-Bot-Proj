import pandas as pd
import plotly.express as px
from plotly.io import to_json
import pycountry
import requests
from bs4 import BeautifulSoup
from chatbot.sql import engine


def load_data_from_sql():
    try:
        # MySQL 테이블을 DataFrame으로 읽어오기
        query = "SELECT * FROM travel_caution"
        travel_caution = pd.read_sql(query, engine)

        return travel_caution
        
    except Exception as e:
        print(f"데이터베이스에서 데이터를 불러오는 중 오류 발생: {str(e)}")
        return pd.DataFrame()

# 웹 스크래핑 함수
def fetch_data():
    url = "https://www.0404.go.kr/dev/country.mofa?idx=&hash=&chkvalue=no1&stext=&group_idx="
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    data = []
    countries = soup.select("ul.country_list > li")

    for country in countries:
        country_name = country.select_one("a").text.strip()
        img_tags = country.select("img")
        travel_advice = [img["alt"].strip() for img in img_tags if img.get("alt")]
        travel_advice = ", ".join(travel_advice) if travel_advice else "정보 없음"
        data.append([country_name, travel_advice])

    return pd.DataFrame(data, columns=["Country", "Travel_Advice"])

# 위험 수준 계산 함수
def get_risk_level(advice):
    if '여행금지' in advice:
        return 4
    elif '출국권고' in advice:
        return 3
    elif '여행자제' in advice:
        return 2
    elif '여행유의' in advice:
        return 1
    else:
        return 0

# 데이터 병합 및 처리 함수
def merge_and_process_data():
    web_data = fetch_data()
    sql_data = load_data_from_sql()
    
    if 'Country' not in sql_data.columns and 'Country_EN' in sql_data.columns:
        sql_data['Country'] = sql_data['Country_EN']
    
    merged_df = pd.merge(web_data, sql_data, on='Country', how='outer')
    
    def get_iso_code(country_name):
        try:
            if pd.isnull(country_name):
                return None
            country = pycountry.countries.search_fuzzy(country_name)
            return country[0].alpha_3 if country else None
        except LookupError:
            return None

    merged_df['ISO_Alpha_3'] = merged_df['Country_EN'].apply(get_iso_code)
    merged_df['Risk_level'] = merged_df['Travel_Advice'].apply(get_risk_level)
    
    return merged_df

# 시각화 함수

def visualize_travel_advice():
    df = merge_and_process_data()
    if df.empty:
        print("경고: 시각화할 데이터가 없습니다.")
        return None

    # 위험 수준별 고정 색상 설정
    color_map = {
        "안전": "#FEF3E2",           # 부드러운 초록색
        "여행유의": "#FFB200",          # 연한 살구색
        "여행자제": "#EB5B00",         # 밝은 주황색
        "출국권고": "#D91656",  # 강렬한 빨간색
        "여행금지": "#640D5F"        # 딥 블루
    }

    # 색상 맵핑을 위해 'Risk_level'을 범주형 문자열로 변환
    risk_mapping = {
        0: "안전",
        1: "여행유의",
        2: "여행자제",
        3: "출국권고",
        4: "여행금지"
    }
    df['Risk_level_str'] = df['Risk_level'].map(risk_mapping)

    # 데이터가 범주형인지 확인
    df['Risk_level_str'] = pd.Categorical(df['Risk_level_str'], categories=color_map.keys())

    fig = px.choropleth(df,
                        locations='ISO_Alpha_3',
                        color='Risk_level_str',
                        hover_name='Country',
                        color_discrete_map=color_map,  # 고정 색상
                        height=400)

    fig.update_geos(projection_type="natural earth", 
                    showcountries=True, 
                    countrycolor="Gray",
                    showframe=False,
                    showcoastlines=True)
    
    # 범례를 그래프 아래 한 줄로 배치
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=50),  # 아래 여백 추가
        legend=dict(
            orientation="h",  # 수평 방향
            yanchor="bottom",  # 아래 정렬
            y=-0.2,           # 그래프 아래로 위치 이동
            xanchor="center", # 중앙 정렬
            x=0.5             # 그래프 중심에 배치
        ),
        legend_title_text="여행 위험 수준"  # 범례 제목 추가
    )

    return to_json(fig)