FROM python:3.6.6-jessie

ENV LANG C.UTF-8
ENV TZ=Europe/Istanbul

RUN  apt-get update && apt-get install -y gcc musl-dev libpq-dev git libjpeg-dev zlib1g-dev libffi-dev libxml2-dev libxslt1-dev vim xfonts-75dpi xfonts-base 
RUN  wget https://downloads.wkhtmltopdf.org/0.12/0.12.5/wkhtmltox_0.12.5-1.jessie_amd64.deb && dpkg -i wkhtmltox_0.12.5-1.jessie_amd64.deb
RUN  pip3  install --upgrade virtualenv \
	&& virtualenv zopsedu-venv

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
