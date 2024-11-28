# train.py

import numpy as np
import tensorflow as tf
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras import layers, models
from tensorflow.keras.layers import Input, Dense, LSTM, Conv1D, Dropout, Bidirectional, Multiply, Permute, Flatten
from tensorflow.keras.utils import get_custom_objects, register_keras_serializable, get_custom_objects
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split
# import yfinance as yf
from datetime import datetime
from tensorflow.keras.models import load_model
# from dotenv import load_dotenv
import os
import pymysql
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()

# 데이터베이스 연결 정보
username = os.getenv('sql_username')
password = os.getenv('sql_password')
host = os.getenv('sql_host')
port = os.getenv('sql_port')
database = 'team5'
engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")


@register_keras_serializable(package="Custom", name="attention_3d_block")
# Attention 블록 정의
def attention_3d_block(inputs):
    input_dim = int(inputs.shape[2])
    a = Dense(input_dim, activation='softmax')(inputs)
    a_probs = Permute((1, 2), name='attention_vec')(a)
    return Multiply()([inputs, a_probs])

# 사용자 정의 레이어 등록
get_custom_objects().update({"attention_3d_block": attention_3d_block})

# 모델 정의
@register_keras_serializable(package="Custom", name="attention_model")
def attention_model(input_dims, time_steps, lstm_units):
    inputs = Input(shape=(time_steps, input_dims))
    x = Conv1D(filters=64, kernel_size=1, activation='relu')(inputs)
    x = Dropout(0.1)(x)
    # Bidirectional 및 LSTM 정의
    lstm_out = Dropout(0.3)(Bidirectional(LSTM(lstm_units, return_sequences=True))(x))
    lstm_out2 = Dropout(0.3)(Bidirectional(LSTM(lstm_units, return_sequences=True))(lstm_out))
    attention_mul = Flatten()(attention_3d_block(lstm_out2))
    output = Dense(1, activation='linear')(attention_mul)
    return Model(inputs=[inputs], outputs=output)

# 사용자 정의 모델 등록
get_custom_objects().update({"attention_model": attention_model})

def load_data_from_sql():
    try:
        # MySQL 테이블을 DataFrame으로 읽어오기
        query = "SELECT TIME, USD, CNY,JPY, EUR  FROM currency_rate WHERE time >= '2012-01-01'"
        currency_rate = pd.read_sql(query, engine)

        return currency_rate

    except Exception as e:
        print(f"데이터베이스에서 데이터를 불러오는 중 오류 발생: {str(e)}")
        return pd.DataFrame()


# 결측값 처리
def fill_na_with_avg(df):
    return (df.ffill() + df.bfill()) / 2

# R^2 지표 정의
def r2_keras(y_true, y_pred):
    SS_res = tf.reduce_sum(tf.square(y_true - y_pred))
    SS_tot = tf.reduce_sum(tf.square(y_true - tf.reduce_mean(y_true)))
    return 1 - SS_res / (SS_tot + tf.keras.backend.epsilon())

# 학습 진행 상황 시각화 함수
def plot_training_history(history):
    plt.figure(figsize=(12, 6))
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Training Progress')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.show()

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

# 모델 학습 함수
def train_model(train_X, train_Y, input_dims, time_steps, lstm_units, model_path, epochs=20, batch_size=64):
    model = attention_model(input_dims, time_steps, lstm_units)
    model.compile(loss='mse', optimizer='adam', metrics=['mse'])
    model.fit(
        [train_X], train_Y,
        epochs=epochs, batch_size=batch_size, validation_split=0.25,
        callbacks=[
            EarlyStopping(monitor='val_loss', patience=10, mode='min'),
            ModelCheckpoint(model_path, monitor='val_loss', save_best_only=True, mode='min')
        ]
    )
    model.save(model_path)

