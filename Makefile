.PHONY: install run-api run-ui test lint

install:
	python -m pip install -r requirements.txt

run-api:
	uvicorn app.main:app --reload

run-ui:
	streamlit run ui/streamlit_app.py

test:
	pytest -q
