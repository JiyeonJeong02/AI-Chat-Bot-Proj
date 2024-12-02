# 데이터 로드 및 전처리 함수
import pandas as pd
from plotly.io import to_json
import plotly.express as px
from chatbot.sql import engine


def load_data_from_sql():
    try:
        # MySQL 테이블을 DataFrame으로 읽어오기
        query = "SELECT * FROM tour_intrst"
        tour_intrst = pd.read_sql(query, engine)
        
        return tour_intrst
        
    except Exception as e:
        print(f"데이터베이스에서 데이터를 불러오는 중 오류 발생: {str(e)}")
        return pd.DataFrame()

def df_rename():
    df = load_data_from_sql()
    column_mapping = {
    "CHINA_TOUR_INTRST_VALUE": "중국",
    "JP_TOUR_INTRST_VALUE": "일본",
    "HONGKONG_MACAU_TOUR_INTRST_VALUE": "홍콩마카오",
    "SEASIA_TOUR_INTRST_VALUE": "동남아시아",
    "MDLEST_SWASIA_TOUR_INTRST_VALUE": "중동서남아시아",
    "USA_CANADA_TOUR_INTRST_VALUE": "미국캐나다",
    "SAMRC_LAMRC_TOUR_INTRST_VALUE": "남미중남미",
    "WEURP_NEURP_TOUR_INTRST_VALUE": "서유럽북유럽",
    "EEURP_TOUR_INTRST_VALUE": "동유럽",
    "SEURP_TOUR_INTRST_VALUE": "남유럽",
    "SPCPC_TOUR_INTRST_VALUE": "남태평양",
    "AFRICA_TOUR_INTRST_VALUE": "아프리카",
    }

    # 컬럼명 변경
    df.rename(columns=column_mapping, inplace=True)
    return df

def tour_servey():
    df = df_rename()
    # 긴 형식으로 변환
    melted = df.melt(
        id_vars=["RESPOND_ID", "SEXDSTN_FLAG_CD", "AGRDE_FLAG_NM"],
        value_vars=[
            '중국', '일본', '홍콩마카오', '동남아시아', '중동서남아시아',
            '미국캐나다', '남미중남미', '서유럽북유럽', '동유럽', '남유럽',
            '남태평양', '아프리카'],
        var_name="Region",
        value_name="Interest Change",
    )

    # 관심 변화 수준 순서 강제 적용
    desired_order = ["많이 적어졌다", "약간 적어졌다", "예전과 비슷하다", "약간 커졌다", "많이 커졌다"]
    melted["Interest Change"] = pd.Categorical(melted["Interest Change"], categories=desired_order, ordered=True)
    melted = melted.sort_values("Interest Change")

    # 기본 그래프 생성
    fig = px.bar(
        melted,
        x="Region",
        color="Interest Change",
        # title="여행 관심 변화",
        labels={"Region": "지역", "value": "빈도", "Interest Change": "관심 변화 수준"},
        barmode="stack",  # 누적 막대그래프
    )

    # 필터링 옵션 정의
    sexes = melted["SEXDSTN_FLAG_CD"].unique()
    ages = melted["AGRDE_FLAG_NM"].unique()

    # 버튼 생성
    buttons = []
    for sex in [None] + list(sexes):
        for age in [None] + list(ages):
            label = f"{sex or '전체 성별'}-{age or '전체 연령대'}"
            filtered_data = melted[
                ((melted["SEXDSTN_FLAG_CD"] == sex) | (sex is None)) &
                ((melted["AGRDE_FLAG_NM"] == age) | (age is None))
            ]
            buttons.append(dict(
                args=[{
                    'x': [filtered_data["Region"]],
                    'y': [filtered_data["Interest Change"]],
                    'title': f"{sex or '전체 성별'}, {age or '전체 연령대'}의 여행 관심 변화"
                }],
                label=label,
                method="update"
            ))

    # 버튼 메뉴 추가
    fig.update_layout(
        updatemenus=[{
            'buttons': buttons,
            'direction': 'down',
            'showactive': True,
            'x': 1.3,
            'y': 1.2
        }],
        margin={"r":0, "t":0, "l":0, "b":0}
    )

    return to_json(fig)