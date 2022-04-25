
from functools import wraps
from flask import request

def verify_authorization_header(function):
	'''
	Verify the request searching for Authorization Beaer: <token>
	'''
	@wraps(function)
	def decorfunc(*args, **kwargs):
		headers = request.headers
		if "Authorization" in headers:
			if "Bearer" in headers["Authorization"]:
				return function(*args, **kwargs)
		return "403"
	return decorfunc

def get_404(function):
	'''
	Returns a 404 error in case of None or [] results
	'''
	@wraps(function)
	def decorfunc(*args, **kwargs):
		result = function(*args, **kwargs)
		if result is None or result == []:
			return "404"
		return result
	return decorfunc
