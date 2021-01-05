FROM debian:stable-slim

RUN apt update \
    && apt install -y wget bzip2 git make python3 \
    && wget -qO- http://shyboy.oss-cn-shenzhen.aliyuncs.com/readonly/tc32_gcc_v2.0.tar.bz2 | tar xvjf - -C /opt/ \
    && git clone --depth 1 https://github.com/Ai-Thinker-Open/Telink_825X_SDK /sdk \
    && apt remove -y wget bzip2 \
    && rm -rf /var/lib/apt/lists/*

ENV PATH $PATH:/opt/tc32/bin
ENV TEL_PATH /sdk

WORKDIR /code
