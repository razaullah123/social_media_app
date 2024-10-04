from datetime import datetime, timedelta

from jose import JWSError, jwt, ExpiredSignatureError
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from . import schemas, database, models
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "12e2bcc7b4cfd947ec78d7eeaa1bf56077a8bd1a24b827243caecfcd38540dbe"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        # Decode the JWT token and automatically check the expiration ("exp" claim)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception

        token_data = schemas.TokenData(id=str(id))

    except ExpiredSignatureError:
        # This will handle the specific case where the token is expired
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWSError:
        # This will handle other issues, such as invalid tokens
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(str(token), credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user
