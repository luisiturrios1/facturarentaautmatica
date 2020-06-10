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

EXPOSE 3031

CMD ["uwsgi", "--module", "alvisarrentas.wsgi:application", "--master", "--processes", "1", "--die-on-term", "--socket", "wsgi-server:3031"]