# 모델 학습 함수 수정
def train_model_for_currency(train_X, train_Y, input_dims, time_steps, lstm_units, currency_code, epochs=20, batch_size=64):
    model = attention_model(input_dims, time_steps, lstm_units)
    model.compile(loss='mse', optimizer='adam', metrics=['mse'])
    history = model.fit(
        [train_X], train_Y,
        epochs=epochs, batch_size=batch_size, validation_split=0.25,
        callbacks=[
            EarlyStopping(monitor='val_loss', patience=10, mode='min'),
            ModelCheckpoint(f"./{currency_code}.h5", monitor='val_loss', save_best_only=True, mode='min')
        ]
    )
    model.save(f"./{currency_code}.h5")
    plot_training_history(history)
    return model

def save_model_for_tensorserving(model, currency_code, export_path='./models'):
    """
    Save the model in TensorFlow Serving format with proper versioning
    
    Args:
        model: Trained Keras model
        currency_code: Currency code used as model identifier
        export_path: Base directory for saving serving models
    """
    import os
    from datetime import datetime

    # Create export directory for the currency code
    currency_path = os.path.join(export_path, f"{currency_code}")
    os.makedirs(currency_path, exist_ok=True)

    # Find the next version number
    existing_versions = [int(d) for d in os.listdir(currency_path) if d.isdigit()]
    next_version = max(existing_versions) + 1 if existing_versions else 1

    # Create full model export path with version
    model_export_path = os.path.join(currency_path, str(next_version))
    os.makedirs(model_export_path, exist_ok=True)

    # Export model for TensorFlow Serving
    model.export(model_export_path)
    print(f"Model for {currency_code} saved in TensorFlow Serving format at: {model_export_path}")

def main():
    target_currencies = ['EUR']#['USD', 'CNY', 'JPY', 'EUR']
    exchange_df = load_data_from_sql()
    if exchange_df.empty:
        print("No data loaded. Exiting.")
        return

    exchange_df['TIME'] = pd.to_datetime(exchange_df['TIME'], errors='coerce')
    exchange_df = exchange_df.dropna().sort_values(by='TIME')
    exchange_df['USD'] = pd.to_numeric(exchange_df['USD'], errors='coerce')
    exchange_df['CNY'] = pd.to_numeric(exchange_df['CNY'], errors='coerce')
    exchange_df['JPY'] = pd.to_numeric(exchange_df['JPY'], errors='coerce')
    exchange_df['EUR'] = pd.to_numeric(exchange_df['EUR'], errors='coerce')

    TIME_STEPS = 60
    LSTM_UNITS = 64
    epochs = 20
    batch_size = 64

    # Create base directory for TensorFlow Serving models
    # os.makedirs('./tensorserving_models', exist_ok=True)

    for currency in target_currencies:
        if currency not in exchange_df.columns:
            print(f"{currency} 데이터가 없습니다. 건너뜁니다.")
            continue

        print(f"Processing {currency}...")

        # 해당 통화 데이터 선택 및 결측값 처리
        df = fill_na_with_avg(exchange_df[currency])
        df = np.array(df).reshape(-1, 1)
        df, normalize_params = normalize_mult(df)

        # 데이터셋 생성
        train_X, _ = create_dataset(df, TIME_STEPS)
        _, train_Y = create_dataset(df[:, 0].reshape(len(df), 1), TIME_STEPS)

        # 데이터 분리
        train_X, test_X, train_Y, test_Y = train_test_split(train_X, train_Y, test_size=0.2, random_state=42)

        # 모델 학습
        model = attention_model(1, TIME_STEPS, LSTM_UNITS)
        model.compile(loss='mse', optimizer='adam', metrics=['mse'])
        model.fit(
            [train_X], train_Y,
            epochs=epochs, batch_size=batch_size, validation_split=0.25,
            callbacks=[EarlyStopping(monitor='val_loss', patience=10, mode='min')]
        )

        # Save model in TensorFlow Serving format
        save_model_for_tensorserving(model, currency)
if __name__ == "__main__":
    main()

