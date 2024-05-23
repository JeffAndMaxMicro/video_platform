# 使用官方 Python 映像作為基礎映像
FROM python:3.9-slim

# 安裝必要的系統依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

# 設置工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案文件到工作目錄
COPY . /app/

# 設置環境變量，告訴 Django 我們處於生產環境中
ENV DJANGO_SETTINGS_MODULE=videoPlateform.settings

# 暴露端口
EXPOSE 8000

# 啟動 Django 開發伺服器
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "videoPlateform.wsgi:application"]