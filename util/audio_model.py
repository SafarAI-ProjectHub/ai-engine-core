from util.config import client
from util.logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)


async def audio_model(model: str, voice: str, instructions: str, input: str, speech_file_path: str):
    logger.info(
        "Calling audio_model | model=%s voice=%s path=%s cid=%s",
        model,
        voice,
        speech_file_path,
        get_correlation_id(),
    )
    async with client.audio.speech.with_streaming_response.create(
        model=model,
        voice=voice,
        instructions=instructions,
        input=input
    ) as response:
        await response.stream_to_file(speech_file_path)
    logger.info("audio_model completed | path=%s", speech_file_path)
