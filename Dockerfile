FROM python:3.9-alpine
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY Pipfile /app/
COPY Pipfile.lock /app/

RUN apk add --update --no-cache freetype-dev \
                                fribidi-dev \
                                harfbuzz-dev \
                                jpeg-dev \
                                lcms2-dev \
                                openjpeg-dev \
                                tcl-dev \
                                tiff-dev \
                                tk-dev \
                                zlib-dev

#RUN apk add --update --no-cache --virtual .tmp-build-deps \
RUN apk add --update --no-cache \
      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev \
      python3-dev libffi-dev openssl-dev cargo

RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --deploy
RUN pip install gunicorn

#RUN apk del .tmp-build-deps

COPY . /app/