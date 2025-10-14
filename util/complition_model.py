from util.config import client

async def complition_model(model: str, instructions: str, input: str, max_output_tokens: int = None, temperature: float = None) -> str:
    if model in ["gpt-5-mini", "gpt-5", "gpt-5-nano"]:
        response = await client.responses.create(
            model=model,
            instructions=instructions,
            input = input
        )
    else:
        response = await client.responses.create(
            model=model,
            instructions=instructions,
            input = input,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )
    return response
