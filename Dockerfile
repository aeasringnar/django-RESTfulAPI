FROM ubuntu-18-env:v3
MAINTAINER Aeasringnar
WORKDIR /proj
COPY . .
RUN chmod +x server.sh
CMD ./server.sh start