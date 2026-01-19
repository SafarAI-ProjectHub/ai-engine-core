## SafarAI AI Engine – API Endpoints

This document describes the current FastAPI endpoints exposed by the SafarAI AI Engine Core, based strictly on the code in `main.py`, `EndPoint/`, `util/`, and `safarai_realtime/backend/session.py`.

All JSON endpoints (except the streaming chatbot) use the shared `ApiResponse` envelope from `util/classes.py`:

```text
ApiResponse[T] {
  success: bool
  data: T                      # endpoint-specific payload
  usage?: {
    tokens?: int
    duration_seconds?: float
    session_seconds?: float
  }
  meta?: {
    endpoint_key?: string      # e.g. "audio_book", "translation"
    extra?: object | null
  }
}
```

When `USE_ROOT_PATH=true` in `.env`, the FastAPI app is mounted at `root_path="/ai"`. In that case, all paths below should be called with an `/ai` prefix when accessed through your reverse proxy (for example `/ai/audio-book` instead of `/audio-book`).

---

## 1. Health Check

### `GET /`

Simple health check endpoint.

- **Request body**: none
- **Response**:

```json
{
  "Hello": "World"
}
```

> Note: This root route does **not** use the `ApiResponse` envelope in `main.py`. The alternative entrypoint `EndPoint/Endpoint.py` wraps this in `ApiResponse`, so the exact shape depends on which entrypoint you run.

---

## 2. Audiobook Generation

Defined in `EndPoint/audio_book.py`.

### `POST /audio-book`

Generate an audiobook from input text using an LLM followed by TTS. The generated `.mp3` file is stored under the `speechfiles/` directory as `audio-book_{id}.mp3`.

- **Request body** (`AduioBookRequest`):

```json
{
  "text": "Your story or content here",
  "id": 1,
  "voice": "nova",
  "accent": "any free-form accent description"
}
```

- `text` (string, required): The text to turn into an audiobook.
- `id` (integer, required): Identifier used in the output filename (`audio-book_{id}.mp3`).
- `voice` (string, optional, default `"nova"`): Voice identifier for the TTS model.
- `accent` (string, required by the model schema): Currently not used in `audio_book.py` but reserved for future use.

- **Response body** (`ApiResponse<AduioBookResponse>`):

```json
{
  "success": true,
  "data": {
    "status": "success",
    "message": "Audio book created successfully",
    "text": "LLM-generated expanded / improved story text",
    "file_path": "speechfiles/audio-book_1.mp3",
    "token_count": 1234,
    "duration": 87.32
  },
  "usage": {
    "tokens": 1234,
    "duration_seconds": 87.32
  },
  "meta": {
    "endpoint_key": "audio_book",
    "extra": null
  }
}
```

On error, `success` is `false` and `data.status` is `"False"`; `file_path` is empty and `token_count` / `duration` are `0`.

---

## 3. Text-to-Speech

Defined in `EndPoint/text_to_speech.py`.

### `POST /text-to-speech`

Convert arbitrary text into speech, stored as `speech_{id}.mp3` under `speechfiles/`.

- **Request body** (`TextToSpeechRequest`):

```json
{
  "text": "Text to read",
  "id": 1,
  "voice": "nova",
  "accent": "British English"
}
```

- `text` (string, required): The text to be spoken.
- `id` (integer, required): Identifier used in the output filename (`speech_{id}.mp3`).
- `voice` (string, optional, default `"nova"`): TTS voice.
- `accent` (string, required): Accent description; used to build the TTS instructions.

The endpoint constructs internal instructions such as:

> Please read the text in a clear and engaging manner... you should talk in this accent: `{accent}`.

- **Response body** (`ApiResponse<TextToSpeechResponse>`):

```json
{
  "success": true,
  "data": {
    "status": "success",
    "message": "Speech synthesis complete",
    "file_path": "speechfiles/speech_1.mp3",
    "token_count": 123,
    "duration": 12.45
  },
  "usage": {
    "tokens": 123,
    "duration_seconds": 12.45
  },
  "meta": {
    "endpoint_key": "tts",
    "extra": null
  }
}
```

On error, `success` is `false`, `data.status` is `"False"`, and the file path / counts are empty or zeroed.

