FROM python:3.8

COPY sources.list /etc/apt
RUN apt update && apt upgrade -y &&\ 
  apt install -y gcc g++ make vim net-tools python3-dev

WORKDIR /proj
COPY . .
ENV LC_ALL=zh_CN.utf8
ENV LANG=zh_CN.utf8
ENV LANGUAGE=zh_CN.utf8
ENV PIPURL "https://mirrors.aliyun.com/pypi/simple/"
RUN pip install -i ${PIPURL} -r requirements.txt
CMD ["gunicorn", "-c", "gunicorn_conf.py"]
