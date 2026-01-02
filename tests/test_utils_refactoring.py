"""Tests for refactored utility functions."""
import pytest
from httpx import Request, Response

from postgrest.exceptions import APIError
from postgrest.utils import handle_request_error, parse_text_search_type


class TestParseTextSearchType:
    """Test the parse_text_search_type utility function."""

    def test_plain_type(self):
        """Test that 'plain' returns 'pl'."""
        assert parse_text_search_type("plain") == "pl"

    def test_phrase_type(self):
        """Test that 'phrase' returns 'ph'."""
        assert parse_text_search_type("phrase") == "ph"

    def test_web_search_type(self):
        """Test that 'web_search' returns 'w'."""
        assert parse_text_search_type("web_search") == "w"

    def test_none_type(self):
        """Test that None returns empty string."""
        assert parse_text_search_type(None) == ""

    def test_unknown_type(self):
        """Test that unknown type returns empty string."""
        assert parse_text_search_type("unknown") == ""


class TestHandleRequestError:
    """Test the handle_request_error utility function."""

    def test_raises_api_error(self):
        """Test that handle_request_error always raises APIError."""
        # Create a mock response with error
        request = Request("GET", "http://test.com")
        response = Response(
            status_code=400,
            request=request,
            content=b'{"message": "Test error", "code": "400"}',
        )

        with pytest.raises(APIError) as exc_info:
            handle_request_error(response)

        assert "Test error" in str(exc_info.value) or "400" in str(exc_info.value)

    def test_handles_invalid_json(self):
        """Test that handle_request_error handles invalid JSON gracefully."""
        request = Request("GET", "http://test.com")
        response = Response(
            status_code=500,
            request=request,
            content=b"Invalid JSON",
        )

        # Should still raise APIError even with invalid JSON
        with pytest.raises(APIError):
            handle_request_error(response)
