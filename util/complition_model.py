from util.config import client
from util.logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)


async def complition_model(model: str, instructions: str, input: str, max_output_tokens: int = None, temperature: float = None):
    logger.info(
        "Calling complition_model | model=%s has_max_tokens=%s has_temp=%s cid=%s",
        model,
        max_output_tokens is not None,
        temperature is not None,
        get_correlation_id(),
    )
    if model in ["gpt-5-mini", "gpt-5", "gpt-5-nano"]:
        response = await client.responses.create(
            model=model,
            instructions=instructions,
            input=input,
        )
    else:
        response = await client.responses.create(
            model=model,
            instructions=instructions,
            input=input,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )
    logger.info("complition_model completed | model=%s", model)
    return response
