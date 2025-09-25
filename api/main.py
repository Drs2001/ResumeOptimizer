from typing import Union, Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from database.model import DB, Token, User, UserPublic, UserCreate
from auth import verify_password, create_access_token, decode
from jose import JWTError

db = DB()

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/register/")
def register(username: str, password: str):
    """
    Registers a new user

    Returns:
        String: Message whether the new user was added succesfully
    """
    if db.find_user(username):
        raise HTTPException(status_code=400, detail="Username already taken")
    return db.add_user(username, password)

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    Logs the user in and creates a access token

    Returns:
        Token: access token and token type
    """
    user = db.find_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")
    
@app.get("/me")
def read_users_me(token: str = Depends(oauth2_scheme)):
    """
    Returns the user based on the token

    Returns:
        Dict: The users username
    """
    try:
        payload = decode(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@app.get("/users/", response_model=list[User])
def read_users(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return db.get_users()
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}