---

## 4. Translation

Defined in `EndPoint/translation.py`.

### `POST /translation`

Translate text into a target language. The model is instructed to return strict JSON with `translation` and `info` fields.

- **Request body** (`translationRequest`):

```json
{
  "text": "How are you?",
  "target_language": "Arabic"
}
```

- `text` (string, required): Source text to translate.
- `target_language` (string, required): Target language description (e.g., `"Arabic"`, `"French"`).

- **Response body** (`ApiResponse<translationResponse>`):

```json
{
  "success": true,
  "data": {
    "status": "success",
    "translation": "مرحباً، كيف حالك؟",
    "info": "سؤال شائع للتحية.",
    "token_count": 57
  },
  "usage": {
    "tokens": 57
  },
  "meta": {
    "endpoint_key": "translation",
    "extra": null
  }
}
```

On error, `success` is `false`, and both `translation` and `info` in `data` contain an error message.

---

## 5. Writing Correction

Defined in `EndPoint/correction.py`.

### `POST /correction`

Evaluate and correct a student’s written response based on rubric criteria and example feedback loaded from:

- `config/activitywritingcriteria.txt`
- `config/writingexamples.txt`

The model is instructed to return JSON with `score` and `feedback`.

- **Request body** (`CorrectionRequest`):

```json
{
  "question": "Describe your last vacation.",
  "text": "I goed to the beach and it was fun."
}
```

- `question` (string, required): The writing prompt or question.
- `text` (string, required): The student’s answer to be evaluated.

- **Response body** (`ApiResponse<CorrectionResponse>`):

```json
{
  "success": true,
  "data": {
    "status": "success",
    "score": 18,
    "feedback": "You made a few grammar mistakes like 'goed' instead of 'went'. Try to add more detail.",
    "token_count": 210
  },
  "usage": {
    "tokens": 210
  },
  "meta": {
    "endpoint_key": "correction",
    "extra": null
  }
}
```

- `score` is an integer derived from the model output (non‑numeric values are safely coerced to `0`).
- `feedback` is textual feedback summarizing strengths and weaknesses.

On error, `success` is `false`, `score` is `0`, and `feedback` contains the error message.

---

## 6. Streaming Chatbot

Defined in `EndPoint/chatbot.py`.

### `POST /chatbot/stream`

Stream chat responses from the SafarAI learning assistant using server‑sent events (SSE). This endpoint is tailored for frontends that need token‑by‑token or chunked responses.

- **Request body** (`ChatbotRequest`):

```json
{
  "message": "Explain the difference between 'few' and 'a few'.",
  "conversation_history": [
    { "role": "user", "content": "Hi!" },
    { "role": "assistant", "content": "Hello! How can I help you with English today?" }
  ]
}
```

- `message` (string, required): The user’s new message.
- `conversation_history` (array, optional, default `[]`):
  - Each item is an object with:
    - `role`: `"user"` or `"assistant"`
    - `content`: string

The endpoint:

1. Counts tokens for the current message and all `conversation_history` entries.
2. Builds a list of messages including a system prompt (`system_prompt` from `safarai_chatbot.chatbot.chatbot`).
3. Streams chunks from `stream_response(messages)`.

- **Response**:

  - On success: a `StreamingResponse` with `media_type="text/plain"` containing SSE‑formatted lines:

    ```text
    data: {"content": "First chunk...", "done": false}

    data: {"content": "Next chunk...", "done": false}

    ...

    data: {"content": "", "done": true, "token_count": 345}

    ```

  - On internal errors while streaming, the generator yields:

    ```text
    data: {"error": "error message", "done": true}

    ```

  - On top‑level exceptions (before streaming starts), the endpoint returns an `ApiResponse<ChatbotResponse>` with `success=false` and:
    - `data.status = "False"`
    - `data.response` containing the error message
    - `data.conversation_history` echoing the input history
    - `usage.tokens = 0`

Because the normal path is a plain streaming response, **do not** expect a JSON `ApiResponse` on success for this endpoint.

---

## 7. Guided English Chatbot (OpenAI Conversations API)

Defined in `EndPoint/new_chatbot.py`.

This set of endpoints uses the OpenAI Conversations API to maintain server‑side conversation state.

