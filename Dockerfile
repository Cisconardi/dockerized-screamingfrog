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
RUN wget https://download.screamingfrog.co.uk/products/seo-spider/screamingfrogseospider_18.1_all.deb && \
    dpkg -i screamingfrogseospider_18.1_all.deb && \
    rm screamingfrogseospider_18.1_all.deb

# Crea la cartella e accetta EULA
RUN mkdir -p /root/.ScreamingFrogSEOSpider && \
    echo 'eula.accepted=12' > /root/.ScreamingFrogSEOSpider/spider.config

# Variabili d'ambiente per la licenza
ENV SF_LICENSE_NAME=""
ENV SF_LICENSE_KEY=""

# Scrive licence.txt dinamicamente (non serve il file statico)
RUN echo "name=${SF_LICENSE_NAME}" > /root/.ScreamingFrogSEOSpider/licence.txt && \
    echo "license=${SF_LICENSE_KEY}" >> /root/.ScreamingFrogSEOSpider/licence.txt

# Script CLI (se serve ancora)
COPY start_screamingfrog.sh /root/start_screamingfrog.sh
RUN chmod +x /root/start_screamingfrog.sh

# === INTEGRAZIONE MCP SERVER ===

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
ENTRYPOINT ["uvicorn", "mcp.main:app", "--host", "0.0.0.0", "--port", "8000"]
