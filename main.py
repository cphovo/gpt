import os
import typer
import random
from enum import Enum
from dotenv import load_dotenv
from revChatGPT.V1 import Chatbot
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from core.bard import Chatbot as Bard
from typing_extensions import Annotated
from core.translate import translate as translator
from core.utils import readlines

app = typer.Typer()

load_dotenv()

gpt_plus_access_token = os.getenv("ACCESS_TOKEN")
gpt_access_token = os.getenv("CHATGPT_ACCESS_TOKEN")
bard_session = os.getenv("BARD_SESSION")

cloudfare_bypass = [
    "https://ai.fakeopen.com/api/",
    "https://bypass.churchless.tech/",
    "https://api.pawan.krd/backend-api/",
]

base_url = os.getenv("CHATGPT_BASE_URL") or random.choice(cloudfare_bypass)

console = Console()


CONTINUE_COMMAND = ["continue", ":c"]
RESET_CONVERSATION_COMMAND = ["reset", ":r"]
EXIT_COMMAND = ["exit", ":q!"]
RE_ENTER_COMMAND = ':q'


@app.command()
def chatgpt(plus: Annotated[bool, typer.Option("--plus", "-p", prompt=True)] = False):
    if plus:
        chatbot = Chatbot(
            config={"access_token": gpt_plus_access_token}, base_url=base_url)
        console.print("Using ChatGPT Plus...", style="bold green")
    else:
        chatbot = Chatbot(
            config={"access_token": gpt_access_token}, base_url=base_url)
        console.print("Using ChatGPT...", style="bold green")
    print(f"proxy: {chatbot.base_url}")
    while True:
        text = readlines()

        if text.strip().lower() in CONTINUE_COMMAND:
            chatbot.continue_write()
            continue

        if text.strip().lower() in RESET_CONVERSATION_COMMAND:
            chatbot.reset_chat()
            console.print(
                "I cleaned my brain, try new topic plz...", style="bold yellow")
            continue

        if text.strip().lower() in EXIT_COMMAND:
            exit(0)

        if text.strip().endswith(RE_ENTER_COMMAND):
            continue

        response = chatbot.ask(
            text, model='gpt-4') if plus else chatbot.ask(text)

        prev_text = ""
        for data in response:
            message = data["message"][len(prev_text):]
            print(message, end="", flush=True)
            prev_text = data["message"]

        print()
        chatbot.gen_title(chatbot.conversation_id, chatbot.parent_id)


@app.command()
def bard():
    chatbot = Bard(bard_session)
    console.print("Using Google Bard...", style="bold green")
    while True:
        text = readlines()

        if text.strip().lower() in RESET_CONVERSATION_COMMAND:
            console.print(
                "I cleaned my brain, try new topic plz...", style="bold yellow")
            chatbot = Bard(bard_session)
            continue

        if text.strip().lower() in EXIT_COMMAND:
            exit(0)

        if text.strip().endswith(RE_ENTER_COMMAND):
            continue

        response = chatbot.ask(text)
        console.print(Markdown(response["content"]))
        print(response["images"] if response["images"] else "")
        print()


class Language(str, Enum):
    """Support language codes for translation.

    - zh: Chinese
    - en: English
    - ja: Japanese
    - fr: French

    Other language codes can be found at https://www.deepl.com/translator
    """
    zh = "zh"
    en = "en"
    ja = "ja"
    fr = "fr"


@app.command(name="zh", help="Shortcut keys to translate Chinese to English.")
def translate_zh_to_en():
    print("Translate Chinese to English...")
    translate()


@app.command(name="en", help="Shortcut keys to translate English to Chinese.")
def translate_en_to_zh():
    print("Translate English to Chinese...")
    translate("en", "zh")


@app.command()
def translate(source: Annotated[Language, typer.Option("--source", "-s", prompt=True, show_choices=False)] = "zh", target: Annotated[Language, typer.Option("--target", "-t", prompt=True, show_choices=False)] = "en"):
    console.print(">>> ", style="bold green", end="")
    text = input()
    response = translator(text, source, target)
    print(response)


if __name__ == "__main__":
    app()
