# Dockerfile
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

# Add curl installation
RUN apt-get update && apt-get install -y curl

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# # Start the FastAPI app and run the curl command
# CMD uvicorn main:app --host 0.0.0.0 --port 80 & \
#     sleep 3 && \
#     curl -L -g -X GET 'http://127.0.0.1:8000/atm/maintenance' && \
#     wait
