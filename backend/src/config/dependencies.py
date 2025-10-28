from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from config import crud, schema, security
from config.database import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_session)
        ) -> schema.User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    # Now that we have the username, find the user in the database
    user = await crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    
    # Return the user as Pydantic schema
    return schema.User.model_validate(user)