from pydantic import BaseModel
from typing import Optional, List

class CrawlRequest(BaseModel):
    url: str
    headless: bool = True
    spider: bool = False
    save_crawl: bool = True
    export_tabs: List[str] = ["Internal:All"]
    export_format: str = "csv"
    crawl_subdomains: bool = False
    crawl_external: bool = False
    config: Optional[str] = ""
    crawl_list: Optional[str] = ""
    include: Optional[str] = ""
    exclude: Optional[str] = ""
    user_agent: Optional[str] = ""
    authentication: Optional[str] = ""
    proxy: Optional[str] = ""
    max_depth: Optional[int] = 0
    max_urls: Optional[int] = 0
    output_folder: Optional[str] = None #aggiungot per compatibilità
