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

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    python manage.py compress --force && \
    python manage.py build_index --skip-checks

# EXPOSE 8000

RUN chmod +x /mysite/bin/docker_start.sh

ENTRYPOINT [ "/mysite/bin/docker_start.sh" ]
