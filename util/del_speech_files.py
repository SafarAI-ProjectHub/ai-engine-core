import os
from pathlib import Path
from util.config import Path as ConfigPath, APIRouter, HTTPException, cls
from util.logging_config import get_logger

del_speech_files_router = APIRouter(tags=["del-speech-files"])
logger = get_logger(__name__)


@del_speech_files_router.get("/del-speech-files")
async def del_speech_files():
    try:
        logger.info("Deleting speech files...")
        speech_files_path = ConfigPath(__file__).parent.parent / "speechfiles"
        speech_files = list(speech_files_path.glob("*.mp3"))
        for speech_file in speech_files:
            os.remove(speech_file)
        logger.info("Deleted %s speech files", len(speech_files))
        data = {"message": "Speech files deleted successfully", "deleted": len(speech_files)}
        return cls.build_response(
            data=data,
            endpoint_key="del_speech_files",
        )
    except Exception as e:
        logger.exception("Error deleting speech files: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
