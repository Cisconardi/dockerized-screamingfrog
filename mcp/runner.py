import subprocess
from pathlib import Path
from mcp.models import CrawlRequest

def build_command(req: CrawlRequest):
    """
    Constructs the Screaming Frog CLI command based on the CrawlRequest.

    Args:
        req: The CrawlRequest object containing crawl parameters.

    Returns:
        A tuple containing the list of command arguments and the output folder path string.
    """
    output_folder = Path(req.output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    command = ["/usr/bin/screamingfrogseospider"]

    if req.headless:
        command.append("--headless")
    if req.spider:
        command.append("--spider")

    if req.url:
        command += ["--crawl", req.url]

    if req.save_crawl:
        command.append("--save-crawl")

    command += ["--output-folder", str(output_folder)]

    if req.export_tabs:
        command += ["--export-tabs", ",".join(req.export_tabs)]

    if req.export_format:
        command += ["--export-format", req.export_format]

    if req.crawl_subdomains:
        command.append("--crawl-subdomains")
    if req.crawl_external:
        command.append("--crawl-external-links")
    if req.config:
        command += ["--config", req.config]
    if req.crawl_list:
        command += ["--crawl-list", req.crawl_list]
    if req.include:
        command += ["--include", req.include]
    if req.exclude:
        command += ["--exclude", req.exclude]
    if req.user_agent:
        command += ["--user-agent", req.user_agent]
    if req.authentication:
        command += ["--authentication", req.authentication]
    if req.proxy:
        command += ["--proxy", req.proxy]
    if req.max_depth:
        command += ["--max-depth", str(req.max_depth)]
    if req.max_urls:
        command += ["--max-url-length", str(req.max_urls)]

    return command, str(output_folder)

def run_crawl(req: CrawlRequest):
    """
    Executes the Screaming Frog crawl command.

    Args:
        req: The CrawlRequest object.

    Returns:
        A dictionary containing the command executed, stdout, stderr,
        return code, and output folder path.
        Exceptions during subprocess.run (e.g., FileNotFoundError) are expected
        to be caught by the caller.
    """
    command, output_folder = build_command(req)
    result = subprocess.run(command, capture_output=True, text=True)

    return {
        "command": " ".join(command),
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "output_folder": output_folder
    }
