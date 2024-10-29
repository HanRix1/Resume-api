FROM python:3.12.3

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app

RUN pip install pdm
COPY ./pyproject.toml ./pdm.lock ./
RUN pdm export --prod -f requirements -o requirements.txt
RUN pip install --no-cache-dir -r requirements.txt --user --no-dependencies


COPY . /usr/src/app

CMD ["python", "main.py"]