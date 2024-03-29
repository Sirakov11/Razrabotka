FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip install --trusted-host pypi.python.org -r requirements1.txt

EXPOSE 5000

CMD ["python", "main.py"]