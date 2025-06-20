FROM ubuntu:22.04

# Imposta frontend non interattivo per apt
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt-get update && apt-get install -y debconf-utils

# Aggiorna sistema e installa dipendenze di sistema
RUN apt update && apt upgrade -y && \
    apt install -y \
    ttf-mscorefonts-installer \
    sudo wget xdg-utils curl gnupg2 unzip \
    libgconf-2-4 zenity fonts-wqy-zenhei xvfb libgtk2.0-0 libnss3 libxss1 \
    openjdk-21-jre \
    python3 python3-pip

# Imposta limite memoria Java (1GB)
ENV _JAVA_OPTIONS="-Xmx1024m"

# Installa Screaming Frog 22.1
RUN wget https://download.screamingfrog.co.uk/products/seo-spider/screamingfrogseospider_22.1_all.deb && \
    dpkg -i screamingfrogseospider_22.1_all.deb && \
    rm screamingfrogseospider_22.1_all.deb

# Copia gli script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# CLI legacy
COPY start_screamingfrog.sh /root/start_screamingfrog.sh
RUN chmod +x /root/start_screamingfrog.sh

# === CREA UTENTE APP ===
RUN useradd -ms /bin/bash app

# === INTEGRAZIONE MCP SERVER ===

WORKDIR /app

COPY mcp /app/mcp
COPY requirements.txt /app/requirements.txt

RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Crea le cartelle e assegna i permessi all'utente "app"
RUN mkdir -p /output /crawls && \
    chown -R app:app /output /crawls /app

# Imposta utente non root
USER app

# Espone la porta FastAPI MCP
EXPOSE 8080

# Avvio server MCP
ENTRYPOINT ["/entrypoint.sh"]
