#!/bin/bash
psql -c "CREATE USER pachatary_user WITH PASSWORD 'password';"
psql -c "CREATE DATABASE pachatary_db WITH OWNER pachatary_user;"
psql -c "ALTER USER pachatary_user CREATEDB;"
