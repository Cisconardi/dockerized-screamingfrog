FROM ubuntu:22.04

# Imposta frontend non interattivo per apt
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# Aggiorna sistema e installa dipendenze
RUN apt update && apt upgrade -y
RUN apt install -y \
    ttf-mscorefonts-installer \
    sudo wget xdg-utils \
    libgconf-2-4 zenity fonts-wqy-zenhei xvfb libgtk2.0-0 libnss3 libxss1 \
    python3 python3-pip

# Installa Screaming Frog 18.1
RUN wget https://download.screamingfrog.co.uk/products/seo-spider/screamingfrogseospider_22.1_all.deb && \
    dpkg -i screamingfrogseospider_22.1_all.deb && \
    rm screamingfrogseospider_22.1_all.deb

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


# Script CLI (se serve ancora)
COPY start_screamingfrog.sh /root/start_screamingfrog.sh
RUN chmod +x /root/start_screamingfrog.sh

# === INTEGRAZIONE MCP SERVER ===

WORKDIR /app

# Cartella API FastAPI (MCP)
COPY mcp /app/mcp
COPY requirements.txt /app/requirements.txt

# Installa le dipendenze Python
RUN pip3 install -r /app/requirements.txt

# Crea cartelle di output e crawls
RUN mkdir -p /output /crawls

# Imposta display virtuale
ENV DISPLAY :99

# Espone la porta API MCP
EXPOSE 8000

# Avvio: MCP Server (puoi cambiare con variabile se vuoi usare ancora CLI)
ENTRYPOINT ["/entrypoint.sh"]
