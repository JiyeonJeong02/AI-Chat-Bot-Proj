# Create your views here.
import plotly.graph_objs as go
from plotly.io import to_json
import pandas as pd
from django.conf import settings  # settings.py의 경로 설정 사용
from sqlalchemy import create_engine


def load_wooricard_data():
    try:
        # MySQL 연결 문자열 생성
        db_settings = settings.DATABASES['default']
        connection_string = f"mysql+pymysql://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
        
        # SQLAlchemy 엔진 생성
        engine = create_engine(connection_string)
        
        # MySQL 테이블을 DataFrame으로 읽어오기
        query = "SELECT * FROM edu_data_f_cleaned"
        data = pd.read_sql(query, engine)
        
        return data
        
    except Exception as e:
        print(f"데이터베이스에서 데이터를 불러오는 중 오류 발생: {str(e)}")
        return pd.DataFrame()  # 오류 발생 시 빈 DataFrame 반환

data = load_wooricard_data()

def load_cpi_card_data():
    try:
        # MySQL 연결 문자열 생성
        db_settings = settings.DATABASES['default']
        connection_string = f"mysql+pymysql://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
        
        # SQLAlchemy 엔진 생성
        engine = create_engine(connection_string)
        
        # MySQL 테이블을 DataFrame으로 읽어오기
        query = "SELECT * FROM cpi_card_data"
        data = pd.read_sql(query, engine)
        
        return data
        
    except Exception as e:
        print(f"데이터베이스에서 데이터를 불러오는 중 오류 발생: {str(e)}")
        return pd.DataFrame()  # 오류 발생 시 빈 DataFrame 반환

def top10_level_view():
    
    # if data.empty:  # 데이터가 비었을 경우
    #     return render(request, "dashboard_hoseop.html", {"error_message": "CSV 데이터를 불러올 수 없습니다."})
    
    # 각 회원 등급별로 이용 금액이 높은 항목 상위 10개 선택
    top10_level_categories = data.groupby('회원등급')[data.columns[9:]].mean().apply(lambda x: x.nlargest(10), axis=1)

    # Plotly 그래프 생성
    fig = go.Figure()

    # 각 회원 등급별로 데이터 추가
    for level in data['회원등급'].unique():
        fig.add_trace(
            go.Scatter(
                x=top10_level_categories.columns,  # 카테고리 (x축)
                y=top10_level_categories.loc[level],  # 평균 소비 금액 (y축)
                mode="lines+markers",
                name=f'Level {level}',  # 회원 등급 이름
                text=top10_level_categories.loc[level],  # Hover 텍스트
                hoverinfo="text+name+x+y",  # Hover 정보 표시
                marker=dict(size=10),  # 점 크기 설정
                line=dict(width=2),  # 선 두께 설정
            )
        )

    # 레이아웃 설정
    fig.update_layout(
        xaxis=dict(title="Categories", tickangle=45),  # x축 제목 및 각도 설정
        yaxis=dict(title="Average Spending"),  # y축 제목
        legend=dict(title="Membership Level"),  # 범례 제목
        template="plotly_white",  # 그래프 스타일
        margin=dict(l=50, r=50, t=50, b=100),  # 여백 설정
    )

    # 그래프를 HTML로 변환
    return to_json(fig)

def lifestage_distribution_view():

    # if data.empty:  # 데이터가 비었을 경우
    #     return render(request, "dashboard_hoseop.html", {"error_message": "CSV 데이터를 불러올 수 없습니다."})

    # 회원등급 및 라이프스테이지 분포 카운트
    life_stage_distribution = data.groupby(['회원등급', '라이프스테이지']).size().unstack(fill_value=0)

    # Plotly 그래프 생성
    fig = go.Figure()

    # 각 라이프스테이지별로 데이터 추가
    for life_stage in life_stage_distribution.columns:
        fig.add_trace(
            go.Bar(
                x=life_stage_distribution.index,  # 회원 등급 (x축)
                y=life_stage_distribution[life_stage],  # 각 회원 등급에 따른 라이프스테이지 수 (y축)
                name=life_stage,  # 라이프스테이지 이름
                hoverinfo="name+x+y",  # Hover 정보 표시
            )
        )

    # 레이아웃 설정
    fig.update_layout(
        barmode='group',  # 막대 그래프를 쌓아 표시
        xaxis=dict(title="Membership Level"),  # x축 제목 설정
        yaxis=dict(title="Count"),  # y축 제목 설정
        legend=dict(title="Life Stage"),  # 범례 제목 설정
        template="plotly_white",  # 그래프 스타일
        margin=dict(l=50, r=50, t=50, b=100),  # 여백 설정
    )

    # 그래프를 HTML로 변환
    return to_json(fig)

