from util.config import client, cls, Path, HTTPException, APIRouter, prs
from util.complition_model import complition_model
from util.token_utils import count_tokens

correction_router = APIRouter(tags=["correction"])

@correction_router.post("/correction", response_model=cls.ApiResponse)
async def get_correction(request: cls.CorrectionRequest):
    try:
        criteria_path = Path(__file__).parent.parent / "config" / "activitywritingcriteria.txt"
        example_path = Path(__file__).parent.parent / "config" / "writingexamples.txt"
                # read the criteria from the file
        with open(criteria_path, "r", encoding="utf-8") as file:
            # read the file content
            criteria = file.read()
        with open(example_path, "r", encoding="utf-8") as file:
            # read the file content
            examples = file.read()
        instructions = f"""
                You are a professional writing correction assistant.
                You should be strict with the evaluation.
                Your task is to evaluate a user's written response based on:

                The given question: 
                {request.question}

                The evaluation criteria: 
                {criteria}

                ##Scoring##

                ##Evaluate the response across five criteria:##

                -Task Achievement
                -Coherence and Cohesion
                -Lexical Resource
                -Grammatical Range and Accuracy
                -Spelling, Punctuation, and Mechanics
                -Each criterion must be scored with 0, 1, 3, or 5.
                -Sum the scores to produce a total out of 25.

                ##Output Format##

                Return the result in JSON with exactly these keys:
                {{
                "score": "int",
                "feedback": "string"
                }}

                ##Feedback Instructions##

                -Feedback must be concise, constructive, and supportive.
                -Address each criterion specifically with strengths and suggestions for improvement.
                -Point out specific mistakes and show how to correct them.
                -If a criterion does not apply, do not penalize the user.
                -Do not restate the question or answer, explain the criteria, or add extra commentary.

                ##Example##
                {examples}"""

            
        response = await complition_model(
            model = "gpt-4o",
            instructions = instructions,
            input = request.text
        )
        # Parse the response to extract JSON
        response_data = prs.extract_json_from_response(response, header="score:")
        
        # Safely convert score to int
        score = response_data.get("score", 0)
        if isinstance(score, str):
            try:
                score = int(score)
            except ValueError:
                score = 0
        
        # Get feedback safely
        feedback = response_data.get("feedback", "No feedback available")

        # Count tokens for input and model output text
        output_text = response.output_text
        token_count = count_tokens(request.text, "gpt-4o") + count_tokens(output_text, "gpt-4o")

        data = cls.CorrectionResponse(
            status="success",
            score=score,
            feedback=feedback,
            token_count=token_count,
        )
        usage = cls.Usage(tokens=token_count)
        return cls.build_response(
            data=data,
            usage=usage,
            endpoint_key="correction",
        )
    except Exception as e:
        data = cls.CorrectionResponse(
            status="False",
            score=0,
            feedback=f"An error occurred while processing the request: {str(e)}",
            token_count=0,
        )
        usage = cls.Usage(tokens=0)
        return cls.build_response(
            data=data,
            usage=usage,
            endpoint_key="correction",
            success=False,
        )
