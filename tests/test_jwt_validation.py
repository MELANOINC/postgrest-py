"""Tests for JWT token validation utilities."""

import pytest

from postgrest.utils import is_valid_jwt


class TestJWTValidation:
    """Test cases for JWT token validation."""

    def test_valid_jwt_token(self):
        """Test that a valid JWT token is recognized."""
        # This is a sample JWT token (header.payload.signature format)
        valid_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        assert is_valid_jwt(valid_jwt) is True

    def test_another_valid_jwt(self):
        """Test another valid JWT format."""
        valid_jwt = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInN1YiI6InVzZXIxMjMiLCJleHAiOjE3MDAwMDAwMDB9.abc123-def456_ghi789"
        assert is_valid_jwt(valid_jwt) is True

    def test_invalid_jwt_two_parts_only(self):
        """Test that a token with only two parts is invalid."""
        invalid_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0"
        assert is_valid_jwt(invalid_jwt) is False

    def test_invalid_jwt_four_parts(self):
        """Test that a token with four parts is invalid."""
        invalid_jwt = "part1.part2.part3.part4"
        assert is_valid_jwt(invalid_jwt) is False

    def test_invalid_jwt_empty_string(self):
        """Test that an empty string is invalid."""
        assert is_valid_jwt("") is False

    def test_invalid_jwt_none(self):
        """Test that None is invalid."""
        # This should not raise an exception
        assert is_valid_jwt(None) is False

    def test_invalid_jwt_non_string(self):
        """Test that non-string values are invalid."""
        assert is_valid_jwt(123) is False
        assert is_valid_jwt([]) is False
        assert is_valid_jwt({}) is False

    def test_invalid_jwt_with_spaces(self):
        """Test that a token with spaces is invalid."""
        invalid_jwt = "eyJhbGci OiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature"
        assert is_valid_jwt(invalid_jwt) is False

    def test_invalid_jwt_with_special_chars(self):
        """Test that a token with invalid characters is invalid."""
        invalid_jwt = "header!@#.payload$%^.signature&*()"
        assert is_valid_jwt(invalid_jwt) is False

    def test_invalid_jwt_empty_parts(self):
        """Test that a token with empty parts is invalid."""
        invalid_jwt = "..signature"
        assert is_valid_jwt(invalid_jwt) is False
        invalid_jwt = "header.."
        assert is_valid_jwt(invalid_jwt) is False

    def test_invalid_jwt_non_base64(self):
        """Test that a token with non-base64 content is invalid."""
        # Using invalid base64 characters
        invalid_jwt = "!!!.???.***"
        assert is_valid_jwt(invalid_jwt) is False

    def test_simple_string_not_jwt(self):
        """Test that a simple string is not recognized as JWT."""
        assert is_valid_jwt("s3cr3t") is False
        assert is_valid_jwt("Bearer token") is False
        assert is_valid_jwt("random_api_key_12345") is False

    def test_base64_but_not_jwt_format(self):
        """Test that base64 strings without proper JWT structure are invalid."""
        # Valid base64 but not three parts
        assert is_valid_jwt("dGVzdA==") is False
        assert is_valid_jwt("dGVzdA.dGVzdA") is False
