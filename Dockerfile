FROM ubuntu-18-env:v3
MAINTAINER Aeasringnar
WORKDIR /proj
COPY . .
ENV LC_ALL=zh_CN.utf8
ENV LANG=zh_CN.utf8
ENV LANGUAGE=zh_CN.utf8
ENV PIPURL "https://mirrors.aliyun.com/pypi/simple/"
RUN pip install -i ${PIPURL} -r requirements.txt
RUN chmod +x server.sh
RUN chmod +x docker_start.sh
CMD ["./docker_start.sh", "8000", "dev"]
