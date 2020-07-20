#!/bin/bash

stop_and_rm_if_exists() {
  container_name=$(docker ps -a --format='{{ .Names }}' | grep postgres)
  if [[ $? -eq 0 ]]; then
    docker stop $container_name && docker rm $container_name
  fi
}

run_postgres() {
  docker run -d --name postgres -e POSTGRES_PASSWORD=zopsedu  -e POSTGRES_USER=zopsedu -e POSTGRES_DB=zopsedu -p 5432:5432 postgres
}

upgrade_and_migrate() {
  flask db upgrade
  sleep 2
  flask db migrate
  sleep 2
  flask db upgrade
}

insert_data() {
  python fake_data.py all 10
  python manage.py insert_data

}


copy_butce_detaylari_file(){
   docker cp detayli_hesap_planlari.csv $(docker ps -a --format='{{ .Names }}' | grep postgres):/
}

insert_butce_detaylari() {
    docker container exec -i $(docker ps -a --format='{{ .Names }}' | grep postgres)  psql -U zopsedu -c "\copy detayli_hesap_planlari(id,parent_id,ana_hesap_hesap_grubu_yardimci_hesap_adi,kurum_adi,hesap_kodu,kurum_turu,saymanlik_kodu) FROM '/detayli_hesap_planlari.csv' DELIMITERS ';' CSV HEADER"
}

drop_birim_agaci(){
docker container exec -i  $(docker ps -a --format='{{ .Names }}' | grep postgres) psql  -U zopsedu -c "DROP TABLE birim CASCADE"
}

insert_birim_agaci(){
docker container exec -i  $(docker ps -a --format='{{ .Names }}' | grep postgres) psql  -U zopsedu zopsedu < birim.sql
}

main() {
  stop_and_rm_if_exists
  sleep 2
  run_postgres; sleep 3 &&  upgrade_and_migrate; sleep 2 && insert_data; sleep 2 && drop_birim_agaci; sleep 3 && insert_birim_agaci; sleep 2 && copy_butce_detaylari_file; sleep 2 && insert_butce_detaylari;
}

main


