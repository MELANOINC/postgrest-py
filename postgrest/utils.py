from __future__ import annotations

import base64
import re
from typing import Any, Type, TypeVar, cast, get_origin
from urllib.parse import urlparse

from deprecation import deprecated
from httpx import AsyncClient  # noqa: F401
from httpx import Client as BaseClient  # noqa: F401
from httpx import Response as RequestResponse
from pydantic import BaseModel, ValidationError

from .version import __version__

# Compiled regex pattern for base64url validation (used in JWT validation)
_BASE64URL_PATTERN = re.compile(r'^[A-Za-z0-9_-]+$')


class SyncClient(BaseClient):
    @deprecated(
        "1.0.2", "1.3.0", __version__, "Use `Client` from the httpx package instead"
    )
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @deprecated(
        "1.0.2",
        "1.3.0",
        __version__,
        "Use `close` method from `Client` in the httpx package instead",
    )
    def aclose(self) -> None:
        self.close()


def sanitize_param(param: Any) -> str:
    param_str = str(param)
    reserved_chars = ",:()"
    if any(char in param_str for char in reserved_chars):
        return f'"{param_str}"'
    return param_str


def sanitize_pattern_param(pattern: str) -> str:
    return sanitize_param(pattern.replace("%", "*"))


_T = TypeVar("_T")


def get_origin_and_cast(typ: type[type[_T]]) -> type[_T]:
    # Base[T] is an instance of typing._GenericAlias, so doing Base[T].__init__
    # tries to call _GenericAlias.__init__ - which is the wrong method
    # get_origin(Base[T]) returns Base
    # This function casts Base back to Base[T] to maintain type-safety
    # while still allowing us to access the methods of `Base` at runtime
    # See: definitions of request builders that use multiple-inheritance
    # like AsyncFilterRequestBuilder
    return cast(Type[_T], get_origin(typ))


def is_http_url(url: str) -> bool:
    return urlparse(url).scheme in {"https", "http"}


TBaseModel = TypeVar("TBaseModel", bound=BaseModel)


def model_validate_json(model: Type[TBaseModel], contents) -> TBaseModel:
    """Compatibility layer between pydantic 1 and 2 for parsing an instance
    of a BaseModel from varied"""
    try:
        # pydantic > 2
        return model.model_validate_json(contents)
    except AttributeError:
        # pydantic < 2
        return model.parse_raw(contents)


def is_valid_jwt(token: Any) -> bool:
    """
    Validates if a string is a properly formatted JWT token.
    
    A valid JWT token consists of three base64url-encoded parts
    separated by dots: header.payload.signature
    
    Args:
        token: The token to validate (typically a string)
        
    Returns:
        True if the token is a valid JWT format, False otherwise
    """
    if not token or not isinstance(token, str):
        return False
    
    # JWT should have exactly 3 parts separated by dots
    parts = token.split(".")
    if len(parts) != 3:
        return False
    
    # Check if each part is valid base64url encoding
    for part in parts:
        if not part:  # Empty parts are not allowed
            return False
        if not _BASE64URL_PATTERN.match(part):
            return False
    
    # Additional validation: try to decode the header and payload
    # to ensure they are valid base64url
    try:
        # Add padding if needed for base64 decoding
        for i in range(2):  # Only validate header and payload, not signature
            part = parts[i]
            # Add padding
            padding = 4 - (len(part) % 4)
            if padding != 4:
                part += '=' * padding
            # Replace base64url characters with base64
            part = part.replace('-', '+').replace('_', '/')
            base64.b64decode(part)
    except (ValueError, TypeError, base64.binascii.Error):
        return False
    
    return True


def parse_text_search_type(type_: str | None) -> str:
    """
    Parse text search type option into PostgREST format.
    
    Args:
        type_: The text search type ('plain', 'phrase', or 'web_search')
        
    Returns:
        The corresponding PostgREST type prefix ('pl', 'ph', 'w', or '')
    """
    if type_ == "plain":
        return "pl"
    elif type_ == "phrase":
        return "ph"
    elif type_ == "web_search":
        return "w"
    return ""


def handle_request_error(response: RequestResponse) -> None:
    """
    Handle HTTP request errors by parsing and raising appropriate APIError.
    
    This function attempts to parse the error response from the API and raise
    an APIError with the parsed details. If parsing fails, it raises a generic
    APIError with the response details.
    
    Args:
        response: The HTTP response object from the failed request
        
    Raises:
        APIError: Always raises an APIError with details from the response
    """
    # Import here to avoid circular dependency between utils.py and exceptions.py
    # exceptions.py uses generate_default_error_message which formats response data
    from .exceptions import APIError, APIErrorFromJSON, generate_default_error_message
    
    try:
        json_obj = model_validate_json(APIErrorFromJSON, response.content)
        raise APIError(dict(json_obj))
    except ValidationError:
        raise APIError(generate_default_error_message(response))