def age_and_life_stage_distribution_view():

    # if data.empty:  # 데이터가 비었을 경우
    #     return render(request, "dashboard_hoseop.html", {"error_message": "CSV 데이터를 불러올 수 없습니다."})

    # 거주 지역별 연령대 분포 카운트
    age_distribution = data.groupby(['거주지역_1', '연령대']).size().unstack(fill_value=0)

    # Plotly 그래프 생성 (연령대 분포)
    fig_age = go.Figure()

    # 각 연령대별로 데이터 추가
    for age_group in age_distribution.columns:
        fig_age.add_trace(
            go.Bar(
                x=age_distribution.index,  # 거주 지역 (x축)
                y=age_distribution[age_group],  # 각 거주 지역에 따른 연령대 수 (y축)
                name=str(age_group),  # 연령대 이름
                hoverinfo="name+x+y",  # Hover 정보 표시
            )
        )

    # 연령대 분포 그래프 레이아웃 설정
    fig_age.update_layout(
        barmode='group',  # 막대 그래프를 나란히 표시
        xaxis=dict(title="Residence Area", tickangle=-45),  # x축 제목 및 각도 설정
        yaxis=dict(title="Count"),  # y축 제목 설정
        legend=dict(title="Age Group", x=1.05),  # 범례 제목 및 위치 설정
        template="plotly_white",  # 그래프 스타일
        margin=dict(l=50, r=150, t=50, b=100),  # 여백 설정
    )

    # 거주 지역별 라이프 스테이지 분포 카운트
    life_stage_distribution = data.groupby(['거주지역_1', '라이프스테이지']).size().unstack(fill_value=0)

    # Plotly 그래프 생성 (라이프 스테이지 분포)
    fig_life_stage = go.Figure()

    # 각 라이프 스테이지별로 데이터 추가
    for life_stage in life_stage_distribution.columns:
        fig_life_stage.add_trace(
            go.Bar(
                x=life_stage_distribution.index,  # 거주 지역 (x축)
                y=life_stage_distribution[life_stage],  # 각 거주 지역에 따른 라이프 스테이지 수 (y축)
                name=life_stage,  # 라이프 스테이지 이름
                text=life_stage_distribution[life_stage],  # Hover 텍스트
                hoverinfo="text+name+x+y",  # Hover 정보 표시
            )
        )

    # 라이프 스테이지 분포 그래프 레이아웃 설정
    fig_life_stage.update_layout(
        barmode='group',  # 막대 그래프를 나란히 표시
        xaxis=dict(title="Residence Area", tickangle=-45),  # x축 제목 및 각도 설정
        yaxis=dict(title="Count"),  # y축 제목 설정
        legend=dict(title="Life Stage", x=1.05),  # 범례 제목 및 위치 설정
        template="plotly_white",  # 그래프 스타일
        margin=dict(l=50, r=150, t=50, b=100),  # 여백 설정
    )

    # 두 개의 그래프를 HTML로 변환 및 리턴
    return to_json(fig_age), to_json(fig_life_stage)

