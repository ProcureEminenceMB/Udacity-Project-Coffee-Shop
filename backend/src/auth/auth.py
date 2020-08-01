import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'udacity-coffee-project.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee-api'

## AuthError Exception

class AuthError(Exception):
	def __init__(self, error, status_code):
		self.error = error
		self.status_code = status_code


## Auth Header

def get_token_auth_header():
	# Access the authorization header
	authHeader = request.headers.get('Authorization', None)

	# Raise error if no authorization header was found
	if authHeader is None:
		raise AuthError({
			'code': 'auth_header_missing',
			'description': 'No authorization header was found.'
		}, 401)

	# Split authorization header and analyze
	authDetails = authHeader.split()

	if len(authDetails) != 2: # Authorization header must be two parts; type and token
		raise AuthError({
			'code': 'auth_header_invalid',
			'description': 'Authorization header must contain the token type and the token.'
		}, 401)

	authType = authDetails[0]
	authToken = authDetails[1]

	if authType != 'Bearer': # Authorization header must be bearer
		raise AuthError({
			'code': 'auth_header_invalid',
			'description': 'Authorization header must use a Bearer token.'
		}, 401)

	return authToken

def check_permissions(permission, payload):
	if 'permissions' not in payload: # Check for 'permissions' key in the payload
		raise AuthError({
			'code': 'invalid_permission',
			'description': 'Permission was not specified in the token.'
		}, 401)

	if permission not in payload['permissions']: # Check for required permission
		raise AuthError({
			'code': 'forbidden',
			'description': 'You don\'t have access to this feature.'
		}, 403)
	return True

def verify_decode_jwt(token):
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
			raise AuthError({
				'code': 'invalid_claims',
				'description': 'Incorrect claims. Please, check the audience and issuer.'
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

def requires_auth(permission=''):
	def requires_auth_decorator(f):
		@wraps(f)
		def wrapper(*args, **kwargs):
			token = get_token_auth_header()
			payload = verify_decode_jwt(token)
			check_permissions(permission, payload)
			return f(payload, *args, **kwargs)

		return wrapper
	return requires_auth_decorator