#! /usr/bin/env sh

set -o errexit
set -o pipefail
cmd="$@"

function postgres_ready(){
python3 << END
import sys
import psycopg2
import environ
try:
    env = environ.Env()
    dbname = env.str('POSTGRES_DB')
    user = env.str('POSTGRES_USER')
    password = env.str('POSTGRES_PASSWORD')
    host = 'postgres_db'
    port = 5432
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing..."

>&2 echo "Migrating..."
python3 manage.py migrate

>&2 echo "Collect static..."
python3 manage.py collectstatic --noinput


if [[ ${DEBUG} == 'TRUE' ]] || [[ ${DEBUG} == 'True' ]] || [[ ${DEBUG} == '1' ]]
then
  >&2 echo "Starting debug server..."
  exec python3 manage.py runserver 0.0.0.0:8000
else
    >&2 echo "Starting Gunicorn..."
    exec gunicorn bday_tgbot.wsgi:application \
      -k egg:meinheld#gunicorn_worker \
      --name bday_tgbot \
      --bind 0.0.0.0:8000 \
      --workers 3 \
      "$@"
fi