def gender_expense_distribution_view():
    
    # if data.empty:  # 데이터가 비었을 경우
    #     return render(request, "dashboard_hoseop.html", {"error_message": "CSV 데이터를 불러올 수 없습니다."})

    # 남성과 여성의 소비 카테고리 합계를 각각 계산
    male_expense = data[data['성별'] == '남자'].loc[:, '가전/가구/주방용품':'학원'].sum().nlargest(10)
    female_expense = data[data['성별'] == '여자'].loc[:, '가전/가구/주방용품':'학원'].sum().nlargest(10)

    # Plotly 그래프 생성 (두 개의 파이 차트)
    fig_male = go.Figure()
    fig_female = go.Figure()

    # 남성 소비 카테고리 파이 차트 추가
    fig_male.add_trace(go.Pie(
        labels=male_expense.index,
        values=male_expense.values,
        name='남성 소비 유형',
        hole=0.3,  # 도넛형 파이 차트
        hoverinfo='label+value',
    ))

    # 여성 소비 카테고리 파이 차트 추가
    fig_female.add_trace(go.Pie(
        labels=female_expense.index,
        values=female_expense.values,
        name='여성 소비 유형',
        hole=0.3,
        hoverinfo='label+value',
    ))

    # 남성 차트 레이아웃 설정
    fig_male.update_layout(
        showlegend=True, # 스타일 설정
        template="plotly_white"  # 스타일 설정
    )

    # 여성 차트 레이아웃 설정
    fig_female.update_layout(
        showlegend=True,
        template="plotly_white"
    )

    return to_json(fig_male), to_json(fig_female)

def gender_view():

    # 전체, 남성, 여성의 소비 카테고리 합계를 각각 계산
    total_expense = data.loc[:, '가전/가구/주방용품':'학원'].sum().nlargest(10)
    male_expense = data[data['성별'] == '남자'].loc[:, '가전/가구/주방용품':'학원'].sum().nlargest(10)
    female_expense = data[data['성별'] == '여자'].loc[:, '가전/가구/주방용품':'학원'].sum().nlargest(10)

    # Figure 생성
    fig = go.Figure()

    # 전체 소비 카테고리 파이 차트 (초기 보이는 상태)
    fig.add_trace(go.Pie(
        labels=total_expense.index,
        values=total_expense.values,
        name='전체 소비 유형',
        hole=0.3,
        visible=True,
        hoverinfo='label+value',
        textinfo='none'  # 텍스트 표시 제거
    ))

    # 남성 소비 카테고리 파이 차트 (초기 숨김 상태)
    fig.add_trace(go.Pie(
        labels=male_expense.index,
        values=male_expense.values,
        name='남성 소비 유형',
        hole=0.3,
        visible=False,
        hoverinfo='label+value',
        textinfo='none'  # 텍스트 표시 제거
    ))

    # 여성 소비 카테고리 파이 차트 (초기 숨김 상태)
    fig.add_trace(go.Pie(
        labels=female_expense.index,
        values=female_expense.values,
        name='여성 소비 유형',
        hole=0.3,
        visible=False,
        hoverinfo='label+value',
        textinfo='none'  # 텍스트 표시 제거
    ))

    # 버튼 생성
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.5,
                y=1.5,
                showactive=True,
                buttons=list([
                    dict(label="전체",
                         method="update",
                         args=[{"visible": [True, False, False]}],
                         ),
                    dict(label="남성",
                         method="update",
                         args=[{"visible": [False, True, False]}],
                         ),
                    dict(label="여성",
                         method="update",
                         args=[{"visible": [False, False, True]}]
                         )
                ]),
            )
        ]
    )

    # 레이아웃 설정
    fig.update_layout(
        showlegend=True,
        template="plotly_white",
        # height=400,
        legend=dict(
            x=0,        
            y=0,        
            xanchor='left',
            yanchor='top',
            orientation='h',
        )
    )

    return to_json(fig)

