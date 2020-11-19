FROM  python:3.7

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/lists/*

WORKDIR /home/sant/Desktop/backends/YoutubeArchive
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
