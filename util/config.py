import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pathlib import Path
from openai import AsyncOpenAI, audio
import dotenv 
import os 
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn
from util import parsingoutput as prs
from util import classes as cls
from util.logging_config import configure_logging, logging_middleware, get_logger
from safarai_chatbot.chatbot.chatbot import stream_response, system_prompt


try: 
    # Load environment variables from .env file
    dotenv.load_dotenv()

    # Configure logging once at startup
    configure_logging()
    logger = get_logger(__name__)

    key = os.getenv("OPEN_AI_KEY")
    client = AsyncOpenAI(api_key=key)

    # Check if running behind a reverse proxy (production) or directly (development)
    # Set USE_ROOT_PATH=true in .env for production with reverse proxy
    use_root_path = os.getenv("USE_ROOT_PATH", "false").lower() == "true"
    root_path = "/ai" if use_root_path else None

    # Define a simple FastAPI app
    app = FastAPI(
        root_path=root_path,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # Add logging middleware for request/response logging with correlation IDs
    app.middleware("http")(logging_middleware)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """
        Catch-all exception handler to make sure crashes are logged centrally.
        Let FastAPI's default handler deal with HTTPException separately.
        """
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )


except Exception as e:
    # At this early stage logger may not be available yet, so re-raise as HTTPException
    raise HTTPException(status_code=500, detail=str(e))