def age_payment_distribution_view():

    # if data.empty:  # 데이터가 비었을 경우
    #     return render(request, "dashboard_hoseop.html", {"error_message": "CSV 데이터를 불러올 수 없습니다."})

    # 연령대별 신용카드 및 체크카드 사용 금액 합계 계산
    age_payment = data.groupby('연령대')[['신용카드이용금액', '체크카드이용금액']].sum().reset_index()

    # Plotly 그래프 생성
    fig = go.Figure()

    # 신용카드 이용금액 막대 추가
    fig.add_trace(go.Bar(
        x=age_payment['연령대'],
        y=age_payment['신용카드이용금액'],
        name='신용카드이용금액',
        marker_color='mediumseagreen',
        hoverinfo='x+y'  # 마우스 오버 시 x축, y축
    ))

    # 체크카드 이용금액 막대 추가
    fig.add_trace(go.Bar(
        x=age_payment['연령대'],
        y=age_payment['체크카드이용금액'],
        name='체크카드이용금액',
        marker_color='coral',
        hoverinfo='x+y'  # 마우스 오버 시 x축, y축
    ))

    # 레이아웃 설정
    fig.update_layout(
        barmode='group',  # 막대를 나란히 배치
        xaxis=dict(title='연령대'),
        yaxis=dict(title='이용 금액 (단위: 원)'),
        legend=dict(title='결제 방식'),
        template='plotly_white',  # 배경 스타일 설정
        margin=dict(l=50, r=150, t=50, b=100),
        color_discrete_sequence = 'Plotly'
    )

    # 그래프를 HTML로 변환 후 리턴
    return to_json(fig)

def age_category_top5_view():

    # # if data.empty:  # 데이터가 비었을 경우
    # #     return render(request, "dashboard_hoseop.html", {"error_message": "CSV 데이터를 불러올 수 없습니다."})

    # # 연령대별 소비 카테고리 합계 계산
    # age_category = data.groupby('연령대').sum().loc[:, '가전/가구/주방용품':'학원']  # 소비 카테고리 컬럼 이름에 맞게 수정

    # # 상위 5개 카테고리를 선택하기 위해 melt 후 연령대별로 정렬
    # age_category_melted = age_category.reset_index().melt(id_vars='연령대', var_name='소비 카테고리', value_name='이용 금액')
    # top_categories = age_category_melted.groupby('연령대').apply(lambda x: x.nlargest(5, '이용 금액')).reset_index(drop=True)

    # Step 1: 연령대별 소비 카테고리 합계 계산
    category_columns = data.loc[:, '가전/가구/주방용품':'학원']
    age_category = data.groupby('연령대')[category_columns.columns].sum()

    # Step 2: 각 연령대별로 상위 5개의 카테고리 선택
    top_categories = pd.DataFrame()

    for age_group, row in age_category.iterrows():
        # 각 연령대에서 상위 5개의 카테고리 선택
        top_5 = row.nlargest(5).index.tolist()  # 상위 5개의 카테고리 이름
        top_5_values = row.nlargest(5).values.tolist()  # 상위 5개의 금액
        temp_df = pd.DataFrame({
            '연령대': [age_group] * 5,
            '소비 카테고리': top_5,
            '이용 금액': top_5_values
        })
        top_categories = pd.concat([top_categories, temp_df])

    # Plotly 그래프 생성
    fig = go.Figure()

    # 각 연령대별로 상위 5개 소비 카테고리의 데이터를 추가
    for category in top_categories['소비 카테고리'].unique():
        category_data = top_categories[top_categories['소비 카테고리'] == category]
        fig.add_trace(go.Bar(
            x=category_data['연령대'],
            y=category_data['이용 금액'],
            name=category,
            hoverinfo='x+y+name',  # 마우스 오버 시 값 표시
        ))

    # 레이아웃 설정
    fig.update_layout(
        barmode='group',  # 막대를 나란히 배치
        xaxis=dict(title='연령대'),
        yaxis=dict(title='총 이용 금액 (단위: 원)'),
        legend=dict(title='소비 카테고리'),
        template='plotly_white',  # 배경 스타일 설정
    )

    # 그래프를 HTML로 변환 후 리턴
    return to_json(fig)

