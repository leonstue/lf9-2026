FROM python:3.15

WORKDIR /app

RUN pip install --no-cache-dir flask

COPY src/ ./src/

EXPOSE 5000

CMD ["flask", "--app", "src/list_server.py", "run", "--host=0.0.0.0", "--port=5000"]
