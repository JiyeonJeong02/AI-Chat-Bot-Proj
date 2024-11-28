from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import tensorflow as tf
import yfinance as yf
# from tensorflow.keras.models import load_model
from airflow import DAG
from airflow.operators.python import PythonOperator
from dotenv import load_dotenv
import os
import pymysql
from sqlalchemy import create_engine
import requests

load_dotenv()

# 데이터베이스 연결 정보
username = os.getenv('sql_username')
password = os.getenv('sql_password')
host = os.getenv('sql_host')
port = os.getenv('sql_port')
database = 'team5'
engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")

def load_data_from_sql():
    try:
        # MySQL 테이블을 DataFrame으로 읽어오기
        query = "SELECT TIME, USD, CNY, JPY, EUR FROM currency_rate WHERE time >= '2012-01-01'"
        currency_rate = pd.read_sql(query, engine)
        
        return currency_rate
        
    except Exception as e:
        print(f"데이터베이스에서 데이터를 불러오는 중 오류 발생: {str(e)}")
        return pd.DataFrame()

# 데이터셋 생성
def create_dataset(dataset, look_back):
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back - 1):
        dataX.append(dataset[i:(i + look_back), :])
        dataY.append(dataset[i + look_back, :])
    return np.array(dataX), np.array(dataY)


# 데이터 정규화
def normalize_mult(data):
    normalize = np.zeros((data.shape[1], 2), dtype='float64')
    for i in range(data.shape[1]):
        listlow, listhigh = np.percentile(data[:, i], [0, 60])
        normalize[i, :] = [listlow, listhigh]
        delta = listhigh - listlow
        if delta != 0:
            data[:, i] = (data[:, i] - listlow) / delta
    return data, normalize

# 역정규화 함수
def FNormalizeMult(data, normalize):
    for i in range(data.shape[1]):
        delta = normalize[i, 1] - normalize[i, 0]
        if delta != 0:
            data[:, i] = data[:, i] * delta + normalize[i, 0]
    return data



# 결측값 처리
def fill_na_with_avg(df):
    return (df.ffill() + df.bfill()) / 2

# 테스트 데이터를 준비하는 함수
def prepare_test_data(test_data, time_steps, normalize):
    test, _ = normalize_mult(test_data)  # test_data는 이미 numpy 배열 형태
    test_X, test_Y = create_dataset(test, time_steps)
    test_Y = FNormalizeMult(test_Y, normalize)
    return test_X, test_Y

# 미래 예측 함수
def predict_future(model_url, last_sequence, future_steps, normalize):
    future_predictions = []
    current_sequence = last_sequence.copy()

    for _ in range(future_steps):
        # Use API call to fetch prediction
        prediction = fetch_predictions_from_model(model_url, current_sequence[np.newaxis, :, :])[0, 0]
        # Denormalize prediction
        denormalized_prediction = prediction * (normalize[0, 1] - normalize[0, 0]) + normalize[0, 0]
        future_predictions.append(denormalized_prediction)

        # Update the sequence
        current_sequence = np.roll(current_sequence, -1, axis=0)
        current_sequence[-1, 0] = prediction  # Append the new prediction to the sequence

    return np.array(future_predictions)


