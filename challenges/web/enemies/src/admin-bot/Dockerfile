FROM python:3.12
WORKDIR /opt/bot
COPY pyproject.toml poetry.lock ./
RUN mkdir admin_bot && touch admin_bot/__init__.py
RUN pip install .
RUN rm -rf admin_bot
RUN apt-get update # This is required to get the package index
RUN apt-get install -y \
    curl \
    unzip \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
	libx11-xcb1 \
	libgbm1
RUN playwright install chromium
COPY . ./
CMD ["python3", "-m", "admin_bot"]
