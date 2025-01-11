import json
from flask import request
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import os


AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
ALGORITHMS = [os.environ['ALGORITHMS']]
API_AUDIENCE = os.environ['API_AUDIENCE']

# AuthError Exception
# A standardized way to handle and communicate authentication and authorization errors.

class AuthError(Exception):
    """
    Custom exception for authentication errors.

    Attributes:
        error (dict): Error details including a code and description.
        status_code (int): HTTP status code associated with the error.
    """
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

# Get Token Auth Header
# Extracts and validates the authorization token from the request header.

def get_token_auth_header():
    """
    Extracts the token from the Authorization header.

    Process:
        - Ensures the Authorization header is present.
        - Validates the header format as 'Bearer <token>'.
        - Returns the token if valid.

    Raises:
        AuthError: If the header is missing, malformed, or the token is absent.
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token


# Check Permissions
# Validates that the required permission exists in the JWT payload.

def check_permissions(permission, payload):
    """
    Ensures the user has the necessary permission.

    Args:
        permission (str): The required permission string (e.g., 'post:actors').
        payload (dict): The decoded JWT payload.

    Process:
        - Checks if 'permissions' exist in the payload.
        - Validates the required permission against the payload's permissions list.
        - Returns True if valid.

    Raises:
        AuthError: If the permissions claim is missing or the required permission is not found.
    """
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)
    return True


# Verify and Decode JWT
# Verifies and decodes a JSON Web Token (JWT) using Auth0's JSON Web Key Set (JWKS).

def verify_decode_jwt(token):
    """
    Verifies and decodes the JWT token using Auth0.

    Args:
        token (str): The JWT token to verify.

    Process:
        - Fetches the JWKS from the Auth0 domain.
        - Extracts the token's header and validates the key ID (kid).
        - Uses the appropriate RSA key to verify the token's signature.
        - Decodes the token and validates its claims (audience and issuer).

    Returns:
        dict: Decoded JWT payload.

    Raises:
        AuthError: For invalid headers, expired tokens, incorrect claims, or any other verification issues.
    """
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            message = 'Incorrect claims. Please, check the audience and issuer.'
            raise AuthError({
                'code': 'invalid_claims',
                'description': message
            }, 401)

        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)

    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)


# Requires Authorization
# A decorator to enforce authentication and authorization for protected routes.

def requires_auth(permission=''):
    """
    Decorator to enforce authentication and authorization.

    Args:
        permission (str): The required permission string (e.g., 'post:actors').

    Process:
        - Retrieves the token using get_token_auth_header().
        - Verifies and decodes the token using verify_decode_jwt().
        - Validates the required permission using check_permissions().
        - Passes the decoded payload to the decorated function.

    Returns:
        function: The decorated function with validated payload passed as an argument.

    Raises:
        AuthError: For missing tokens, invalid permissions, or JWT verification issues.
    """
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator
