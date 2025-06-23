# 📝 Writing Correction API (FastAPI + GPT-4)

A FastAPI-based web service that provides AI-powered feedback and grading for student writing using OpenAI's GPT-4 API. This project reads evaluation criteria from a file, processes student input, and returns a detailed score and feedback response.

---

## 📁 Project Structure

```
.
├── main.py                # Main FastAPI application
├── writingcriteria.txt    # Text file with grading criteria
├── requirements.txt       # Python dependencies
├── .env                   # Contains the OpenAI API key (not committed)
├── Include/
├── Lib/
└── Scripts/               # Virtual environment executables
```

---

## ✅ Prerequisites

- Python 3.9+
- An OpenAI API key
- Git (optional for version control)
- Recommended: Virtual environment (already included)

---

## ⚙️ Virtual Environment Setup

This repo includes a virtual environment. If you'd rather set up a fresh one:

### 1. Create a Virtual Environment

```bash
python -m venv .
```

### 2. Activate the Environment

- **PowerShell:**
  ```powershell
  .\Scripts\Activate.ps1
  ```
  _Tip: If blocked by policy, run:_
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

- **Command Prompt:**
  ```cmd
  Scripts\activate.bat
  ```

- **Git Bash / WSL:**
  ```bash
  source Scripts/activate
  ```

---

## 📦 Installing Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Setup Your `.env` File

Create a file named `.env` in the root directory with:

```env
OPEN_AI_KEY=your_openai_api_key
```

> **Never share or hardcode your API key.** Use `.env` for security.
> **Add .env to .gitignore.**



---

## ▶️ Running the Application

Start the API with:

```bash
python main.py
```

Once running, the server will be available at:

```
http://0.0.0.0:9999/
```

---

## 📡 API Endpoints

### `GET /`

Health check endpoint.

```json
{ "Hello": "World" }
```

---

### `POST /correction`

Submit a writing task for AI correction.

#### Request JSON

```json
{
  "question": "Describe your last vacation.",
  "text": "I goed to the beach and it was fun."
}
```

#### Response JSON

```json
{
  "score": 17,
  "feedback": "You made a few grammar mistakes like 'goed' instead of 'went'. Try to add more detail next time..."
}
```

#### What It Does

- Reads grading criteria from `writingcriteria.txt`
- Builds a structured GPT-4 prompt
- Receives and returns a JSON object with:
  - `score` (0–25 total)
  - `feedback` (textual advice)

---

## 🧠 Technologies Used

| Tool        | Purpose                      |
|-------------|------------------------------|
| FastAPI     | API development              |
| Uvicorn     | ASGI server                  |
| Pydantic    | Input data validation        |
| OpenAI API  | AI-powered feedback engine   |
| python-dotenv | Loads environment variables|

---

## 🧪 Criteria File Format

**writingcriteria.txt**

You can define your own evaluation rubric, e.g.:

```
1. Grammar and Syntax
2. Coherence
3. Relevance
4. Vocabulary
5. Structure
```

The system grades each on a scale: `0, 1, 3, or 5` and calculates a total score.

---

## ✅ Best Practices

- ✔ Keep sensitive keys in `.env`
- ✔ Use `requirements.txt` to share dependencies
- ✔ Use `POST` for any state-changing operations
- ✔ Validate all user inputs with `Pydantic`
- ✔ Avoid overly strict grading — your prompt already includes leniency

---

## 🛡 Security Note

For production:
- Never expose raw OpenAI keys publicly
- Use HTTPS
- Add API authentication or rate limiting
- Consider containerization (e.g., Docker)

---

## 📤 Deployment (Optional)

For production environments, use:

```bash
uvicorn main:app --host 0.0.0.0 --port 9999 --reload
```

You can also use Docker or deploy to platforms like:
- [Render](https://render.com)
- [Railway](https://railway.app)
- [Fly.io](https://fly.io)

---

## 🪄 License

For educational and demo purposes.

---

## ✍️ Author

**Abdallah Esam Al-Nsour**  
Computer Engineer & AI Enthusiast

---