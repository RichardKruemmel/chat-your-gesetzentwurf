import os
import secrets
from datetime import timedelta
import os
from typing import List, Optional, Annotated

from fastapi import FastAPI, Depends, HTTPException, File, status, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
import langchain
from pydantic import BaseModel

# from app.core.chat import get_response
from app.database.database import Session
from app.database.crud import get_user
from app.database.schema import ChatRequest, Token, User
from app.security import create_access_token
from app.utils.bearer import OAuth2PasswordBearerWithCookie
from app.utils.hashing import Hasher


def get_application():
    _app = FastAPI(title="Chat your Gesetzentwurf")

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


if os.environ.get("ENV") == "local":
    langchain.debug = True


def authenticate_user(username: str, password: str, db: Session):
    user = get_user(username=username, db=db)
    if not user:
        return False
    if not Hasher.verify_password(password, user.hashed_password):
        return False
    return user


@app.post("/token", response_model=Token)
def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(
        minutes=int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])
    )
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )
    return {"access_token": access_token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")


def get_current_user_from_token(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(
            token, os.environ["SECRET_KEY"], algorithms=[os.environ["ALGORITHM"]]
        )
        username: str = payload.get("sub")
        print("username/email extracted is ", username)
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username=username, db=db)
    if user is None:
        raise credentials_exception
    return user


@app.get("/")
async def read_root(name: Optional[str] = ", chat with your Gesetzentwurf!"):
    return {"Hello": name}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user_from_token)):
    return current_user


@app.post(
    "/chat",
    summary="Chat with the AI",
    description="Get a response from the AI model based on the input text",
)
async def read_chat(request: ChatRequest):
    try:
        content = request.messages[-1].content
        input_file = request.files[0] if request.files else None

        response = None
        # get_response(content, ai="qa-chain", input_file=input_file)

        if response is not None:
            return response
        else:
            raise HTTPException(
                status_code=500, detail="Failed to get a response from the AI model"
            )
    except IndexError:
        raise HTTPException(
            status_code=400, detail="No messages provided in the request"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


""" 
@app.post("/uploadfile")
async def create_upload_file(
    # current_user: User = Depends(get_current_user_from_token),
    file: UploadFile = File(...),
):
    if not (file.filename.lower().endswith((".pdf", ".txt"))):
        raise HTTPException(
            status_code=500, detail="Wrong file type. You need a PDF or text file"
        )
    try:
        
    except Exception as e:
        print("Error uploading file")
        print(e)
        raise HTTPException(status_code=500, detail="Failed to upload file") """
