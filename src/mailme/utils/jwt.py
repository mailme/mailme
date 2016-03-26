from datetime import datetime, timedelta

import jwt
from django.conf import settings


JWT_OPTIONS = {
    'verify_signature': True,
    'verify_exp': True,
    'verify_nbf': True,
    'verify_iat': True,
    'verify_aud': False,
    'require_exp': True,
    'require_iat': True,
    'require_nbf': True
}

LEEWAY = 10
EXPIRATION_DELTA = timedelta(seconds=60)


def decode_token(token, user):
    # TODO: user based secret keys

    return jwt.decode(
        token,
        verify=True,
        key=settings.SECRET_KEY,
        options=JWT_OPTIONS,
        leeway=LEEWAY,
        algorithms=['HS256']
    )


def encode_token(user_id, private_key):
    issued_at = datetime.utcnow()
    payload = {
        'iss': user_id,
        'exp': issued_at + EXPIRATION_DELTA,
        'iat': issued_at,
        'nbf': issued_at,
    }

    return jwt.encode(
        payload,
        key=settings.SECRET_KEY,
        algorithm='HS256'
    ).decode('utf-8')
