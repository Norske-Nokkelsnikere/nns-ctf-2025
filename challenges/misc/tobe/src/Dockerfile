FROM python:3.12
WORKDIR app
COPY . ./
RUN pip install .
CMD ["uvicorn", "tobe:app", "--host", "0.0.0.0", "--port", "9999"]
