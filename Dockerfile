FROM ubuntu-18-env:v3
MAINTAINER Aeasringnar
WORKDIR /proj
COPY . .
ENV LC_ALL=zh_CN.utf8
ENV LANG=zh_CN.utf8
ENV LANGUAGE=zh_CN.utf8
RUN pip install -r requirements.txt
RUN chmod +x server.sh
CMD ["./server.sh", "start"]
