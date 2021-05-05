FROM tiangolo/uwsgi-nginx-flask:python3.8

RUN \
    # install ffmpeg
    apt-get update && \
    apt-get install -y ca-certificates ffmpeg python3-testresources && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/ && \
    # download pretrained models
    wget https://github.com/deezer/spleeter/releases/download/v1.4.0/5stems.tar.gz

COPY requirements.txt /app/requirements.txt

RUN pip3 install --no-cache-dir  -r requirements.txt

COPY . /app