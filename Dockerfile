FROM python:3.9-alpine
LABEL MAINTAINER="Antonin GUILET <antonin.guilet-dupont@laposte.net>"
ENV PS1="\[\e[0;33m\]|> warhammer40k <| \[\e[1;35m\]\W\[\e[0m\] \[\e[0m\]# "

WORKDIR /src
COPY . /src
RUN pip install --no-cache-dir -r requirements.txt \
    && python setup.py install
WORKDIR /
ENTRYPOINT ["warhammer40k"]
