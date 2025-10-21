FROM python:3.12
COPY pyproject.toml poetry.lock ./
RUN mkdir backend && touch backend/__init__.py
RUN pip install .
RUN rm -rf backend
COPY . ./
CMD ["uvicorn", "backend:APP", "--host", "0.0.0.0", "--port", "8000", "--header", "Access-Control-Allow-Methods:POST,GET", "--header", "Access-Control-Allow-Origin:*", "--header", "Access-Control-Allow-Headers:*"]
