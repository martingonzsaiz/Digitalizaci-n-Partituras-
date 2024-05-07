FROM openjdk:17-jdk-slim-buster

RUN apt-get update && apt-get install -y \
    git \
    gradle \
    tesseract-ocr \
    libtesseract-dev \
    libfreetype6-dev \
    ghostscript \
    imagemagick \
    python3-pip  

RUN sed -i '/disable ghostscript format types/,+6d' /etc/ImageMagick-6/policy.xml

RUN pip3 install flask google-cloud-storage flask-login flask_sqlalchemy flask_migrate

COPY . /app

WORKDIR /app

EXPOSE 5000

CMD ["python3", "run.py"]