def evaluate_model(model_url, test_X, test_Y, normalize, currency, future_steps, test_time):
    predictions = fetch_predictions_from_model(model_url, test_X)
    predictions = np.array(list(predictions))

    # Generate predictions for test data
    # predictions = model.predict(test_X)
    predictions = FNormalizeMult(predictions, normalize).flatten()  # Flatten to 1D array
    test_Y = test_Y.flatten()  # Flatten to 1D array

    # Ensure test_time matches test_Y
    test_time = test_time[:len(test_Y)]  # Truncate test_time to match test_Y length

    # Future Predictions
    last_sequence = test_X[-1]
    future_predictions = predict_future(model_url, last_sequence, future_steps, normalize)

    # Generate future time axis
    future_time = pd.date_range(test_time[-1], periods=future_steps + 1, freq='D')[1:]

    # Create DataFrame for test results (predictions)
    test_pred_df = pd.DataFrame({
        'TIME': test_time,
        currency: predictions,
        'SOURCE': 'PREDICTION'
    })

    # Create DataFrame for test results (real values)
    test_real_df = pd.DataFrame({
        'TIME': test_time,
        currency: test_Y,
        'SOURCE': 'REAL'
    })

    # Combine test prediction and real results
    test_combined_df = pd.concat([test_pred_df, test_real_df], ignore_index=True)

    # Create DataFrame for future predictions
    future_df = pd.DataFrame({
        'TIME': future_time,
        currency: future_predictions,
        'SOURCE': 'FUTURE'
    })

    # Combine all results
    combined_df = pd.concat([test_combined_df, future_df], ignore_index=True)



    return combined_df

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
    
    
def run_prediction_and_upload():
    TIME_STEPS = 60
    FUTURE_STEPS = 60  # Number of future days to predict

    target_currencies = ['USD', 'CNY', 'JPY', 'EUR']
    exchange_df = load_data_from_sql()
    if exchange_df.empty:
        print("No data loaded. Exiting.")
        return

    exchange_df['TIME'] = pd.to_datetime(exchange_df['TIME'], errors='coerce')
    exchange_df = exchange_df.dropna().sort_values(by='TIME')  # Drop rows with NaT or NaN
    exchange_df['USD'] = pd.to_numeric(exchange_df['USD'], errors='coerce')  # 숫자로 변환
    exchange_df['CNY'] = pd.to_numeric(exchange_df['CNY'], errors='coerce')  # 숫자로 변환
    exchange_df['JPY'] = pd.to_numeric(exchange_df['JPY'], errors='coerce')  # 숫자로 변환
    exchange_df['EUR'] = pd.to_numeric(exchange_df['EUR'], errors='coerce')  # 숫자로 변환

    results_list = []

    # 각 target currency에 대해 반복
    for currency in target_currencies:
        print(f"Evaluating for currency: {currency}")

        model_url = f"http://host.docker.internal:8501/v1/models/{currency}:predict"

        # 해당 통화의 데이터 가져오기 및 결측치 처리
        df = fill_na_with_avg(exchange_df[currency])
        timestamps = exchange_df['TIME'].values

        # 데이터 정규화
        df = np.array(df).reshape(-1, 1)
        df, normalize = normalize_mult(df)

        # 테스트 데이터 준비
        test_index = int(len(df) * 0.8)
        _, test = df[:test_index], df[test_index:]
        _, test_time = timestamps[:test_index], timestamps[test_index:]
        test_X, test_Y = prepare_test_data(test, TIME_STEPS, normalize)

        # 모델 평가 및 결과 저장
        combined_df = evaluate_model(model_url, test_X, test_Y, normalize, currency, FUTURE_STEPS, test_time)

        # Append to results
        results_list.append(combined_df)

    # Combine all currency results
    final_df = pd.concat(results_list, axis=1)

    # Ensure columns are named correctly
    final_df = final_df.loc[:, ~final_df.columns.duplicated()]
    final_df = final_df.rename(columns={col: col if col in ['TIME', 'SOURCE'] else col.split('_')[-1] for col in final_df.columns})

    # Save to CSV
    # final_df.to_csv('currency_predictions.csv', index=False)
    final_df.to_sql('currency_forecast', con=engine, if_exists='replace', index=False)
    print("Results saved to 'currency_forecast.csv'.")

# Airflow DAG definition
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 5,
    'retry_delay': timedelta(hours=1),
}

with DAG(
    '05_Currency_Forecast',
    default_args=default_args,
    description='Predicts future currency exchange rates and uploads to MySQL daily',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    
    upload_task = PythonOperator(
        task_id='run_prediction_and_upload',
        python_callable=run_prediction_and_upload
    )

    upload_task
