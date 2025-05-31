FROM ubuntu:latest
LABEL authors="Intel"

ENTRYPOINT ["top", "-b"]