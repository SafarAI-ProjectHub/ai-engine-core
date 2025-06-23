from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import uvicorn
import os
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

key = os.getenv("OPEN_AI_KEY")
client = openai.Client(api_key = key)
with open("config/activitywritingcriteria.txt", "r", encoding="utf-8") as file:
    # read the file content
    criteria = file.read()

app = FastAPI(root_path="/ai")

@app.get("/")
def read_root():
    return {"Hello": "World"}

class CorrectionRequest(BaseModel):
    question: str
    text: str

#corrction endpoint
@app.post("/correction")
def get_correction(request: CorrectionRequest):
    try:
        response = client.chat.completions.create(
        model = "gpt-4",
        temperature= 0,
        messages = [
            {"role" : "system", "content" : "you are a helpful assistant that provides feedback on writing."},
            {"role" : "system", "content" : "you will be given the question and a piece of text and a set of criteria. you will provide a correction for the text based on the criteria."},
            {"role" : "system", "content" : "Grade the answer for each criterion from 0, 1, 3, or 5 as described. sum the scores for a total out of 25"},
            {"role" : "system", "content" : "return the correction the following format: {'score': int, 'feedback': str}"},
            {"role" : "system", "content" : "If any of the criteria do not apply to this answer, do not penalize the student for those criteria."},
            {"role" : "system", "content" : "dont be so strict, be lenient and give the student the benefit of the doubt."},
            {"role" : "user", "content" : f"Here is the question: {request.question}\n\nHere is the text: {request.text}\n\nHere are the criteria: {criteria}\n\nPlease provide a correction for the text based on the criteria."}

        ]
    )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))



# uvicorn.run(app, host = "0.0.0.0", port = 9999)