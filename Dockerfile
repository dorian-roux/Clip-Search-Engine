FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN echo "" > .streamlit/secret.toml
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip3 install -r requirements.txt

EXPOSE 8501

# Run
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]