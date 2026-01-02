JWT Token Validation
=====================

The library provides a utility function to validate JWT (JSON Web Token) format.

Validating JWT Tokens
----------------------

You can use the ``is_valid_jwt`` function to check if a token string follows the proper JWT format:

.. code-block:: python

    from postgrest import is_valid_jwt

    # Valid JWT token (header.payload.signature)
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    
    if is_valid_jwt(token):
        print("Token is a valid JWT")
    else:
        print("Token is not a valid JWT format")

.. note::
    The ``is_valid_jwt`` function only validates the **format** of the JWT token (three base64url-encoded parts separated by dots). It does **not** verify the signature or validate the token's claims (expiration, issuer, etc.). For full JWT verification, use a dedicated JWT library like PyJWT.

Use Cases
---------

This function is useful when you want to:

- Check if a token string is in JWT format before processing
- Distinguish between JWT tokens and other types of API keys
- Validate user input before passing tokens to authentication

Example with Authentication
----------------------------

.. code-block:: python

    import asyncio
    from postgrest import AsyncPostgrestClient, is_valid_jwt

    async def main():
        token = "your-token-here"
        
        async with AsyncPostgrestClient("http://localhost:3000") as client:
            # Optionally validate JWT format before authenticating
            if is_valid_jwt(token):
                print("Using JWT token")
            else:
                print("Using API key or other token format")
            
            # The auth method accepts both JWT tokens and other API keys
            client.auth(token)
            r = await client.from_("countries").select("*").execute()
            countries = r.data

    asyncio.run(main())

.. tip::
    The ``auth`` method accepts any token string, including JWT tokens and other API keys. You don't need to validate the format before calling ``auth``, but the ``is_valid_jwt`` function is available if you need format validation for your application logic.
