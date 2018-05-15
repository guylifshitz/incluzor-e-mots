#!/bin/sh
set -e

cd /code/incluzor-e-mots

until psql $DATABASE_URL -c '\l'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing"

if [ "x$DJANGO_MANAGEPY_MIGRATE" = 'xon' ]; then
    /venv/bin/python3 manage.py migrate --noinput
fi

if [ ! -f /code/.build ]; then
  echo "Collecting statics files"
  /venv/bin/python3 manage.py collectstatic --noinput
  date > /code/.build
fi

exec "$@"
