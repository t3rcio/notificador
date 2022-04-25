'''
Endpoints for GMB - Google My Business
'''
SERVICE_ENDPOINT = 'https://mybusinessaccountmanagement.googleapis.com'

ACCOUNTS = '/v1/accounts'
LOCATIONS = '/v1/locations'

# - verifique esse endpoint para a normatizacao google
LOCATIONS_BY_ACCOUNT = '/v1/accounts/<string:parent_account>/locations'
REVIEWS = '/v1/reviews'

# - verifique esse endpoint para a normatizacao google
REVIEWS_BY_ACCOUNTS_LOCATIONS = '/v1/accounts/<string:parent_account>/locations/<int:location_id>/reviews'
