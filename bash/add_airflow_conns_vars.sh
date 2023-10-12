#!/bin/sh

# run from /airflow dir

container_id=$(docker container ls | grep 'schedule' | awk '{print $1}')

echo $PWD

docker exec -i ${container_id} bash < connections.sh 



