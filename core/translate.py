import requests
import os

url = os.getenv("DEEPL_URL") or "http://127.0.0.1:1188/translate"


def translate(text: str, from_lang: str = "zh", to_lang: str = "en") -> str:
    r = requests.post(
        url=url,
        json={
            "text": text,
            "source_lang": from_lang,
            "target_lang": to_lang
        }
    )
    return r.json()["data"]


if __name__ == "__main__":
    print(translate("你好"))
