#!/bin/bash
# Local development env vars 
export DEBUG='1'
export LOCAL_DEPLOY='1'

export DATABASE_NAME='pachatary_db'
export DATABASE_USER='pachatary_user'
export DATABASE_PASS='password'

export SECRET_KEY='39#j7n^$06yb=t-3u!-h(q)25sq&_2_hwq8zw@*r5p%tu=y1uj'
export CLIENT_SECRET_KEY='299d43b710b142b4bc7d5d62772acfa9'

export EMAIL_USE_TLS='1'
export EMAIL_HOST='smtp.example.com' 
export EMAIL_HOST_PASSWORD='my_secret_password'
export EMAIL_HOST_USER='user@example.com'
export EMAIL_HOST_ORIGIN='email@example.com'
export EMAIL_PORT='123'

export ANDROID_DEEPLINK_DOMAIN='app://local-pachatary.com'

export ELASTICSEARCH_URL='http://localhost:9200/'

export ANDROID_MIN_VERSION='0'

export PUBLIC_DOMAIN='pachatary.domain'

export REDIS_URL='redis://localhost:6379'

# Remote deployment extra env vars
# export HOST='domain.host.com'
# export AWS_ACCESS_KEY_ID='amazon_key'
# export AWS_SECRET_ACCESS_KEY='amazon_secret'
# export AWS_STORAGE_BUCKET_NAME='pachatary-bucket'
# export DATABASE_URL='postgres://amazonaws.com'
# export ROLLBAR_ACCESS_TOKEN='rollbar.com'
