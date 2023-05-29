import os
from dotenv import load_dotenv
from revChatGPT.V1 import Chatbot
from core.bard import Chatbot as Bard
from rich.console import Console
from rich.markdown import Markdown
from core.translate import translate as translator
from rich import print
import typer
from typing_extensions import Annotated
import random

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


@app.command()
def chatgpt(plus: Annotated[bool, typer.Option("--plus", "-p", prompt=True)] = False):
    console = Console()
    if plus:
        chatbot = Chatbot(
            config={"access_token": gpt_plus_access_token}, base_url=base_url)
        console.print("Using ChatGPT Plus...", style="bold green")
    else:
        chatbot = Chatbot(
            config={"access_token": gpt_access_token}, base_url=base_url)
        console.print("Using ChatGPT...", style="bold green")
    print(chatbot.base_url)
    while True:
        lines = []
        console.print(
            "ask for answer(press Enter twice to finish): ", style="bold green")
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        text = "\n".join(lines)

        if text.strip() == "continue":
            chatbot.continue_write()

        if text.strip() == "reset":
            chatbot.reset_chat()

        if text.strip() == "exit":
            exit(0)

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
    console = Console()
    console.print("Using Google Bard...", style="bold green")
    while True:
        lines = []
        console.print(
            "ask for answer(press Enter twice to finish): ", style="bold green")
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        text = "\n".join(lines)

        if text.strip() == "reset":
            chatbot = Bard(bard_session)

        if text.strip() == "exit":
            exit(0)

        response = chatbot.ask(text)
        console.print(Markdown(response["content"]))
        print(response["images"] if response["images"] else "")
        print()


@app.command()
def translate(source: Annotated[str, typer.Option("--source", "-s", prompt=True)] = "zh", target: Annotated[str, typer.Option("--target", "-t", prompt=True)] = "en"):
    console = Console()
    console.print("ask for answer(press Enter twice to finish): ",
                  style="bold green")
    text = input()
    response = translator(text, source, target)
    print(response)


if __name__ == "__main__":
    app()
