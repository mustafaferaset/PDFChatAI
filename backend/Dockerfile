FROM python:3.9-slim

# set work directory
WORKDIR /app

# Install build essentials and clean up in one layer to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# copy project
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

#RUN sed -i 's/\r$//g' /app/entrypoint.sh
#RUN chmod +x /app/entrypoint.sh

# run entrypoint.sh
#ENTRYPOINT ["/app/entrypoint.sh"]
