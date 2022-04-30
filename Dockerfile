# For more information, please refer to https://aka.ms/vscode-docker-python
FROM 739065237548.dkr.ecr.us-east-1.amazonaws.com/billtitles-py:base
#FROM tiangolo/uvicorn-gunicorn:python3.8

EXPOSE 80

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

#RUN apt update && apt upgrade -y
#RUN apt-get install curl -y

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
USER ${APPUSER}

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#CMD ["uvicorn", "billtitles.main:app"]
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:80", "-k", "uvicorn.workers.UvicornWorker", "billtitles.main:app"]
