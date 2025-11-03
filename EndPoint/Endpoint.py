import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util.config import app, uvicorn
from safarai_realtime.backend import realtime
from audio_book import audio_book_router as audio_book_router
from text_to_speech import text_to_speech_router as text_to_speech_router
from translation import translation_router as translation_router
from correction import correction_router as correction_router
from chatbot import chatbot_router as chatbot_router
from new_chatbot import new_chatbot_router
from util.del_speech_files import del_speech_files_router as del_speech_files_router


@app.get("/")
def read_root():
    return {"Hello": "World"}
app.include_router(new_chatbot_router)

app.include_router(realtime)

app.include_router(audio_book_router)

app.include_router(text_to_speech_router)

app.include_router(translation_router)

app.include_router(correction_router)

app.include_router(chatbot_router)

app.include_router(del_speech_files_router)
    
if __name__ == "__main__":
    uvicorn.run("Endpoint:app", host = "0.0.0.0", port = 9999, reload=True)


