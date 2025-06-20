#!/bin/bash

# Accetta la EULA e imposta la licenza
mkdir -p /root/.ScreamingFrogSEOSpider
echo "eula.accepted=15" > /root/.ScreamingFrogSEOSpider/spider.config
echo "name=${SF_LICENSE_NAME}" > /root/.ScreamingFrogSEOSpider/licence.txt
echo "license=${SF_LICENSE_KEY}" >> /root/.ScreamingFrogSEOSpider/licence.txt

# ✅ Imposta memoria massima Java a 1GB
export _JAVA_OPTIONS="-Xmx1024m"

# Avvia il server FastAPI
exec uvicorn mcp.main:app --host 0.0.0.0 --port 8080
