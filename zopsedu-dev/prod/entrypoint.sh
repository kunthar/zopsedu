#!/bin/bash
. /zopsedu-venv/bin/activate
#git clone https://github.com/kunthar/zopsedu
pip install -r /zopsedu/requirements.txt
pip install gunicorn
export FLASK_APP=/zopsedu/zopsedu/server.py
export FLASK_CONFIGURATION=production
export POSTGRES_USER=zopsedu
export POSTGRES_PASSWORD=dombilililerle
export POSTGRES_HOST=172.24.0.11:5432
export POSTGRES_DB=zopsedu
export REDIS_HOST=172.24.0.10
ln -s /zopsedu/zopsedu /zopsedu-venv/lib/python3.6/site-packages/zopsedu

if [ $FIRST_RUN == 1 ]; then
  cd /zopsedu/zopsedu
  flask db upgrade
  python fake_data.py all 10
  python manage.py insert_data
  exit 0

else
#  GUNICORN_CMD_ARGS="--bind 0.0.0.0:5000 --keyfile /ssl/privkey.pem --certfile /ssl/cert.pem --workers=5 --log-level=debug --keep-alive=5" gunicorn zopsedu.server:app
  # GUNICORN_CMD_ARGS="--forwarded-allow-ips='192.168.121.110' --bind 0.0.0.0:5000 --keyfile /ssl/privkey.pem --certfile /ssl/cert.pem --ca-certs /ssl/chain.pem --workers=5 --log-level=debug --keep-alive=5" gunicorn zopsedu.server:app
   GUNICORN_CMD_ARGS="--bind 0.0.0.0:5000 --workers=5 --log-level=debug --keep-alive=5" gunicorn zopsedu.server:app
#  flask run --host 0.0.0.0 --port 5000
fi
