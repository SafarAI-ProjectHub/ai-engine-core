from dis import Instruction
from util.config import client, cls, HTTPException, APIRouter, prs
from util.complition_model import complition_model

translation_router  = APIRouter(tags=["translation"])

@translation_router.post("/translation", response_model=cls.translationResponse)
async def translate_text(request: cls.translationRequest):
    try:

        Instruction = f"""
            You are a translation assistant. Your ONLY task is to translate the user's text to {request.target_language}.
            Do NOT answer, explain, or comment on the text. Do NOT provide any information except the translation and a brief description of the translated text.
            If the input is a question, ONLY translate the question—do NOT answer it.
            Return the translation in JSON format with these keys: {{ "translation": "string", "info": "string" }}.
            Do NOT return the original text, any answers, or any extra information.

            ##EXAMPLES##
            input: "How are you?"
            output: {{ "translation": "مرحباً، كيف حالك؟", "info": "سؤال شائع للتحية." }}

            input: "What is the capital of France?"
            output: {{ "translation": "ما هي عاصمة فرنسا؟", "info": "سؤال عن عاصمة دولة." }}

            input: "Translate: I love programming."
            output: {{ "translation": "أحب البرمجة.", "info": "جملة تعبر عن الحب للبرمجة." }}
            """

        response = await complition_model (
            model = "gpt-5-nano",
            instructions = Instruction,
            input = request.text,
        )
        # Parse the response to extract JSON
        response_data = prs.extract_json_from_response(response)
        # Return the translation response model
        return cls.translationResponse(
            translation=response_data.get("translation", "error:translation not found"),
            info=response_data.get("info", "error:info not found")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))