FROM apache/airflow:2.5.1-python3.8

# root 사용자로 필요한 시스템 패키지 설치
USER root
RUN apt-get update && \
    apt-get install -y fonts-nanum && \
    apt-get install -y build-essential default-libmysqlclient-dev openjdk-17-jre pkg-config && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Java 환경 변수 설정
ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64
ENV PATH $JAVA_HOME/bin:$PATH

# airflow 사용자로 변경
USER airflow

# 필요한 Python 패키지 설치
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade \
    yfinance \
    pandas \
    numpy \
    oauth2client \
    gspread \
    mysqlclient \
    fredapi \
    PublicDataReader \
    elasticsearch \
    eland \
    prophet==1.1.6 \
    plotly \
    dash \
    konlpy \
    wordcloud \
    gensim \
    openai \
    sklearn \
    opensearch-py \
    protobuf==3.20.*

RUN pip install --no-cache-dir --upgrade \
    opensearch-py-ml \
    pytrends

RUN pip install --no-cache-dir --upgrade \
    keras==2.11.0 \
    tensorflow==2.11.0 \
    pymysql==1.0.2 \
    sqlalchemy==1.4.25 \
    selenium

RUN pip install --no-cache-dir --upgrade \
    nltk \ 
    torch \
    shapely \
    transformers

RUN pip install scikit-learn

# Airflow 웹 서버 시작
CMD ["airflow", "webserver"]