# For more information, please refer to https://aka.ms/vscode-docker-python
FROM mongo

RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get -y install python3.8
# Install pip requirements
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

WORKDIR /python_app
COPY . /python_app

# CMD ["python3", "crypto_market_tracker.py"]
