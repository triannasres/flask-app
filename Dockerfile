FROM python:3.9.6

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

CMD ["python", "app.py"]
