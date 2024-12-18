import os
from dotenv import load_dotenv
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from fredapi import Fred
import pymysql
from sqlalchemy import create_engine

load_dotenv()


FRED_API_KEY = os.getenv('FRED_API_KEY')
username = os.getenv('sql_username')
password = os.getenv('sql_password')
host = os.getenv('sql_host')
port = os.getenv('sql_port')
engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/team5")


fred = Fred(api_key=FRED_API_KEY)

# 현재 날짜를 end_date로 사용
end_date = datetime.today() - timedelta(days=1)

# 데이터 가져오기 함수
def fetch_data(series_id, start_date=(end_date - timedelta(days=1)), end_date=end_date):
    try:
        data = fred.get_series(series_id, observation_start=start_date, observation_end=end_date)
        return data
    except ValueError as e:
        print(f"Error fetching data for {series_id}: {e}")
        return None

# 데이터프레임 생성 함수
def make_df():
    data_frames = {
        'FFTR': fetch_data('DFEDTARU'),
        'GDP': fetch_data('GDP'),
        'GDP Growth Rate': fetch_data('A191RL1Q225SBEA'),
        'PCE': fetch_data('PCE'),
        'Core PCE': fetch_data('PCEPILFE'),
        'CPI': fetch_data('CPIAUCSL'),
        'Core CPI': fetch_data('CPILFESL'),
        'Personal Income': fetch_data('PI'),
        'Unemployment Rate': fetch_data('UNRATE'),
        'ISM Manufacturing': fetch_data('MANEMP'),
        'Durable Goods Orders': fetch_data('DGORDER'),
        'Building Permits': fetch_data('PERMIT'),
        'Retail Sales': fetch_data('RSAFS'),
        'Consumer Sentiment': fetch_data('UMCSENT'),
        'Nonfarm Payrolls': fetch_data('PAYEMS'),
        'JOLTS Hires': fetch_data('JTSHIL')
    }

    df = pd.DataFrame()
    for key, value in data_frames.items():
        if value is not None:
            temp_df = value.reset_index()
            temp_df.columns = ['date', key]
            if df.empty:
                df = temp_df
            else:
                df = pd.merge(df, temp_df, on='date', how='outer')
    
    df.sort_values(by='date', inplace=True)
    df.fillna(method='ffill', inplace=True)
    return df


def upload_data() :
    df = make_df()

    df.to_sql('fred_data', con=engine, if_exists='append', index=False)



# Airflow DAG 정의
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2015, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    '01_Fred_Data',
    default_args=default_args,
    description="미 연준 데이터를 업로드 합니다.",
    schedule_interval='@daily',
    start_date=datetime(2015, 1, 1),
    catchup=False,
    tags=['Opensearch', 'fred', 'data']
) as dag :
    t1 = PythonOperator(
        task_id='create_index_and_mapping',
        python_callable=upload_data
    )
    
    t1