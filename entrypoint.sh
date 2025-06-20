#!/bin/bash

export _JAVA_OPTIONS="-Xmx1024m"
umask 000

mkdir -p /root/.ScreamingFrogSEOSpider /output /crawls
chmod -R 777 /root/.ScreamingFrogSEOSpider /output /crawls

# Scrivi licenza valida in due righe
echo "${SF_LICENSE_NAME}" > /root/.ScreamingFrogSEOSpider/licence.txt
echo "${SF_LICENSE_KEY}" >> /root/.ScreamingFrogSEOSpider/licence.txt

# Accetta EULA
echo "eula.accepted=15" > /root/.ScreamingFrogSEOSpider/spider.config

# Avvia FastAPI MCP
exec uvicorn mcp.main:app --host 0.0.0.0 --port 8080
