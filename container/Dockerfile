FROM python:3.11.5-alpine
WORKDIR /app

COPY ./app /app
RUN pip install --upgrade pip
RUN pip install --upgrade --no-cache-dir --requirement requirements.txt

ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=2001

EXPOSE 2001
CMD ["uvicorn", "main:app"]