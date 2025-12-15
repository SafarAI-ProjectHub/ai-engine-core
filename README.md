## SafarAI AI Engine Core

SafarAI AI Engine Core is a FastAPI-based backend that powers English-learning features such as audiobook generation, text‑to‑speech, translation, writing correction, chatbots, and real‑time spoken conversation practice.

The service wraps OpenAI models behind a consistent JSON API with shared response envelopes, token accounting, and utilities for managing generated audio files.

---

## Project Structure

[main.py](main.py) is the main entrypoint used in local development and most deployments. It wires together the core app from `util.config` and includes all routers.

- `main.py` – starts the FastAPI app and includes all routers
- `util/`
  - `config.py` – app factory, Async OpenAI client, CORS, `root_path` handling, shared imports
  - `classes.py` – shared request/response models and the generic `ApiResponse` envelope
  - `audio_model.py`, `audio_utils.py` – helpers for TTS and audio duration
  - `complition_model.py`, `parsingoutput.py`, `token_utils.py` – LLM response helpers and token counting
  - `del_speech_files.py` – maintenance endpoint for cleaning up generated audio
- `EndPoint/`
  - `Endpoint.py` – alternative entrypoint wiring the same routers (used in some deployments)
  - `audio_book.py` – audiobook generation endpoint
  - `text_to_speech.py` – generic TTS endpoint
  - `translation.py` – text translation endpoint
  - `correction.py` – writing correction/scoring endpoint
  - `chatbot.py` – streaming chatbot endpoint (server‑sent events)
  - `new_chatbot.py` – OpenAI Conversations API based chatbot endpoints
- `safarai_realtime/backend/session.py` – real‑time WebRTC session helper endpoints
- `safarai_realtime/frontend/` – HTML frontend for the real‑time speaking practice
- `safarai_chatbot/` – HTML + backend helpers for chatbot frontends
- `speechfiles/` – generated `.mp3` audio files (audiobook and TTS outputs)
- `Docs/` – additional documentation (deployment, legacy correction docs, audiobook design)

---

## Installation & Setup

### Requirements

- Python 3.9+
- OpenAI API key with access to the referenced models

### Install

```bash
git clone https://github.com/SafarAI-ProjectHub/ai-engine-core.git
cd ai-engine-core

python -m venv venv
venv\Scripts\activate            # Windows
# or: source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

### Environment variables

Create a `.env` file in the project root:

```env
OPEN_AI_KEY=your_openai_api_key
# Optional: mount the API under /ai when running behind a reverse proxy
USE_ROOT_PATH=true
```

- `OPEN_AI_KEY` is required by `util.config.client` and by the `new_chatbot` module.
- `USE_ROOT_PATH`:
  - if `true` → FastAPI is created with `root_path="/ai"` so all URLs are effectively mounted under `/ai` when reverse‑proxied.
  - if `false` (default) → the app is mounted at `/`.

---

## Running the API

### Local development

The simplest way to run everything locally is:

```bash
python main.py
```

This starts Uvicorn on:

- `http://0.0.0.0:9999/` (no root path)
- or via your reverse proxy as configured if `USE_ROOT_PATH=true`

You can also run Uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 9999 --reload
```

### Interactive API docs

FastAPI Swagger UI and ReDoc are enabled in `util.config`:

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI schema: `/openapi.json`

If `USE_ROOT_PATH=true` and your reverse proxy forwards `/ai/` to this app, the docs will be available at:

- `https://your-domain/ai/docs`
- `https://your-domain/ai/redoc`

---

## Shared API Envelope & Models

All JSON endpoints (except the streaming chatbot endpoint) return a common envelope defined in `util/classes.py`:

- `ApiResponse[T]`
  - `success: bool` – `true` if the endpoint completed successfully
  - `data: T` – endpoint‑specific payload (see per‑endpoint docs)
  - `usage: Usage | null`
    - `tokens: int | null` – approximate token usage for the request/response
    - `duration_seconds: float | null` – audio duration in seconds where applicable
    - `session_seconds: float | null` – for long‑running sessions (currently unused in most endpoints)
  - `meta: Meta | null`
    - `endpoint_key: string | null` – stable key such as `"audio_book"`, `"translation"`, `"correction"`, etc.
    - `extra: object | null` – optional additional metadata

The request/response models used inside `data` include:

- `AduioBookRequest` / `AduioBookResponse`
- `TextToSpeechRequest` / `TextToSpeechResponse`
- `translationRequest` / `translationResponse`
- `CorrectionRequest` / `CorrectionResponse`
- `ChatbotRequest` / `ChatbotResponse`
- `NewChatbotRequest` / `NewChatbotResponse`

A detailed, per‑model breakdown is provided in the API documentation file described below.

---

## Endpoints Overview

All paths below are shown without any `root_path`. If `USE_ROOT_PATH=true`, prefix them with `/ai` when calling through your reverse proxy (for example `/ai/audio-book`).

High‑level list (full details in `Docs/API_Endpoints.md`):

- `GET /` – simple health check
- `POST /audio-book` – generate an audiobook from text using GPT + TTS
- `POST /text-to-speech` – generic text‑to‑speech for arbitrary text
- `POST /translation` – translate text into a target language with a JSON response
- `POST /correction` – score and correct writing using rubric‑based evaluation
- `POST /chatbot/stream` – streaming chatbot responses via server‑sent events
- `GET /new_conversation` – create a new OpenAI conversation for the guided English chatbot
- `DELETE /delete_conversation` – delete an existing OpenAI conversation
- `POST /chatbot` – send a message to the guided English chatbot in an existing conversation
- `GET /del-speech-files` – delete all generated `.mp3` files under `speechfiles/`
- Real‑time speaking practice (`/realtime` prefix, see below)
  - `GET /realtime/new` – serve the WebRTC call frontend
  - `POST /realtime/session` – create a new OpenAI real‑time session
  - `POST /realtime/keep-alive` – keep a real‑time session alive
  - `POST /realtime/close` – close a real‑time session and remove it from memory
  - `GET /realtime/debug/sessions` – inspect active real‑time sessions (debug only)

For complete schemas, examples, and behavior notes, see:

- [Docs/API_Endpoints.md](Docs/API_Endpoints.md)

---

## Additional Documentation

Under `Docs/` you will find:

- `AI_Engine_Deployment_Guide.md` – step‑by‑step deployment to Ubuntu + Apache with systemd
- `API_Correction_Documentation.md` – focused documentation for an earlier version of the `/correction` API
- `Audiobook_Enhancement_Documentation.md` – design notes and plans for richer audiobook generation

`Docs/API_Endpoints.md` is intended to be the canonical source of truth for the current endpoints; other documents describe historical behavior, deployment, or design ideas.

---

## License & Usage

This codebase is intended for educational and SafarAI project use. Ensure you keep your OpenAI API keys secret and apply appropriate authentication, logging, and rate limiting before exposing the service on the public internet.


