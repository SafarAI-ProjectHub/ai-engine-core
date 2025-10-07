import json
import re

def extract_json_from_response(response, header: str = "output:") -> dict:
    """
    Extracts and parses a JSON object from a response's output text, optionally removing a header.
    Args:
        response: An object with an 'output_text' attribute containing the response string.
        header (str, optional): The header string to remove from the start of the output text. Defaults to "output:".
    Returns:
        dict: The parsed JSON object as a Python dictionary.
    """
    output_text = response.output_text.strip()
    
    # Remove header if present
    if output_text.startswith(header):
        output_text = output_text[len(header):].strip()
    
    # Try to find JSON object in the text
    json_match = re.search(r'\{.*\}', output_text, re.DOTALL)
    if json_match:
        output_text = json_match.group(0)
    
    # If no JSON object found, try to construct one
    if not output_text.startswith("{"):
        # Look for key-value patterns and construct JSON
        score_match = re.search(r'"score":\s*(\d+)', output_text)
        feedback_match = re.search(r'"feedback":\s*"([^"]*)"', output_text)
        
        if score_match and feedback_match:
            score = score_match.group(1)
            feedback = feedback_match.group(1)
            output_text = f'{{"score": {score}, "feedback": "{feedback}"}}'
        else:
            # Fallback: wrap the entire text in braces
            output_text = "{" + output_text + "}"
    
    # Clean up any common issues
    # Replace single quotes with double quotes for keys (but preserve string values)
    output_text = re.sub(r"'([^']*)':", r'"\1":', output_text)
    
    try:
        data = json.loads(output_text)
        return data
    except json.JSONDecodeError as e:
        # If JSON parsing fails, try to extract values manually
        score_match = re.search(r'"score":\s*(\d+)', output_text)
        feedback_match = re.search(r'"feedback":\s*"([^"]*)"', output_text)
        
        if score_match and feedback_match:
            return {
                "score": int(score_match.group(1)),
                "feedback": feedback_match.group(1)
            }
        else:
            raise e


def format_json_response(data: dict) -> str:
    """
    Format a dictionary as a pretty-printed JSON string.
    Args:
        data (dict): The dictionary to format as JSON.
    Returns:
        str: The formatted JSON string.
    """
    formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
    return formatted_json