# Setup
```sh
pip install poetry
```
# Running the backend
```sh
poetry run uvicorn backend:APP --header "Access-Control-Allow-Methods:POST,GET" --header "Access-Control-Allow-Origin:*" --header "Access-Control-Allow-Headers:*"
```

# Resetting the database
```sh
rm app.sqlite
```
