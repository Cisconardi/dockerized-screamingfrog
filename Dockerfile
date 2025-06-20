FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
ENV _JAVA_OPTIONS="-Xmx1024m"

# Installazione dipendenze di sistema
RUN apt-get update && apt-get install -y \
    debconf-utils ttf-mscorefonts-installer \
    sudo wget xdg-utils curl gnupg2 unzip \
    libgconf-2-4 zenity fonts-wqy-zenhei xvfb \
    libgtk2.0-0 libnss3 libxss1 \
    openjdk-21-jre \
    python3 python3-pip && \
    apt-get clean

# Installa Screaming Frog
RUN wget https://download.screamingfrog.co.uk/products/seo-spider/screamingfrogseospider_22.1_all.deb && \
    dpkg -i screamingfrogseospider_22.1_all.deb && \
    rm screamingfrogseospider_22.1_all.deb

# Crea utente generico
RUN useradd -ms /bin/bash app

# === Setup cartelle ===
RUN mkdir -p /output /crawls /root/.ScreamingFrogSEOSpider && \
    chmod -R 777 /output /crawls /root/.ScreamingFrogSEOSpider

# Copia script di avvio
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# CLI compatibile con avvio standalone
COPY start_screamingfrog.sh /root/start_screamingfrog.sh
RUN chmod +x /root/start_screamingfrog.sh

# === COPY MCP Server ===
WORKDIR /app
COPY mcp /app/mcp
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Espone la porta FastAPI MCP
EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
