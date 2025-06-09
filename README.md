# AI Engine Core

`ai-engine-core` is the central module powering AI-based evaluation tasks in the Safar platform. It includes shared logic for automated correction, structured feedback generation, and rubric-based scoring using large language models such as GPT-4.

## 🔍 Features

- **Modular Architecture:** Supports multiple AI modules (e.g., placement tests, lesson activity grading).
- **Automated Scoring:** Uses GPT-4 to evaluate student inputs against configurable rubrics.
- **Feedback Generation:** Returns structured and human-readable feedback.
- **Extensible Criteria:** Reads evaluation rubrics from external files.
- **JSON Output Support:** Enables integration with other systems or frontends.
- **Notebooks + API Integration:** Development-friendly structure supporting both notebooks and API endpoints.

---

## 🧠 Project Structure

```
ai-engine-core/
│
├── engine/                # Shared AI logic and utility tools
├── modules/
│   ├── placement_test/    # Placement exam scoring
│   └── lesson_activities/ # Lesson writing activity scoring
├── config/                # Rubric and model configuration
├── api/                   # Optional FastAPI/Flask integration
├── tests/                 # Unit tests
├── data/                  # Sample input data
├── notebooks/             # Development notebooks
└── tools/                 # Utility scripts (e.g., H5P processors)
```

---

## ⚙️ Requirements

- Python 3.x
- [openai](https://pypi.org/project/openai/)
- An OpenAI API Key with GPT-4 access

Install dependencies:
```bash
pip install openai
```

Set your OpenAI key via environment variable or `.env`:
```bash
export OPENAI_API_KEY=your-key-here
```

---

## 🛡️ Security Note

**Do not share your OpenAI API key publicly.**  
Always use `.env` or environment variables to store sensitive keys.

---

# ✍️ Module: Lesson Activity Grader

This module evaluates short student writing answers (e.g., in Safar lessons) based on five criteria.

### Rubric Criteria

The rubric is located at:
```
config/activity_grading_criteria.txt
```

It includes the following criteria, each scored as 0, 1, 3, or 5:

1. **Task Achievement / Content Relevance**
2. **Coherence and Cohesion**
3. **Lexical Resource (Vocabulary Use)**
4. **Grammatical Range and Accuracy**
5. **Spelling, Punctuation, and Mechanics**

---

### Sample Code

You can test lesson activity grading via `notebooks/activity_grading_dev.ipynb` or by importing `lesson_grader.py`.

```python
from modules.lesson_activities.lesson_grader import get_correction

question = "Describe your last holiday."
text = "i go to beach and swim. was very fun"
result = get_correction(question, text)

print(result)
# Output:
# {
#   "score": 17,
#   "feedback": "Good effort. Work on grammar and structure for better coherence."
# }
```

---

### Output Format

```json
{
  "score": 21,
  "feedback": "Well structured with minor grammar mistakes. Excellent vocabulary use."
}
```

---

## 🧪 Testing

Test the lesson grader logic using:

```bash
pytest tests/test_lesson_activities.py
```

---

## 📌 Notes

- Future modules (e.g., for placement exams or essay scoring) will follow similar structure.
- Each module should expose a single `get_correction()` interface.

---

**Developed as part of the SAFAR AI learning platform.**
