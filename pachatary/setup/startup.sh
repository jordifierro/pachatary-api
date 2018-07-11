#!/bin/bash
source ../env/bin/activate
source ./pachatary/setup/envvars.sh
postgres -D /usr/local/var/postgres/ &
../env/elasticsearch-6.2.4/bin/elasticsearch &
../env/redis-4.0.10/src/redis-server &
python manage.py runserver &
