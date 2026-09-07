FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY evals ./evals
COPY sample_data ./sample_data
EXPOSE 8000
CMD ["uvicorn", "support_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]

