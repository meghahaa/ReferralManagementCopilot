.DEFAULT_GOAL := test
PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

.PHONY: install install-dev validate index evaluate test evidence demo run ui docker-build docker-run clean

install:
	$(PIP) install -r requirements.txt
	$(PIP) install --no-deps -e .

install-dev: install

validate:
	$(PYTHON) scripts/seed_data.py

index:
	$(PYTHON) scripts/index_rag.py

evaluate:
	$(PYTHON) evals/eval_pipeline.py

test:
	$(PYTHON) -m pytest tests/ -v

evidence:
	$(PYTHON) scripts/generate_evidence.py

demo:
	$(PYTHON) scripts/run_demo.py REF-1001

run: validate index evaluate test evidence demo

ui:
	streamlit run ui/app.py

docker-build:
	docker build -t referral-management-copilot .

docker-run:
	docker run --rm --env-file .env -p 8501:8501 referral-management-copilot

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov build dist *.egg-info
