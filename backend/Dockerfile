FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Dependencias del sistema + Microsoft ODBC Driver 17 para SQL Server
RUN rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* && \
    rm -f /etc/apt/sources.list.d/debian.sources && \
    printf '%s\n' \
        'deb http://deb.debian.org/debian bookworm main' \
        'deb http://deb.debian.org/debian-security bookworm-security main' \
        > /etc/apt/sources.list && \
    apt-get update -o Acquire::Retries=5 --fix-missing && \
    apt-get install -y --no-install-recommends \
        curl \
        gnupg2 \
        apt-transport-https \
        ca-certificates \
        unixodbc \
        unixodbc-dev \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
        | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg \
    && echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
        > /etc/apt/sources.list.d/mssql-release.list \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* && \
    apt-get update -o Acquire::Retries=5 --fix-missing && \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
        msodbcsql17 \
        mssql-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

ENV PATH="$PATH:/opt/mssql-tools/bin"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/app/generated_pdfs

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "120", "wsgi:app"]