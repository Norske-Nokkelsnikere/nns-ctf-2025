FROM python:3.12
WORKDIR app
COPY . ./
RUN pip install .
CMD ["uvicorn", "card7:app", "--host", "0.0.0.0", "--port", "9999"]
