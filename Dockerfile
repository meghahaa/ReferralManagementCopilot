FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY requirements.txt pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt \
    && python -m pip install --no-deps -e .

COPY data ./data
COPY docs ./docs
COPY evals ./evals
COPY evidence ./evidence
COPY scripts ./scripts
COPY tests ./tests
COPY ui ./ui
COPY .env.example ./

RUN chown -R app:app /app
USER app

EXPOSE 8501

CMD ["streamlit", "run", "ui/app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
