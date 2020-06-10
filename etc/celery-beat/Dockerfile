FROM python:2.7.16

RUN curl -L -o wk.tar.xz https://downloads.wkhtmltopdf.org/0.12/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz \
    && tar xf wk.tar.xz \
    && cp wkhtmltox/bin/wkhtmltopdf /usr/bin \
    && cp wkhtmltox/bin/wkhtmltoimage /usr/bin \
    && rm wk.tar.xz \
    && rm -r wkhtmltox

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt

RUN ["pip", "install", "--no-cache-dir", "-r", "requirements.txt"]

COPY ./src /usr/src/app

CMD ["celery", "-A", "alvisarrentas", "beat", "-l", "info", "--scheduler", "django_celery_beat.schedulers:DatabaseScheduler"]