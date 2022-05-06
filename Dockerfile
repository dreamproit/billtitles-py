FROM tiangolo/uvicorn-gunicorn:python3.8

EXPOSE 80

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_HOME=/opt/poetry

RUN apt install git gcc -y

RUN pip install --no-cache-dir poetry==1.1.13 && \
    poetry config virtualenvs.create false


# Install pip requirements
# COPY requirements.txt .
COPY pyproject.toml poetry.lock ./
RUN poetry install
#RUN python -m pip install --upgrade pip
#RUN python -m pip install -r requirements.txt

#RUN apt update && apt upgrade -y
#RUN apt-get install curl -y

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
#RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
#USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#CMD ["uvicorn", "billtitles.main:app"]
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:80", "-k", "uvicorn.workers.UvicornWorker", "billtitles.main:app"]
