import json

def pack_result(text: str, segments: list = None, language: str = "auto"):
    """Pack transcription result into JSON format."""
    if segments is None:
        segments = []
    return json.dumps({
        "text": text,
        "language": language,
        "segments": segments
    })
