from dis import Instruction
from util.config import client, cls, HTTPException, APIRouter, prs
from util.complition_model import complition_model
from util.token_utils import count_tokens
from util.logging_config import get_logger, get_correlation_id

translation_router  = APIRouter(tags=["translation"])
logger = get_logger(__name__)

@translation_router.post("/translation", response_model=cls.ApiResponse)
async def translate_text(request: cls.translationRequest):
    try:
        # Log incoming text and target language
        logger.info(
            "Translation request | target_language=%s cid=%s",
            request.target_language,
            get_correlation_id(),
        )
        logger.info("Translation request text: %s", request.text)
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

        response = await complition_model(
            model = "gpt-5-nano",
            instructions = Instruction,
            input = request.text,
        )
        # Parse the response to extract JSON
        response_data = prs.extract_json_from_response(response)
        token_count = (
            count_tokens(request.text, "gpt-5-nano")
            + count_tokens(response_data.get("translation", ""), "gpt-5-nano")
            + count_tokens(response_data.get("info", ""), "gpt-5-nano")
        )

        # Build inner data payload
        data = cls.translationResponse(
            status="success",
            translation=response_data.get("translation", "error:translation not found"),
            info=response_data.get("info", "error:info not found"),
            token_count=token_count,
        )
        usage = cls.Usage(tokens=token_count)

        # Log model response content
        logger.info(
            "Translation complete | target_language=%s tokens=%s",
            request.target_language,
            token_count,
        )
        logger.info(
            "Translation response | translation=%s info=%s",
            data.translation,
            data.info,
        )

        return cls.build_response(
            data=data,
            usage=usage,
            endpoint_key="translation",
        )
    except Exception as e:
        logger.exception("Error in translate_text endpoint: %s", e)
        data = cls.translationResponse(
            status="False",
            translation=f"An error occurred while processing the request: {str(e)}",
            info=f"An error occurred while processing the request: {str(e)}",
            token_count=0,
        )
        usage = cls.Usage(tokens=0)
        return cls.build_response(
            data=data,
            usage=usage,
            endpoint_key="translation",
            success=False,
        )
