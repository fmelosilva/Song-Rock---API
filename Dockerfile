FROM python:3.8

WORKDIR /app

COPY main.py requirements.txt ./

RUN \
    # install ffmpeg
    apt-get update && \
    apt-get install -y ffmpeg python3-testresources && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/ && \
    # download pretrained models
    wget https://github.com/deezer/spleeter/releases/download/v1.4.0/5stems.tar.gz

RUN pip3 install --no-cache-dir  -r requirements.txt

CMD [ "python", "main.py" ]