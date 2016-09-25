FROM python:3.5.1
RUN groupadd -r trulii && adduser --disabled-password --system --group  trulii
RUN apt-get update && apt-get install gdal-bin -y --fix-missing
RUN mkdir /app/
ADD ./requirements.txt /app/
WORKDIR /app/
RUN pip install -r requirements.txt
ADD . .

# Installing cron
RUN apt-get update && apt-get install cron -y
RUN touch /var/log/cron.log
RUN chmod a+x crontab
ADD crontab /var/spool/cron/crontabs/

ENV GOSU_VERSION 1.7
RUN set -x \
    && wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture)" \
    && wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture).asc" \
    && export GNUPGHOME="$(mktemp -d)" \
    && gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 \
    && gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu \
    && rm -r "$GNUPGHOME" /usr/local/bin/gosu.asc \
    && chmod +x /usr/local/bin/gosu \
    && gosu nobody true