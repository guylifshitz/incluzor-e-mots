FROM python:3.6-jessie

ENV DATABASE_URL postgres://postgres:password@guylifshitz.com:5433/incluzore_mots

env DATABASE_NAME incluzore_mots
env DATABASE_USER postgres
env DATABASE_PASSWORD password
env DATABASE_HOST guylifshitz.com
env DATABASE_PORT 5433

# Copy in your requirements file
ADD requirements.txt /requirements.txt

# Install build deps, then run `pip3 install`, then remove unneeded build deps all in a single step. Correct the path to your production requirements file, if needed.
RUN python3 -m venv /venv \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "/venv/bin/pip3 install --no-cache-dir -r /requirements.txt" \
    && apt-get update \
    && apt-get install -y postgresql-client

# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
RUN mkdir /code/
WORKDIR /code/
ADD . /code/

# uWSGI will listen on this port
EXPOSE 8001

# Add any custom, static environment variables needed by Django or your settings file here:
ENV DJANGO_SETTINGS_MODULE=incluzor_site.settings

# uWSGI configuration (customize as needed):
ENV UWSGI_VIRTUALENV=/venv UWSGI_WSGI_FILE=incluzor_site/wsgi.py UWSGI_HTTP=:8000 UWSGI_MASTER=1 UWSGI_WORKERS=2 UWSGI_THREADS=8 UWSGI_UID=1000 UWSGI_GID=2000 UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy

# Call collectstatic (customize the following line with the minimal environment variables needed for manage.py to run):
#RUN DATABASE_URL=none /venv/bin/python3 manage.py collectstatic --noinput

# Start uWSGI
RUN chmod +x /code/docker-entrypoint.sh
ENTRYPOINT ["/code/docker-entrypoint.sh"]

CMD ["/venv/bin/uwsgi", "--http-auto-chunked", "--http-keepalive"]
