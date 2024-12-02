import pandas as pd
import plotly.graph_objects as go
from plotly.io import to_json
import plotly.express as px
import requests
from chatbot.sql import engine


    
def load_currency_forecast_from_sql():
    try:
        # MySQL 테이블을 DataFrame으로 읽어오기
        query = "SELECT TIME, USD, CNY, JPY, EUR, SOURCE FROM currency_forecast"
        currency_forecast = pd.read_sql(query, engine)

        return currency_forecast
        
    except Exception as e:
        print(f"데이터베이스에서 데이터를 불러오는 중 오류 발생: {str(e)}")
        return pd.DataFrame()    
    

def create_currency_view():
    """
    통화 환율 데이터를 기반으로 Plotly 그래프를 생성하는 함수.
    """
    combined_data = load_currency_forecast_from_sql()
    # Plotly 그래프 생성
    fig = go.Figure()

    # 통화 및 source 조합 생성
    currencies = ["USD", "CNY", "JPY", "EUR"]
    sources = combined_data['SOURCE'].unique()

    # SOURCE에 대한 한국어 매핑
    source_mapping = {
        "PREDICTION": "예측값",
        "REAL": "실제값",
        "FUTURE": "미래 예측값",
    }

    # 통화 및 source에 따라 각각의 라인 추가
    for currency in currencies:
        for source in sources:
            filtered_data = combined_data[combined_data['SOURCE'] == source]
            source_korean = source_mapping.get(source, source)  # 매핑에서 한국어 값 가져오기
            fig.add_trace(
                go.Scatter(
                    x=filtered_data['TIME'],
                    y=filtered_data[currency],
                    mode='lines',
                    name=f"{currency} ({source_korean})",  # 한국어로 설명된 source 사용
                    visible=(currency == "USD"),  # 초기에는 USD만 표시
                )
            )

    # 드롭다운 메뉴 생성
    dropdown_buttons = [
        {
            "label": currency,
            "method": "update",
            "args": [
                {
                    "visible": [
                        (currency == c) for c in currencies for _ in sources
                    ],  # 선택한 통화만 표시
                },
                {
                    "title": f"Currency Rates Over Time - {currency}",  # 제목 업데이트
                },
            ],
        }
        for currency in currencies
    ]

    # 레이아웃 설정
    fig.update_layout(
        updatemenus=[
            {
                "buttons": dropdown_buttons,
                "direction": "down",
                "showactive": True,
            }
        ],
        title="Currency Rates Over Time - USD",
        xaxis_title="Time",
        yaxis_title="Currency Value",
        template="plotly_white",
    )

    return to_json(fig)