from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from train import normalize_mult, create_dataset, FNormalizeMult, fill_na_with_avg
import requests
import pymysql
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()

# 데이터베이스 연결 정보
username = os.getenv('sql_username')
password = os.getenv('sql_password')
host = os.getenv('sql_host')
port = os.getenv('sql_port')
database = 'team5'
engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")

# 데이터베이스에서 데이터를 로드하는 함수
def load_data_from_sql():
    try:
        query = "SELECT TIME, USD, CNY, JPY, EUR FROM currency_rate WHERE time >= '2012-01-01'"
        currency_rate = pd.read_sql(query, engine)
        return currency_rate
    except Exception as e:
        print(f"데이터베이스에서 데이터를 불러오는 중 오류 발생: {str(e)}")
        return pd.DataFrame()

# REST API를 통해 TensorFlow Serving 모델에서 예측값을 가져오는 함수
def fetch_predictions_from_model(url, input_data):
    """
    TensorFlow Serving 모델에서 예측값을 가져오는 함수.

    :param url: 모델 REST API URL
    :param input_data: 모델에 전달할 데이터 (numpy 배열 형태)
    :return: 예측값 (numpy 배열 형태)
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "instances": input_data.tolist()  # numpy 배열을 리스트로 변환
    }
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        predictions = response.json()["predictions"]
        return np.array(predictions)  # numpy 배열로 변환
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# 모델 평가 및 시각화 함수
def evaluate_model(model_url, test_X, test_Y, normalize, currency):
    predictions = fetch_predictions_from_model(model_url, test_X)
    if predictions is None:
        print(f"Failed to fetch predictions for {currency}")
        return None
    
    predictions = FNormalizeMult(predictions, normalize)
    r2 = r2_score(test_Y, predictions)
    print(f"Currency: {currency}, R^2 Score: {r2}")

    # 실제값과 예측값을 그래프로 시각화
    plt.figure(figsize=(12, 6))
    plt.plot(test_Y, label="Actual Values")
    plt.plot(predictions, label="Predicted Values")
    plt.xlabel("Time Steps")
    plt.ylabel("Values")
    plt.title(f"Actual vs Predicted Values for {currency}")
    plt.legend()
    plt.show()

    return predictions

# 테스트 데이터를 준비하는 함수
def prepare_test_data(test_data, time_steps, normalize):
    test, _ = normalize_mult(test_data)  # test_data는 이미 numpy 배열 형태
    test_X, test_Y = create_dataset(test, time_steps)
    test_Y = FNormalizeMult(test_Y, normalize)
    return test_X, test_Y

# 테스트를 위한 메인 함수
def main():
    TIME_STEPS = 60
    target_currencies = ['USD', 'CNY', 'JPY', 'EUR']

    # 데이터베이스에서 환율 데이터 불러오기
    exchange_df = load_data_from_sql()
    if exchange_df.empty:
        print("No data loaded. Exiting.")
        return

    # 데이터 전처리
    exchange_df['TIME'] = pd.to_datetime(exchange_df['TIME'], errors='coerce')
    exchange_df = exchange_df.dropna().sort_values(by='TIME')  # Drop rows with NaT or NaN
    exchange_df['USD'] = pd.to_numeric(exchange_df['USD'], errors='coerce')  # 숫자로 변환
    exchange_df['CNY'] = pd.to_numeric(exchange_df['CNY'], errors='coerce')  # 숫자로 변환
    exchange_df['JPY'] = pd.to_numeric(exchange_df['JPY'], errors='coerce')  # 숫자로 변환
    exchange_df['EUR'] = pd.to_numeric(exchange_df['EUR'], errors='coerce')  # 숫자로 변환

    # 각 target currency에 대해 반복
    for currency in target_currencies:
        print(f"Evaluating for currency: {currency}")

        # 모델 REST API URL 설정
        MODEL_URL = f'http://localhost:8501/v1/models/{currency}:predict'

        # 해당 통화의 데이터 가져오기 및 결측치 처리
        df = fill_na_with_avg(exchange_df[currency])

        # 데이터 정규화
        df = np.array(df).reshape(-1, 1)
        df, normalize = normalize_mult(df)

        # 테스트 데이터 준비
        test_index = int(len(df) * 0.8)
        _, test = df[:test_index], df[test_index:]
        test_X, test_Y = prepare_test_data(test, TIME_STEPS, normalize)

        # 모델 평가 및 결과 시각화
        predictions = evaluate_model(MODEL_URL, test_X, test_Y, normalize, currency)

if __name__ == "__main__":
    main()
