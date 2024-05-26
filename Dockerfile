# Используем базовый образ Python
FROM python:3.10.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


WORKDIR /app

#COPY requirements.txt /app/
#COPY build.sh /app/

RUN cp .env /app/ || cp default_env /app/.env

COPY . /app/

RUN rm *config_env || echo ''

#RUN pip install -r requirements.txt
RUN bash ./build.sh

EXPOSE 8000


CMD ["uvicorn", "app:init_app", "--host", "0.0.0.0", "--port", "8000"]
