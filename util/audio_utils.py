from pathlib import Path

from mutagen import File


def get_audio_duration_seconds(file_path: str) -> float:
    """
    Return the audio duration in seconds (float).

    Works with common formats supported by mutagen (e.g., mp3, wav, flac, m4a).
    Raises FileNotFoundError if the file is missing, and ValueError if the
    duration cannot be determined.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")

    audio_file = File(path)
    if audio_file is None or not hasattr(audio_file, "info") or audio_file.info is None:
        raise ValueError(f"Could not read audio metadata for: {path}")

    duration = getattr(audio_file.info, "length", None)
    if duration is None:
        raise ValueError(f"Could not determine duration for: {path}")

    return float(duration)