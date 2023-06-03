import re
from rich.console import Console

console = Console()


def readlines(sentinel: str = ':wq', prompt: str | None = None) -> str:
    """Multi-line read command line input.

    Args:
        sentinel (str): The end of the input(case insensitive). If you want to press Enter twice to finish, the value of sentinel is set to ''
        prompt (str|None): The prompt string. If None, the prompt is set to f'ask for answer(press "{sentinel}" to finish)'
    """
    prompt = prompt or f'ask for answer(press "{sentinel}" to finish):'
    console.print(prompt, style="bold green")
    lines = []
    while True:
        line = input()
        if line.rstrip().lower() == sentinel.lower():
            break
        lines.append(line)
    return '\n'.join(lines)


if __name__ == '__main__':
    print(readlines())
