from datetime import datetime, timedelta
from xmlrpc.client import boolean
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException, status

bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

KEY = "20a6d84fa39a2c4fa2624d44290f4d84fb10319bf0a2638a162b4c836509679f"
EMAIL_KEY = "11a6d84fa38a2a2ca2624d42290f4d84fb10316bf0a2638a173b4c836509679g"
ALGORITHM = "HS512"
ACCESS_TOKEN_EXPIRE_DAYS = 1
EMAIL_TOKEN_EXPIRE_DAYS = 1

def EncryptPassword(password):
    return bcrypt.hash(password)

# Create the JW Token and add an expiration date. expires_delta= desired increase (it could be sended or not)
def CreateToken(data: dict, expires_delta: timedelta | None = None):
    toEnconde = data.copy()
    # If user send the expire_delta we add the desired increase to the now day
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    # If user doesn't send the expire_delta we add 5 days to the now day
    else:
        expire = datetime.utcnow() + timedelta(ACCESS_TOKEN_EXPIRE_DAYS)
    # change the expiration date parameter
    toEnconde.update({"exp": expire})
    updatedJWT = jwt.encode(toEnconde, KEY, algorithm=ALGORITHM)
    return updatedJWT

def CreateEmailToken(data: dict, expires_delta: timedelta | None = None):
    toEncode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(EMAIL_TOKEN_EXPIRE_DAYS)
    toEncode.update({"exp": expire})
    updatedJWT = jwt.encode(toEncode, EMAIL_KEY, algorithm=ALGORITHM)
    return updatedJWT

# This method compare the original password with the encrypted 
def VerifyPassword(original, encrypted):
    return bcrypt.verify(original, encrypted);

def DecodeToken(token):
	return jwt.decode(token, KEY, algorithms=ALGORITHM)

def DecodeEmailToken(token):
	return jwt.decode(token, EMAIL_KEY, algorithms=ALGORITHM)

async def GetTokenInformation(token):
	# Token shoud have 2 items (0=Type, 1=payload)
    try:
        if(len(token) == 2 and token[0] == "Bearer"):
            payload = DecodeToken(token[1].strip())
            username: str = payload.get("sub")
            return username
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"})
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"})
    
async def DecodeEmailTokenInformation(token):
    try:
        if(len(token) == 2 and token[0] == "Bearer"):
            payload = DecodeEmailToken(token[1].strip())
            email: str = payload.get("email")
            if payload.get("isAdmin") == True:
                role = 'admin'
            else:
                role = 'user'
            return email, role
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate type",
            headers={"WWW-Authenticate": "Bearer"}) 
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
	    detail="Could not validate credentials",
	    headers={"WWW-Authenticate": "Bearer"})
