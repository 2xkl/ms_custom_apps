FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends libffi-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --disable-pip-version-check --no-warn-script-location -r requirements.txt

COPY . .

RUN addgroup --system app && adduser --system --ingroup app app
USER app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
