from jose import jwt
from config import SECRET_KEY

ALGORITHM = "HS256"


def create_token(data):

    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token):

    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
