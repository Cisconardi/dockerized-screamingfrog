#!/bin/bash

set -e  # Esce subito in caso di errore

# Imposta memoria Java
export _JAVA_OPTIONS="-Xmx1024m"

# Permessi open per output & crawl (se montati)
umask 000
mkdir -p /output /crawls /root/.ScreamingFrogSEOSpider
chmod -R 777 /output /crawls /root/.ScreamingFrogSEOSpider

# Accetta EULA Screaming Frog
echo "eula.accepted=15" > /root/.ScreamingFrogSEOSpider/spider.config

# Imposta licenza correttamente (prima riga: username, seconda riga: key)
echo "${SF_LICENSE_NAME}" > /root/.ScreamingFrogSEOSpider/licence.txt
echo "${SF_LICENSE_KEY}" >> /root/.ScreamingFrogSEOSpider/licence.txt
chmod 600 /root/.ScreamingFrogSEOSpider/licence.txt

chmod 600 /root/.ScreamingFrogSEOSpider/licence.txt

# Avvia il server FastAPI
echo "Starting FastAPI MCP server..."
exec uvicorn mcp.main:app --host 0.0.0.0 --port 8080
