import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'udacity-coffee-project.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee-api'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
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


'''
@TODO implement check_permissions(permission, payload) method
	@INPUTS
		permission: string permission (i.e. 'post:drink')
		payload: decoded jwt payload

	it should raise an AuthError if permissions are not included in the payload
		!!NOTE check your RBAC settings in Auth0
	it should raise an AuthError if the requested permission string is not in the payload permissions array
	return true otherwise
'''
def check_permissions(permission, payload):
	raise Exception('Not Implemented')

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

'''
@TODO implement @requires_auth(permission) decorator method
	@INPUTS
		permission: string permission (i.e. 'post:drink')

	it should use the get_token_auth_header method to get the token
	it should use the verify_decode_jwt method to decode the jwt
	it should use the check_permissions method validate claims and check the requested permission
	return the decorator which passes the decoded payload to the decorated method
'''
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