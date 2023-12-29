import os
from datetime import timedelta
import os
from typing import Optional


from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Response,
    Query,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError

# from app.core.chat import get_response
from app.database.crud import get_user, get_vectorized_election_programs_from_db
from app.database.database import Session, engine
from app.database.utils.db_utils import get_session
from app.database.schema import ChatRequest, Token, User
from app.security import create_access_token
from app.utils.bearer import OAuth2PasswordBearerWithCookie
from app.utils.hashing import Hasher
from app.langchain.agent import setup_langchain_agent
from app.logging_config import configure_logging
from app.eval.main import main as eval_main
from app.llama_index.ingestion import (
    query_and_ingest_election_programs,
)
from app.llama_index.llm import verify_llm_connection
from app.llama_index.index import setup_index
from app.llama_index.agent import setup_llama_agent
from app.eval.langfuse_integration import get_langfuse_callback_manager


configure_logging()


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


@app.on_event("startup")
async def startup_event():
    global global_llama_agent
    global global_llangchain_agent
    global_llama_agent = setup_llama_agent()
    global_llangchain_agent = setup_langchain_agent()


def authenticate_user(username: str, password: str, db: Session = Depends(get_session)):
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
    db: Session = Depends(get_session),
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
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)
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
    "/chat_llama",
    summary="Chat with the AI",
    description="Get a response from the AI model based on the input text",
)
async def read_chat(chat_request: ChatRequest):
    try:
        response = await global_llama_agent.aquery(chat_request.question)
        print(response)
        if response is not None:
            return {"reply": response}
        else:
            raise HTTPException(
                status_code=500, detail="Failed to get a response from the AI model"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/chat_agent",
    summary="Chat with the AI",
    description="Get a response from the AI model based on the input text",
)
async def read_chat(
    question: str = Query(
        ..., description="Input text to get a response from the AI model"
    ),
):
    try:
        langfuse_callback = get_langfuse_callback_manager()
        response = global_llangchain_agent.invoke(
            input=question, config={"callbacks": [langfuse_callback]}
        )
        print(response)
        if response is not None:
            return response
        else:
            raise HTTPException(
                status_code=500, detail="Failed to get a response from the AI model"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/check-db-connection")
async def check_db_connection():
    try:
        with engine.connect():
            pass  # Connection was successful
        return {
            "status": "success",
            "message": "Connected to the database successfully.",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to the database: {e}",
        )


@app.get("/check-llm-connection")
async def check_llm_connection():
    try:
        verify_llm_connection()
        return {
            "status": "success",
            "message": "Connected to the LLM successfully.",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to the LLM: {e}",
        )


@app.get("/check-index-connection")
async def check_index_connection():
    try:
        setup_index()
        return {
            "status": "success",
            "message": "Setup index successfully.",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to the LLM: {e}",
        )


@app.get("/ingest-data")
async def ingest_data(party_id: int):
    try:
        # Bundestagswahl 2021 only

        election_id = 128
        query_and_ingest_election_programs(election_id=election_id, party_id=party_id)
        return {
            "status": "success",
            "message": "Ingested data.",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest data: {e}",
        )


@app.get("/create-eval")
def create_eval():
    try:
        eval_main()
        return {
            "status": "success",
            "message": "Created eval.",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create eval: {e}",
        )


@app.get("/vectorized-programs")
def get_vectorized_programs(db: Session = Depends(get_session)):
    try:
        programs = []
        vectorized_programs = get_vectorized_election_programs_from_db(db)
        if vectorized_programs is not None:
            for program in vectorized_programs:
                programs.append(
                    {
                        "id": program.id,
                        "party_id": program.party_id,
                        "election_id": program.election_id,
                        "full_name": program.full_name,
                        "label": program.label,
                    }
                )
        print(vectorized_programs)
        return programs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve vectorized programs: {e}",
        )
