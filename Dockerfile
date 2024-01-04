FROM python:3.11
WORKDIR /code
ENV PYTHONUNBUFFERED = 1
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8000
COPY . .
CMD ["python", "manage.py","runserver"]