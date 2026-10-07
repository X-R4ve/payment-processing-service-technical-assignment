FROM python:3.14.7-slim
COPY requirements.txt .
RUN pip install --upgrade pip --retries 10 --timeout 50 && \
    pip install -r requirements.txt --retries 10 --timeout 50
COPY alembic.ini .
COPY app app
CMD ["uvicorn", "app.main:payment_processing_service_app", "--host", "0.0.0.0", "--port", "8000"]
