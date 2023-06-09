import re
import sys

from pygments.lexers.markup import MarkdownLexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML


def create_session() -> PromptSession:
    return PromptSession(history=InMemoryHistory())


def create_completer(commands: list, pattern_str: str = "$") -> WordCompleter:
    return WordCompleter(words=commands, pattern=re.compile(pattern_str))


def bottom_toolbar():
    # Default MacOS
    exit_key = 'Esc + Enter'
    if sys.platform.startswith('win32'):
        exit_key = 'Alt + Enter'
    return HTML(f'Press <b><style bg="ansired">{exit_key}</style></b> to send a message! <b><style bg="green">Vi</style></b> commands are supported')


def prompt_message(prompt: str):
    return HTML(f'<b><style fg="green">{prompt}</style></b>')


def get_input(
    session: PromptSession = None,
    completer: WordCompleter = None,
    key_bindings: KeyBindings = None,
) -> str:
    """
    Multiline input function.
    """
    return (
        session.prompt(
            prompt_message('> '),
            completer=completer,
            multiline=True,
            auto_suggest=AutoSuggestFromHistory(),
            key_bindings=key_bindings,
            bottom_toolbar=bottom_toolbar,
            vi_mode=True,
            lexer=PygmentsLexer(MarkdownLexer)
        )
        if session
        else prompt(multiline=True)
    )


def multi_input() -> str:
    session = create_session()
    completer = create_completer([
        "reset",
        "continue",
        "exit",
        ":q"
    ])
    return get_input(session=session, completer=completer)


if __name__ == '__main__':
    session = create_session()
    completer = create_completer(["reset", "continue", "rewrite"])
    text = get_input(session=session, completer=completer)
