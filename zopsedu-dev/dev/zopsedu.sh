set -x
#find /home/zopsedu/zopsedu -not -iwholename '*.git*' -not -iwholename '*.jpg*' -mmin 1 | grep zopsedu
latest_commit_from_file=$(cat /home/zopsedu/latest_commit)
cd /home/zopsedu/zopsedu
latest_commit=$(git rev-parse HEAD)

if [ $latest_commit_from_file != $latest_commit ]; then
  sudo docker-compose -f /home/zopsedu/zopsedu-dev/docker-compose.yml stop redis
  sleep 2
  sudo docker-compose -f /home/zopsedu/zopsedu-dev/docker-compose.yml stop db
  sleep 2
  sudo docker-compose -f /home/zopsedu/zopsedu-dev/docker-compose.yml stop zopsedu
  sleep 2
  sudo docker-compose -f /home/zopsedu/zopsedu-dev/docker-compose.yml stop zopsedu_db_operations
  sleep 5
  sleep 10
  sudo docker-compose -f /home/zopsedu/zopsedu-dev/docker-compose.yml rm -f redis
  sleep 5
  sudo docker-compose -f /home/zopsedu/zopsedu-dev/docker-compose.yml rm -f db
  sleep 5
  sudo docker-compose -f /home/zopsedu/zopsedu-dev/docker-compose.yml rm -f zopsedu
  sleep 5
  sudo docker-compose -f /home/zopsedu/zopsedu-dev/docker-compose.yml rm -f zopsedu_db_operations
  sleep 5
  sudo docker-compose -f /home/zopsedu/zopsedu-dev/docker-compose.yml up -d redis
  sleep 10
  sudo docker-compose -f /home/zopsedu/zopsedu-dev/docker-compose.yml up -d db
  sleep 15
  sudo docker-compose -f /home/zopsedu/zopsedu-dev/docker-compose.yml up -d zopsedu_db_operations
  sleep 30 
  sudo docker-compose -f /home/zopsedu/zopsedu-dev/docker-compose.yml up -d zopsedu
fi

echo $latest_commit > /root/latest_commit
set +x
