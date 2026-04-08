FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml /app/pyproject.toml
COPY server /app/server
COPY data /app/data
COPY artifacts /app/artifacts
COPY inference.py /app/inference.py
COPY final_real_evaluation.py /app/final_real_evaluation.py
COPY openenv.yaml /app/openenv.yaml
COPY README.md /app/README.md

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
