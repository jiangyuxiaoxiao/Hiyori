FROM python:3.10.12-bookworm
COPY ./Hiyori/Plugins /app/Hiyori/Plugins
COPY ./Hiyori/Utils /app/Hiyori/Utils
COPY ./Hiyori/Data /app/Hiyori/DockerStart
COPY ./Hiyori/.env /app/Hiyori/
COPY ./Hiyori/.env.prod /app/Hiyori/
COPY ./Hiyori/plugin.prod.json /app/Hiyori
COPY ./requirements.txt /app/Hiyori
COPY ./Hiyori/hiyori.py /app/Hiyori
# apt换源
COPY ./sources.list /etc/apt/sources.list
RUN apt-get update \
  && apt-get install ffmpeg libsm6 libxext6 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1:amd64 libxdamage-dev -y \
  && pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
  && pip install -r /app/Hiyori/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /app/Hiyori
EXPOSE 12200

CMD ["python", "hiyori.py"]

