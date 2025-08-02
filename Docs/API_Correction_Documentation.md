# 📘 AI Correction API Documentation

**Base URL**: [`http://54.237.228.206/ai`](http://54.237.228.206/ai)  
**Interactive Swagger UI**: [`http://54.237.228.206/ai/docs`](http://54.237.228.206/ai/docs)

---

## 🔄 POST `/correction`

Submit a writing task for AI-powered correction using GPT-4 and predefined rubric criteria.

### 📥 Request

**URL**:  
`http://54.237.228.206/ai/correction`

**Method**:  
`POST`

**Content-Type**:  
`application/json`

**Body**:
```json
{
  "question": "Describe your last vacation.",
  "text": "I goed to the beach and it was fun."
}
```

| Field     | Type     | Required | Description                                  |
|-----------|----------|----------|----------------------------------------------|
| question  | `string` | ✅       | The writing prompt or question               |
| text      | `string` | ✅       | The student's written answer to be corrected |

---

### 📤 Response

Returns a structured JSON response with a score and feedback based on multiple grading criteria.

```json
{
  "score": 18,
  "feedback": "Good effort. You used the past tense but made a few grammar mistakes like 'goed' instead of 'went'."
}
```

| Field     | Type     | Description                                               |
|-----------|----------|-----------------------------------------------------------|
| score     | `int`    | Total score (0–25), based on 5 criteria                   |
| feedback  | `string` | Qualitative feedback with grammar, coherence, vocabulary |

---

## 📑 Scoring Rubric

The AI evaluates text using the following criteria:

1. Task Achievement / Content Relevance
2. Coherence and Cohesion
3. Lexical Resource (Vocabulary)
4. Grammatical Range and Accuracy
5. Spelling, Punctuation, and Mechanics

Each criterion is scored as: `0`, `1`, `3`, or `5`.  
Total score is the sum (max: 25).

---

## 🧪 Test via Swagger UI

You can test this endpoint using FastAPI’s interactive Swagger documentation:

👉 [`http://54.237.228.206/ai/docs`](http://54.237.228.206/ai/docs)

---

## 🛡️ Notes

- Ensure you provide a valid OpenAI key in your `.env` file.
- All traffic is currently served over HTTP (consider HTTPS for production).
- Supports only plain text input. Future updates may support file upload or batch correction.

---