def cpi_card_predict_view():

    """
    드롭다운으로 카테고리를 선택하여 PCE 및 CPI 데이터를 시각화하는 Plotly 그래프 생성 함수.
    오른쪽 y축에 CPI 값을 표시하고, 신뢰구간 내부를 옅은 색으로 채웁니다.
    """

    data = load_cpi_card_data()

    try:
        # 카테고리 정의
        categories = [
            '합계', '식료품', '의류/잡화', '연료', '가구/가전', '의료/보건', '여행/교통',
            '오락/문화', '교육', '숙박/음식', '공과금/개인 및 전문 서비스'
        ]

        # 기본 그래프 객체 생성
        fig = go.Figure()

        # 드롭다운 버튼 데이터 생성
        buttons = []
        for i, category in enumerate(categories):
            # 컬럼명 설정
            pce_pred = f"{category}_PCE_pred"
            pce_lower = f"{category}_PCE_lower"
            pce_upper = f"{category}_PCE_upper"
            cpi_pred = f"{category}_CPI_pred"
            cpi_lower = f"{category}_CPI_lower"
            cpi_upper = f"{category}_CPI_upper"

            # PCE 신뢰구간 및 예측값 trace 추가
            fig.add_trace(go.Scatter(
                x=data['TIME'], y=data[pce_upper],
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip',
                visible=(i == 0)  # 첫 번째 카테고리만 표시
            ))
            fig.add_trace(go.Scatter(
                x=data['TIME'], y=data[pce_lower],
                mode='lines',
                fill='tonexty',
                fillcolor='rgba(0, 0, 255, 0.2)',  # 옅은 파란색
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip',
                visible=(i == 0)
            ))
            fig.add_trace(go.Scatter(
                x=data['TIME'], y=data[pce_pred],
                mode='lines',
                name=f"{category} PCE",
                line=dict(color='blue'),
                visible=(i == 0)
            ))

            # CPI 신뢰구간 및 예측값 trace 추가
            fig.add_trace(go.Scatter(
                x=data['TIME'], y=data[cpi_upper],
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip',
                visible=(i == 0),
                yaxis="y2"  # 오른쪽 y축 사용
            ))
            fig.add_trace(go.Scatter(
                x=data['TIME'], y=data[cpi_lower],
                mode='lines',
                fill='tonexty',
                fillcolor='rgba(255, 165, 0, 0.2)',  # 옅은 주황색
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip',
                visible=(i == 0),
                yaxis="y2"  # 오른쪽 y축 사용
            ))
            fig.add_trace(go.Scatter(
                x=data['TIME'], y=data[cpi_pred],
                mode='lines',
                name=f"{category} CPI",
                line=dict(color='orange'),
                visible=(i == 0),
                yaxis="y2"  # 오른쪽 y축 사용
            ))

            # 버튼 생성
            visibility = [False] * len(categories) * 6  # 총 trace 수
            for j in range(i * 6, (i + 1) * 6):
                visibility[j] = True  # 해당 카테고리 trace만 활성화
            buttons.append(dict(
                label=category,
                method="update",
                args=[{"visible": visibility}, {"title": f"{category} PCE 및 CPI 예측 시계열 데이터"}]
            ))

        # 레이아웃 설정
        fig.update_layout(
            # title=f"{categories[0]} PCE 및 CPI 예측 시계열 데이터",
            xaxis=dict(title="시간"),
            yaxis=dict(title="PCE 지출", titlefont=dict(color="blue"), tickfont=dict(color="blue")),
            yaxis2=dict(
                title="CPI 지수",
                titlefont=dict(color="orange"),
                tickfont=dict(color="orange"),
                overlaying="y",
                side="right"
            ),
            updatemenus=[{
                "buttons": buttons,
                "direction": "down",
                "showactive": True,
                "x": 1.15,
                "y": 1.15,
            }],
            legend=dict(x=0.5, y=1.2, orientation="h"),
            template="plotly_white",
        )

        # HTML로 변환
        return to_json(fig)
    
    except Exception as e:
        print(f"그래프 생성 중 오류 발생: {e}")
        return None