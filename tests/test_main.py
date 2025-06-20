import os
import pytest
from fastapi.testclient import TestClient
from unittest import mock

# Assuming mcp.main is accessible from the tests directory.
# If not, sys.path adjustments might be needed, but try direct import first.
# This might require an __init__.py in the root mcp directory if running pytest from root
# or specific PYTHONPATH setup. For simplicity, let's assume it works or can be made to work.

# To make mcp.main importable, create an empty mcp/__init__.py if it's not there.
# Also create tests/__init__.py.

# The following line needs mcp.main to be discoverable.
# We'll be patching 'mcp.main.crawl_states' and 'mcp.main.os.path.isfile'
from mcp.main import app, crawl_states # Import app and crawl_states

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_crawl_states():
    # Clear crawl_states before each test to ensure isolation
    crawl_states.clear()

def test_download_report_crawl_id_not_found():
    response = client.get("/download/nonexistent_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Crawl ID nonexistent_id not found."}

def test_download_report_crawl_running():
    crawl_id = "test_running_id"
    crawl_states[crawl_id] = "running"
    response = client.get(f"/download/{crawl_id}")
    assert response.status_code == 409
    assert response.json() == {"detail": f"Crawl {crawl_id} is still in progress. Please try again later."}

def test_download_report_crawl_failed():
    crawl_id = "test_failed_id"
    crawl_states[crawl_id] = "failed: Some error occurred"
    response = client.get(f"/download/{crawl_id}")
    assert response.status_code == 500
    assert response.json() == {"detail": f"Crawl {crawl_id} failed. No report available. Error: failed: Some error occurred"}

@mock.patch("mcp.main.os.path.isfile")
def test_download_report_success_file_not_found(mock_isfile):
    crawl_id = "test_success_no_file_id"
    crawl_states[crawl_id] = "success"
    mock_isfile.return_value = False # Simulate file not existing

    response = client.get(f"/download/{crawl_id}")

    assert response.status_code == 404
    expected_filename = "internal_all.csv"
    assert response.json() == {"detail": f"Report file {expected_filename} not found for successful crawl {crawl_id}. The crawl completed, but the expected output file is missing."}
    mock_isfile.assert_called_once_with(f"/output/{crawl_id}/{expected_filename}")

@mock.patch("mcp.main.os.path.isfile")
@mock.patch("mcp.main.FileResponse") # Mock FileResponse to avoid actual file operations
def test_download_report_success_file_found(mock_file_response, mock_isfile):
    crawl_id = "test_success_file_found_id"
    crawl_states[crawl_id] = "success"
    mock_isfile.return_value = True # Simulate file existing

    # Configure the mock FileResponse if needed, e.g., to simulate an object
    mock_file_response.return_value = "FileResponse_mock_object"

    response = client.get(f"/download/{crawl_id}")

    assert response.status_code == 200
    # The TestClient won't actually return the FileResponse object directly in 'response.content' in the same way
    # a browser would get the file. We primarily care that it got to the FileResponse part.
    # The content of the response will be the string representation of our mock_file_response.return_value
    assert response.content == b"FileResponse_mock_object"

    expected_filename = "internal_all.csv"
    expected_path = f"/output/{crawl_id}/{expected_filename}"
    mock_isfile.assert_called_once_with(expected_path)
    mock_file_response.assert_called_once_with(expected_path, filename=f"{crawl_id}_{expected_filename}", media_type="application/octet-stream")

def test_download_report_unknown_state():
    crawl_id = "test_unknown_state_id"
    crawl_states[crawl_id] = "weird_state"
    response = client.get(f"/download/{crawl_id}")
    assert response.status_code == 500
    assert response.json() == {"detail": f"Crawl {crawl_id} is in an unknown state: weird_state."}
