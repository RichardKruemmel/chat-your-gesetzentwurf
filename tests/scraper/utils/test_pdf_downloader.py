import pytest
import requests
from app.scraper.utils.pdf_downloader import download_pdf
from unittest.mock import patch, mock_open


@patch("requests.get")
def test_download_pdf_success(mock_get):
    url = "https://example.com/pdf"
    save_path = "/path/to/save.pdf"
    content = b"PDF content"

    mock_response = mock_get.return_value
    mock_response.content = content
    mock_response.raise_for_status.return_value = None

    with patch("builtins.open", mock_open()) as mock_file:
        download_pdf(url, save_path)

    mock_get.assert_called_once_with(url)
    mock_response.raise_for_status.assert_called_once()
    mock_file.assert_called_once_with(save_path, "wb")
    mock_file.return_value.write.assert_called_once_with(content)


@patch("requests.get")
def test_download_pdf_failure(mock_get):
    url = "https://example.com/pdf"
    save_path = "/path/to/save.pdf"

    mock_response = mock_get.return_value
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError

    with pytest.raises(requests.exceptions.HTTPError):
        download_pdf(url, save_path)

    mock_get.assert_called_once_with(url)
    mock_response.raise_for_status.assert_called_once()
