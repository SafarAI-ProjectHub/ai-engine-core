from util.config import client

async def audio_model(model: str, voice: str, instructions: str, input: str, speech_file_path: str):
    async with client.audio.speech.with_streaming_response.create(
        model=model,
        voice=voice,
        instructions=instructions,
        input=input
    ) as response:
        await response.stream_to_file(speech_file_path)
