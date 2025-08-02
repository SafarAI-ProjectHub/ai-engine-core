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
    # Remove 'output:' if present
    if output_text.startswith(header):
        output_text = output_text[len(header):].strip()
    # Add braces to make it valid JSON if needed
    if not output_text.startswith("{"):
        output_text = "{" + output_text + "}"
    # Replace single quotes with double quotes if needed
    output_text = re.sub(r"(\w+):", r'"\1":', output_text)
    data = json.loads(output_text)
    return data


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