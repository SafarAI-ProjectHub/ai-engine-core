# 🧠 AI Engine Core – Writing & Activity Grading with GPT-4

This project powers AI-based evaluation for student writing tasks using OpenAI’s GPT-4. Designed for the [Safar AI](https://safarai.org) platform, it supports **rubric-based scoring**, **structured feedback**, and **modular architecture** for different assessment types like placement tests and writing activities.

---

## 🔍 Features

- ✅ **Modular Architecture:** Easily extendable to support multiple grading types (e.g., placement, essay).
- 🧠 **Automated Scoring:** Uses GPT-4 to grade student input based on configurable rubrics.
- 📝 **Structured Feedback:** Returns JSON with total score and detailed feedback.
- ⚙️ **Configurable Rubrics:** Criteria are defined in external files (e.g., `writingcriteria.txt`).
- 🌐 **API-Ready:** Includes FastAPI interface for integration with frontend or other services.
- 📁 **Notebook-Friendly:** Works with Jupyter notebooks for development or experimentation.

---

## 🗂 Project Structure

```
ai-engine-core/
│
├── engine/                  # Shared logic (to be added)
├── modules/
│   ├── placement/           # Placement test grading (future)
│   └── activities/          # Lesson writing activity grading (future)
│
├── config/
│   └── writingcriteria.txt  # Rubric for writing correction
│
├── api/
│   └── main.py              # FastAPI entrypoint
│
├── data/                    # Example input data (optional)
├── notebooks/               # Development notebooks (e.g., activity_dev.ipynb)
├── tests/                   # Unit tests
├── tools/                   # Utility scripts
│
├── requirements.txt         # Python dependencies
├── .env                     # OpenAI key (NOT committed)
└── README.md                # You're reading it!
```

---

## ✅ Requirements

- Python 3.9+
- OpenAI GPT-4 access key
- Virtual environment (recommended)

### 🧪 Setup Instructions

```bash
git clone https://github.com/your-org/ai-engine-core.git
cd ai-engine-core
python -m venv .
source Scripts/activate        # Or source venv/bin/activate on Linux/Mac
pip install -r requirements.txt
```

---

## 🔐 .env File

Create a `.env` file in the project root:

```env
OPEN_AI_KEY=your_openai_api_key
```

**⚠️ Do NOT share this key. Make sure `.env` is in `.gitignore`.**

---

## ▶️ Running the API (FastAPI)

```bash
python api/main.py
```

Access the API at:

```
http://0.0.0.0:9999/
```

---

## 📡 API Endpoints

### `GET /`

Simple health check.

```json
{ "Hello": "World" }
```

---

### `POST /correction`

Send a student’s writing for AI-based correction.

#### Sample Request

```json
{
  "question": "Describe your last vacation.",
  "text": "I goed to the beach and it was fun."
}
```

#### Sample Response

```json
{
  "score": 17,
  "feedback": "You made a few grammar mistakes like 'goed' instead of 'went'. Try to add more detail next time..."
}
```

> Internally uses GPT-4 and the `writingcriteria.txt` rubric to return a structured evaluation.

---

## 🧪 Rubric Format

File: `config/writingcriteria.txt`

```
1. Task Achievement / Content Relevance
2. Coherence and Cohesion
3. Lexical Resource (Vocabulary)
4. Grammatical Range and Accuracy
5. Spelling, Punctuation, Mechanics
```

Each criterion is scored on a scale of: `0`, `1`, `3`, or `5`.

---

## 🧠 Technologies Used

| Tool           | Purpose                         |
|----------------|----------------------------------|
| FastAPI        | API development                 |
| Uvicorn        | ASGI server                     |
| Pydantic       | Input validation                |
| OpenAI API     | GPT-4 language model            |
| python-dotenv  | Load secret keys from `.env`    |

---

## 🧪 Testing (Optional)

To test logic in isolation (planned):

```bash
pytest tests/test_*.py
```

You can also create and test logic via:

```python
from modules.activities.grader import get_correction
result = get_correction("Describe your last holiday.", "I goed to beach and swam.")
```

---

## 🚀 Deployment (Production)

Recommended command:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 9999 --reload
```

Or use a platform like:
- [Render](https://render.com)
- [Railway](https://railway.app)
- [Fly.io](https://fly.io)

---

## 🛡 Security Best Practices

- Use `.env` to protect your API key.
- Use HTTPS for deployed versions.
- Add authentication or rate limiting for public APIs.
- Consider containerization (e.g., Docker) for production.

---

## 📌 Future Plans

- [ ] Add `placement/` grading logic
- [ ] Refactor grading logic to `engine/`
- [ ] Enable multi-language feedback
- [ ] Add support for H5P JSON or SCORM input
- [ ] Test coverage and CI integration

---

## 🪄 License

This project is for educational and demo purposes.
