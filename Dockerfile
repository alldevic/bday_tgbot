FROM alpine:3.11.3 AS build
ARG DEBUG
ARG SET_TZ
ARG CONTAINER_TIMEZONE
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /app && \
  apk add --no-cache python3 py3-psycopg2 tzdata openntpd && \
  if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
  apk add --no-cache --virtual .build-deps python3-dev gcc musl-dev postgresql-dev libressl-dev libffi-dev make && \
  pip3 install --disable-pip-version-check --no-cache-dir pipenv
WORKDIR /app
COPY Pipfile Pipfile.lock /app/

RUN if [[ "$DEBUG" == "TRUE" ]] || [[ "$DEBUG" == "True" ]] || [[ "$DEBUG" == "1" ]]; then \
  echo "Install with DEV packages"; \
  pipenv install --system --deploy --ignore-pipfile --dev; \
  pip3 uninstall pipenv virtualenv virtualenv-clone pip -y; \
  else \
  echo "Install only PROD packages"; \
  pip3 install --disable-pip-version-check --no-cache-dir gunicorn meinheld; \
  pipenv install --system --deploy --ignore-pipfile; \
  pip3 uninstall pipenv virtualenv virtualenv-clone pip -y; \
  fi && \
  apk --purge del .build-deps  && \
  rm -rf /root/.cache /root/.local \
  /etc/apk/ /usr/share/apk/ /lib/apk/ /sbin/apk \
  /media /usr/lib/terminfo /usr/share/terminfo \
  /usr/lib/python*/ensurepip \
  /usr/lib/python*/turtledemo /usr/lib/python*/turtle.py /usr/lib/python*/__pycache__/turtle.*  \
  /var/cache/apk \
  /var/lib/apk && \
  if [[ "$DEBUG" != "TRUE" ]] && [[ "$DEBUG" != "True" ]] && [[ "$DEBUG" != "1" ]]; then \
  find /usr/lib/python*/* | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf; \
  python3 -m compileall -b /usr/lib/python*; \
  find /usr/lib/python*/* -name "*.py"|xargs rm -rf; \
  find /usr/lib/python*/* -name '*.c' -delete; \
  find /usr/lib/python*/* -name '*.pxd' -delete; \
  find /usr/lib/python*/* -name '*.pyd' -delete; \
  find /usr/lib/python*/* -name '__pycache__' | xargs rm -r; \
  fi && \
  find /usr/lib/python*/site-packages/django/conf/locale ! -name __pycache__ ! -name __init__.py ! -name ru ! -name en -mindepth 1 -maxdepth 1  -type d -print0 | xargs -0 rm -rf && \
  find /usr/lib/python*/site-packages/django/contrib/admin/locale ! -name ru ! -name en* -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 rm -rf && \
  find /usr/lib/python*/site-packages/django/contrib/admindocs/locale ! -name ru ! -name en* -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 rm -rf  && \
  find /usr/lib/python*/site-packages/django/contrib/auth/locale ! -name ru ! -name en* -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 rm -rf  && \
  find /usr/lib/python*/site-packages/django/contrib/contenttypes/locale ! -name ru ! -name en* -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 rm -rf  && \
  find /usr/lib/python*/site-packages/django/contrib/flatpages/locale ! -name ru ! -name en* -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 rm -rf  && \
  find /usr/lib/python*/site-packages/django/contrib/gis/locale ! -name ru ! -name en* -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 rm -rf  && \
  find /usr/lib/python*/site-packages/django/contrib/humanize/locale ! -name ru ! -name en* -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 rm -rf  && \
  find /usr/lib/python*/site-packages/django/contrib/postgres/locale ! -name ru ! -name en* -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 rm -rf  && \
  find /usr/lib/python*/site-packages/django/contrib/redirects/locale ! -name ru ! -name en* -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 rm -rf  && \
  find /usr/lib/python*/site-packages/django/contrib/sessions/locale ! -name ru ! -name en* -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 rm -rf  && \
  find /usr/lib/python*/site-packages/django/contrib/sites/locale ! -name ru ! -name en* -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 rm -rf && \
  rm -rf /app/Pipfile* && \
  rm -rf /usr/lib/python*/site-packages/*.dist-info

RUN if [[ "$SET_TZ" = "True" ]]; then \
  cp /usr/share/zoneinfo/${CONTAINER_TIMEZONE} /etc/localtime; \
  echo "${CONTAINER_TIMEZONE}" >  /etc/timezone; \
  echo "Container timezone set to: $CONTAINER_TIMEZONE"; \
  else \
  echo "Container timezone not modified"; \
  fi

RUN rm -rf /usr/share/zoneinfo


FROM scratch AS deploy
ARG DEBUG
ENV PYTHONUNBUFFERED 1
ENV DEBUG ${DEBUG}
COPY --from=build / /
WORKDIR /app
