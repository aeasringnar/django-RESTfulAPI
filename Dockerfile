FROM python:3.7-alpine
MAINTAINER Aeasringnar
RUN echo http://mirrors.aliyun.com/alpine/v3.9/main > /etc/apk/repositories
RUN echo http://mirrors.aliyun.com/alpine/v3.9/community >> /etc/apk/repositories
RUN apk update
RUN apk --update add --no-cache gcc
RUN apk --update add --no-cache g++
RUN apk --update add --no-cache tzdata
RUN apk --update add --no-cache libffi-dev
RUN apk --update add --no-cache libxslt-dev
RUN apk --update add --no-cache jpeg-dev
ENV TIME_ZONE Asia/Shanghai
ENV PIPURL "https://pypi.tuna.tsinghua.edu.cn/simple"

RUN echo "${TIME_ZONE}" > /etc/timezone
RUN ln -sf /usr/share/zoneinfo/${TIME_ZONE} /etc/localtime

WORKDIR /projects

COPY . .

RUN pip --no-cache-dir install  -i ${PIPURL} --upgrade pip