### 7.1 `GET /new_conversation`

Create a new OpenAI conversation for the guided English chatbot.

- **Request body**: none
- **Response** (`ApiResponse<object>`):

```json
{
  "success": true,
  "data": {
    "conversation_id": "conv_1234567890"
  },
  "usage": null,
  "meta": {
    "endpoint_key": "new_chatbot_new_conversation",
    "extra": null
  }
}
```

The `conversation_id` is the ID returned by `client.conversations.create()` and must be sent with subsequent chat requests.

### 7.2 `DELETE /delete_conversation`

Delete an existing OpenAI conversation using the REST API.

- **Query parameters**:
  - `conversation_id` (string, required): ID of the conversation to delete.

- **Request body**: none

- **Response** (`ApiResponse<object>`):

On success (HTTP 200 from OpenAI):

```json
{
  "success": true,
  "data": {
    "message": "Conversation deleted successfully",
    "status": "success"
  },
  "usage": null,
  "meta": {
    "endpoint_key": "new_chatbot_delete_conversation",
    "extra": null
  }
}
```

On failure (non‑200 from OpenAI):

```json
{
  "success": false,
  "data": {
    "message": "Failed to delete conversation",
    "status": "error",
    "details": { /* body returned by OpenAI */ }
  },
  "usage": null,
  "meta": {
    "endpoint_key": "new_chatbot_delete_conversation",
    "extra": null
  }
}
```

Top‑level exceptions are surfaced as `HTTPException(500)`.

### 7.3 `POST /chatbot`

Send a message to the guided English chatbot within an existing conversation.

> This endpoint shares the path prefix `/chatbot` with the streaming endpoint but uses a **different router** and a different request model; there is no conflict because the streaming endpoint is `/chatbot/stream`.

- **Request body** (`NewChatbotRequest`):

```json
{
  "message": "What is the difference between 'few' and 'a few'?",
  "conversation_id": "conv_1234567890"
}
```

- `message` (string, required): User message.
- `conversation_id` (string, required): ID from `/new_conversation`.

The endpoint uses a fixed system prompt that:

- limits answers to English‑learning topics,
- enables translation to and from Arabic,
- explains single words in English and Arabic,
- corrects typos,
- targets kids and teenagers.

- **Response body** (`ApiResponse<NewChatbotResponse>`):

```json
{
  "success": true,
  "data": {
    "status": "success",
    "response": "Explanation or answer from the assistant...",
    "token_count": 89
  },
  "usage": {
    "tokens": 89
  },
  "meta": {
    "endpoint_key": "new_chatbot_chat",
    "extra": null
  }
}
```

On error, `success` is `false`, `data.status` is `"False"`, and `data.response` contains the error message.

---

## 8. Real-time Speaking Practice (WebRTC + OpenAI Realtime)

Defined in `safarai_realtime/backend/session.py`. All endpoints here are attached to the `realtime` router with prefix `/realtime`.

### 8.1 `GET /realtime/new`

Serve the HTML page for the enhanced frontend with the “talking orb”.

- **Request body**: none
- **Response**: `FileResponse` serving `newcall.html` from the `safarai_realtime/backend` directory.

This is intended to be opened in a browser.

### 8.2 `POST /realtime/session`

Create a new OpenAI real‑time WebRTC session with customized instructions for level, theme, topic, and tutor personality.

- **Request body** (JSON):

```json
{
  "level": "Intermediate",
  "theme": "Daily Life",
  "topic": "Ordering food",
  "personality": "Friendly Mentor",
  "avatar": "friendly"
}
```

All fields are optional in the code; when missing, the following defaults are used:

- `level`: `"Intermediate"`
- `theme`: `"Daily Life"`
- `topic`: `""` (no specific topic)
- `personality`: `"Friendly Mentor"`
- `avatar`: `"friendly"`

The endpoint:

1. Builds an instruction string combining:
   - level‑specific guidance,
   - theme prompts,
   - personality description,
   - detailed correction policies.
2. Sends a POST request to `https://api.openai.com/v1/realtime/sessions` using your `OPEN_AI_KEY`.
3. Stores the returned session metadata in an in‑memory `active_sessions` dict keyed by `id`.

