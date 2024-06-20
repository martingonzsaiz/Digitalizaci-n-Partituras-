FROM python:3.11-slim as base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    libtesseract-dev \
    tesseract-ocr \
    libfreetype6-dev \
    ghostscript \
    imagemagick \
    openjdk-17-jdk \
    dos2unix

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

FROM base as audiveris-builder
RUN git clone https://github.com/Audiveris/audiveris.git && \
    cd audiveris && \
    ./gradlew build

FROM base
COPY --from=audiveris-builder /app/audiveris /app/audiveris
RUN mkdir /app/audiveris_output
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY run_audiveris.sh /app/run_audiveris.sh
RUN dos2unix /app/run_audiveris.sh && chmod +x /app/run_audiveris.sh

EXPOSE 5000

CMD gunicorn -b :$PORT --timeout 300 "app:app"

