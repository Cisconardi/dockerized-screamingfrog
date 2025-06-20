import subprocess

def run_crawl(url: str, export_tabs: list, export_format: str, output_folder: str):
    export_tabs_str = ",".join(export_tabs)
    command = [
        "/usr/bin/screamingfrogseospider",
        "--headless",
        "--crawl", url,
        "--save-crawl",
        "--output-folder", output_folder,
        "--export-tabs", export_tabs_str,
        "--export-format", export_format
    ]
    subprocess.run(command, check=True)