- **Response body**:

The JSON body returned by the OpenAI Realtime API, extended with:

```json
{
  "last_activity": 1734300000.123  // Unix timestamp
}
```

On HTTP errors from OpenAI, the response is a `JSONResponse` with the same status code and an `"error"` field containing the upstream body.

### 8.3 `POST /realtime/keep-alive`

Update the last‑activity timestamp of an existing session to keep it “alive” in memory.

- **Request body**:

```json
{
  "session_id": "sess_1234567890"
}
```

If the `session_id` exists in `active_sessions`, the endpoint updates its `last_activity` and returns:

```json
{
  "status": "Session kept alive",
  "timestamp": 1734300000.456
}
```

If the session is not found:

```json
{
  "error": "Session not found"
}
```

with HTTP status `404`.

### 8.4 `POST /realtime/close`

Close (remove) an active WebRTC session from memory.

- **Request body**:

```json
{
  "session_id": "sess_1234567890"
}
```

Responses:

- When `session_id` is missing:

  ```json
  {
    "error": "session_id is required"
  }
  ```

  with HTTP status `400`.

- When the session exists:

  ```json
  {
    "status": "Session closed"
  }
  ```

- When the session does not exist:

  ```json
  {
    "error": "Session not found"
  }
  ```

  with HTTP status `404`.

On unexpected exceptions, the endpoint returns HTTP `500` with an `"error"` field.

### 8.5 `GET /realtime/debug/sessions`

Debug endpoint to inspect active sessions in memory.

- **Request body**: none

- **Response**:

```json
{
  "active_sessions_count": 1,
  "session_ids": ["sess_1234567890"],
  "sessions": {
    "sess_1234567890": {
      "...": "full session object from OpenAI plus last_activity"
    }
  }
}
```

This endpoint is intended for debugging and should generally be protected or disabled in production.

---

## 9. Maintenance – Delete Speech Files

Defined in `util/del_speech_files.py`.

### `GET /del-speech-files`

Delete all `.mp3` files in the `speechfiles/` directory.

- **Request body**: none

The endpoint:

1. Resolves `speechfiles/` relative to the project root.
2. Deletes all files matching `*.mp3`.
3. Logs the number of deleted files.

- **Response body** (`ApiResponse<object>`):

```json
{
  "success": true,
  "data": {
    "message": "Speech files deleted successfully",
    "deleted": 3
  },
  "usage": null,
  "meta": {
    "endpoint_key": "del_speech_files",
    "extra": null
  }
}
```

On errors (for example, filesystem issues), the endpoint raises `HTTPException(500)` with a `"detail"` message.

---

## 10. Models Overview (from `util/classes.py`)

For convenience, here is a concise list of request and response models used across the API:

- `AduioBookRequest`:
  - `text: str`
  - `id: int`
  - `voice: str = "nova"`
  - `accent: str`

- `AduioBookResponse`:
  - `status: str`
  - `message: str`
  - `text: str`
  - `file_path: str`
  - `token_count: int`
  - `duration: float`

- `TextToSpeechRequest`:
  - `text: str`
  - `id: int`
  - `voice: str = "nova"`
  - `accent: str`

- `TextToSpeechResponse`:
  - `status: str`
  - `message: str`
  - `file_path: str`
  - `token_count: int`
  - `duration: float`

- `translationRequest`:
  - `text: str`
  - `target_language: str`

- `translationResponse`:
  - `status: str`
  - `translation: str`
  - `info: str`
  - `token_count: int`

- `CorrectionRequest`:
  - `question: str`
  - `text: str`

- `CorrectionResponse`:
  - `status: str`
  - `score: int`
  - `feedback: str`
  - `token_count: int`

- `ChatbotRequest`:
  - `message: str`
  - `conversation_history: list = []`

- `ChatbotResponse`:
  - `status: str`
  - `response: str`
  - `conversation_history: list`
  - `token_count: int`

- `NewChatbotRequest`:
  - `message: str`
  - `conversation_id: str`

- `NewChatbotResponse`:
  - `status: str`
  - `response: str`
  - `token_count: int`

These models, together with the `ApiResponse` envelope, define the contract for all JSON‑based endpoints in this project.


