FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY api_client.py .
COPY todo_UI_main.py .

# Expose Streamit's port
EXPOSE 8501

CMD ["streamlit", "run", "todo_UI_main.py", "--server.port=8501", "--server.address=0.0.0.0"]