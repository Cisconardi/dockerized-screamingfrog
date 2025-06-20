#!/bin/bash

# ✅ Imposta memoria massima Java a 1GB
export _JAVA_OPTIONS="-Xmx1024m"

# Forza i permessi se monti volumi
mkdir -p /root/.ScreamingFrogSEOSpider
chmod -R 777 /root/.ScreamingFrogSEOSpider /output /crawls

# Accetta la EULA e imposta la licenza
mkdir -p /root/.ScreamingFrogSEOSpider
echo "eula.accepted=15" > /root/.ScreamingFrogSEOSpider/spider.config
echo "name=${SF_LICENSE_NAME}" > /root/.ScreamingFrogSEOSpider/licence.txt
echo "license=${SF_LICENSE_KEY}" >> /root/.ScreamingFrogSEOSpider/licence.txt



# Avvia il server FastAPI
exec uvicorn mcp.main:app --host 0.0.0.0 --port 8080
