FROM python:3.10.12-bookworm
VOLUME /app/Hiyori/Data
COPY ./Hiyori/ /app/Hiyori/
COPY ./requirements.txt /app/Hiyori
# apt换源
COPY ./sources.list /etc/apt/sources.list
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1:amd64 libxdamage-dev -y
WORKDIR /app/Hiyori
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
EXPOSE 12200

CMD ["python", "hiyori.py"]

