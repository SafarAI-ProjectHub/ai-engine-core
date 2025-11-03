import os
from pathlib import Path
from util.config import Path, APIRouter, HTTPException
import logging

logging.basicConfig(level=logging.INFO)
del_speech_files_router = APIRouter(tags=["del-speech-files"])

@del_speech_files_router.get("/del-speech-files")
async def del_speech_files():
    try:
        logging.info("Deleting speech files...")
        speech_files_path = Path(__file__).parent.parent / "speechfiles"
        speech_files = list(speech_files_path.glob("*.mp3"))
        for speech_file in speech_files:
            os.remove(speech_file)
        logging.info(f"Deleted {len(speech_files)} speech files")
        return {"message": "Speech files deleted successfully"}
    except Exception as e:
        logging.error(f"Error deleting speech files: {e}")
        raise HTTPException(status_code=500, detail=str(e))