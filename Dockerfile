FROM python:3.11-slim

RUN apt-get update && apt-get upgrade && apt-get install gcc libssl-dev pkg-config python3-dev default-libmysqlclient-dev -y && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai  /etc/localtime

RUN pip install --upgrade pip && \
    pip install poetry

WORKDIR /mysite

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry add gunicorn[gevent] && \
    poetry install --no-root --no-dev

COPY . .

RUN python manage.py makemigrations

RUN python manage.py migrate

RUN python manage.py collectstatic --noinput

RUN python manage.py compress --force

RUN python manage.py build_index --skip-checks

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# EXPOSE 8000

RUN chmod +x /mysite/bin/docker_start.sh

ENTRYPOINT [ "/mysite/bin/docker_start.sh" ]
