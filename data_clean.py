import re

def clean_task(text: str) -> str:
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[^\w\s\.,!?]", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\S+@\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    
    text = text.lower().strip()

    return text