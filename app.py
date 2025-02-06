#!/usr/bin/env python

from __future__ import annotations

import os
import json
import random
import signal
import time
from datetime import datetime, timedelta

from textual.color import Lab

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError("Please install bs4 with 'pip install bs4' ")

try:
    from functools import partial
except ImportError:
    raise ImportError("Please install functools with 'pip install functools' ")

try:
    import nltk
    from nltk.inference import resolution
    from nltk.corpus import wordnet
except ImportError:
    raise ImportError("Please install nltk with 'pip install nltk' ")

try:
    import httpx
except ImportError:
    raise ImportError("Please install httpx with 'pip install httpx' ")


from rich.text import TextType
from textual import work
from textual.binding import Binding
from textual.app import App, ComposeResult
from textual.color import Gradient
from textual.reactive import reactive
from textual.worker import Worker, get_current_worker
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, Markdown, ProgressBar, Static, LoadingIndicator, Header, Footer, ContentSwitcher

SECOND = 1000
MAX_SCORE = 1000.0

class Status:
    started = 'started'
    stopped = 'stopped'

GAME = {
    'en': {
        'name': 'English',
        'title': 'Cemantle',
        'code': 'eng',
        'url': 'https://cemantle.certitudes.org',
        'flag': '🇬🇧',
        'status': Status.stopped,
        'markdown': '',
        'words_tested': {},
        'words_to_test': [],
        'words_not_found': [],
        'last_result': {},
        'today_file_path': '',
        'worker': None,
    },
    'fr': {
        'name': 'French',
        'title': 'Cémantix',
        'code': 'fra',
        'url': 'https://cemantix.certitudes.org',
        'flag': '🇫🇷',
        'status': Status.stopped,
        'markdown': '',
        'words_tested': {},
        'words_to_test': [],
        'words_not_found': [],
        'last_result': {},
        'today_file_path': '',
        'worker': None,
    },
}

dict_path = 'Dicts'
days_path = "Days"

markdown_leaderboard_header =  "| Pos  | Word               | Score      |\n"
markdown_leaderboard_header += "| ---- | ------------------ | ---------- |\n"

today_file = f"{datetime.strftime(datetime.now(), '%d-%m-%Y')}.txt"
current_file_path = os.path.dirname(os.path.realpath(__file__)) + "/"

def get_max_value(dictionary):
    max_value = 0
    max_key = ''
    for key, value in dictionary.items():
        if value > max_value:
            max_value = value
            max_key = key
    return max_key, max_value


def removeWordFromFile(file_path, word='', words=[]):
    with open(file_path, mode="r", encoding="utf-8") as f:
        word_list = f.read().splitlines()
    if not word and not words:
        word_list = list(set(word_list))
    with open(file_path, mode="w", encoding="utf-8") as f:
        for w in word_list:
            if (word and w != word) or (words and w not in words) or (not word and not words):
                f.write(w + "\n")


def get_lexical_field(word, lang):
    # Collect lexical field words
    lexical_field = set()

    try:
        # Get synsets (sense groupings)
        for synset in wordnet.synsets(word, lang=lang):
            if not synset:
                continue

            # Add synonyms
            for lemma in synset.lemmas(lang=lang):
                lexical_field.add(lemma.name())
            # Add hypernyms (broader terms)
            for hypernym in synset.hypernyms():
                lexical_field.update(lemma.name() for lemma in hypernym.lemmas(lang=lang))
            # Add hyponyms (narrower terms)
            for hyponym in synset.hyponyms():
                lexical_field.update(lemma.name() for lemma in hyponym.lemmas(lang=lang))

        lexical_field = [lf.replace('_', '-') for lf in list(lexical_field)]

    except Exception as e:
        with open('error.log', mode='a', encoding='utf-8') as f:
            f.write(f'{word}: {e}\n')

    return lexical_field


def getRankings(words, ranking_size=25):
    ranking = {}
    markdown_leaderboard = ""

    for word, value in words.items():
        ranking[word] = value

    # Sort the dictionary by value
    ranking = sorted(ranking.items(), key=lambda x: x[1], reverse=True)

    # Add rows to the Markdown table
    for i, (word, value) in enumerate(ranking):
        if i == ranking_size or value == 0:
            break

        markdown_leaderboard += f"| {str(i + 1) + '.':<4} | {word:<18} | {value:<10} |\n"

    # Return the Markdown table
    return markdown_leaderboard


def loadDict(file_path):
    if os.path.getsize(file_path) == 0:
        return {}
    with open(file_path, mode="r", encoding="utf-8") as f:
        return json.load(f)


def saveDict(file_path, words):
    with open(file_path, mode="w", encoding="utf-8") as f:
        json.dump(words, f)

def saveState(game: dict):
    saveDict(game['today_file_path'], game['words_tested'])
    removeWordFromFile(file_path=f"{dict_path}/{game['code'][:-1]}.txt", words=game['words_not_found'])

def signal_handler(sig, frame, game: dict):
    saveState(game)
    exit(0)

for language in GAME.keys():
    if not os.path.exists(f"{days_path}/{language}"):
        os.makedirs(f"{days_path}/{language}")

    if not os.path.exists(f"{dict_path}/{language}.txt"):
        os.makedirs(dict_path, exist_ok=True)
        open(f"{dict_path}/{language}.txt", mode="w", encoding="utf-8").close()

    GAME[language]['today_file_path'] = f"{days_path}/{language}/{today_file}"

    if os.path.exists(f"{dict_path}/{language}.txt"):
        with open(f"{dict_path}/{language}.txt", mode="r", encoding="utf-8") as f:
            for line in f.readlines():
                GAME[language]['words_to_test'].append(line.replace("\n", ""))
        random.shuffle(GAME[language]['words_to_test'])

    if os.path.exists(GAME[language]['today_file_path']):
        GAME[language]['words_tested'] = loadDict(GAME[language]['today_file_path'])
    else:
        open(GAME[language]['today_file_path'], mode="w", encoding="utf-8").close()

class Cementix(Static):
    """The Cementix class."""

    gradient = Gradient.from_colors(
                "#881177",
                "#aa3355",
                "#cc6666",
                "#ee9944",
                "#eedd00",
                "#99dd55",
                "#44dd88",
                "#22ccbb",
                "#00bbcc",
                "#0099cc",
                "#3366bb",
                "#663399",
            )

    def __init__(self, id: str, language: str):
        self.language = language
        super().__init__(id=id)

    def prefix(self, word) -> str:
        return f"{self.language}-{word}"

    def compose(self) -> ComposeResult:
        """Compose the layout."""

        with Horizontal(classes="padding"):
            with VerticalScroll(id="guesses-container") as guesses_container:
                guesses_container.border_title = "Guesses"
                yield Markdown(id=self.prefix("guesses-list"))

            with Vertical():
                yield Label("Yesterday's word was...", id=self.prefix("yesterday-word"))

                with Horizontal():
                    yield Input(placeholder="Enter a word", id=self.prefix("word-input"))
                    yield Button("Submit", id=self.prefix("submit-word"))

                with Vertical(id="progresion", classes="center"):
                    yield ProgressBar(id=self.prefix("progress-bar"), total=100, gradient=self.gradient, show_eta=False)
                    with Horizontal(id="search-status"):
                        yield LoadingIndicator(id="search-indicator")
                        yield Label("Searching...", id=self.prefix("search-label"))

    def on_mount(self) -> None:
        """A coroutine to handle the mount event."""
        markdown = f"# 🏆 {GAME[self.language]['title']} Rankings 🏆\n"
        markdown += markdown_leaderboard_header
        GAME[self.language]['markdown'] = markdown
        self.query_one(f"#{self.prefix('guesses-list')}", Markdown).update(markdown)
        self.query_one(f"#{self.prefix('progress-bar')}", ProgressBar).update(progress=100)

class CementixApp(App):
    """The main application class."""
    CSS_PATH = "app.tcss"

    BINDINGS = [
        Binding(key="ctrl+o", action="open_website", description="Open the website"),
        Binding(key="ctrl+s", action="save", description="save the state for all languages"),
    ]

    selected_language = 'en'

    start_button = Button("Start 🟢", id="start")
    stop_button = Button("Stop 🛑", id="stop")
    stop_button.display = "none"

    def prefix(self, word) -> str:
        return f"{self.selected_language}-{word}"

    def compose(self) -> ComposeResult:
        """Compose the layout."""
        yield Header()

        with Horizontal(id="buttons", classes="center"):
            for language in GAME.keys():
                yield Button(f"{GAME[language]['name']} {GAME[language]['flag']}", id=f"{language}-tab")

            with Horizontal(id="status"):
                yield Label("Status:")
                yield self.start_button
                yield self.stop_button

        with ContentSwitcher(initial=f"{self.selected_language}-tab", id="content-switcher"):
            for language in GAME.keys():
                yield Cementix(id=f"{language}-tab", language=language)

        yield Footer()

    def action_open_website(self):
        """Open the website."""
        self.app.open_url(GAME[self.selected_language]['url'])

    def action_save(self):
        """save the state for all languages."""
        for language in GAME.keys():
            saveState(GAME[language])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """A coroutine to handle a button pressed event."""

        content_switcher = self.query_one(ContentSwitcher)
        if event.button.id in list(map(lambda x: x.id, content_switcher.children)):
            content_switcher.current = event.button.id
            if event.button.id is not None:
                self.selected_language = event.button.id.split("-")[0]
                self.query_one("#start", Button).display = "block" if GAME[self.selected_language]['status'] == Status.stopped else "none"
                self.query_one("#stop", Button).display = "block" if GAME[self.selected_language]['status'] == Status.started else "none"
            return

        if event.button.id == "start" and max(GAME[self.selected_language]['words_tested'].values()) < MAX_SCORE if GAME[self.selected_language]['words_tested'] else True:
            GAME[self.selected_language]['status'] = Status.started
            self.query_one("#start", Button).display = "none"
            self.query_one("#stop", Button).display = "block"
            GAME[self.selected_language]['worker'] = self.run_worker(self.run_search(self.selected_language), self.selected_language, group=self.prefix("search"), thread=True)
        elif event.button.id == "stop":
            GAME[self.selected_language]['status'] = Status.stopped
            self.query_one("#start", Button).display = "block"
            self.query_one("#stop", Button).display = "none"
            GAME[self.selected_language]['worker'].cancel()
            saveState(GAME[self.selected_language])
        elif event.button.id == self.prefix("submit-word"):
            input = self.query_one(f"#{self.prefix('word-input')}", Input)
            self.submit_word(input.value, self.selected_language)
            input.value = ""
        else:
            self.notify(
                f"Button pressed {event.button.id} - Not handled",
                title="on_button_pressed",
                severity="warning",
            )

    async def on_mount(self) -> None:
        """A coroutine to handle the mount event."""
        for language in GAME.keys():
            self.get_yesterdays_word(language)
            self.set_interval(1, self.update_results_shown)

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """A coroutine to handle a text submitted message."""
        input = self.query_one(f"#{self.prefix('word-input')}", Input)
        self.submit_word(input.value, self.selected_language)
        input.value = ""

    async def run_search(self, language: str) -> None:
        """A coroutine to run the search."""

        while (get_current_worker().is_running and (len(GAME[self.selected_language]['words_to_test']) > 0 and max(GAME[self.selected_language]['words_tested'].values()) < MAX_SCORE if GAME[self.selected_language]['words_tested'] else True)):
            word = GAME[self.selected_language]['words_to_test'].pop()
            self.submit_word(word, self.selected_language)
            time.sleep(random.randint(100, 500) / SECOND)

        if max(GAME[self.selected_language]['words_tested'].values()) >= MAX_SCORE if GAME[self.selected_language]['words_tested'] else True:
            self.notify(
                f"You have found the best word! in {len(GAME[self.selected_language]['words_tested'])} tries",
                title=f"🏆 {GAME[self.selected_language]['title']} Results 🏆",
                severity='information'
            )
            GAME[self.selected_language]['status'] = Status.stopped
            self.query_one("#start", Button).display = "block"
            self.query_one("#stop", Button).display = "none"
            saveState(GAME[self.selected_language])

    @work(exclusive=True)
    async def submit_word(self, word: str, language) -> None:
        """gets score of the word."""
        url = GAME[self.selected_language]['url']
        headers = {"Origin": url, "Referer": url}

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{url}/score", headers=headers, data={"word": word})
            data = response.json() if response.content else {}

            if 'p' in data:
                GAME[language]['last_result'] = {word: data['p']}
                GAME[language]['words_tested'][word] = float(data['p'])

                for w in get_lexical_field(word, GAME[language]['code']):
                    if w in GAME[language]['words_tested']:
                        continue
                    if w in GAME[language]['words_to_test']:
                        GAME[language]['words_to_test'].remove(w)
                    GAME[language]['words_to_test'].append(w)

            elif 'e' in data:
                GAME[language]['words_not_found'].append(word)
            else:
                GAME[language]['words_tested'][word] = 0.0

    @work(thread=True)
    async def get_yesterdays_word(self, language: str) -> None:
        """gets yesterday's word."""

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{GAME[language]['url']}")
            html = BeautifulSoup(response.content.decode("utf-8"), "html.parser")

            yesterday_word = html.select('#yesterday')[0].text if html.select('#yesterday') else 'N/A'
            self.query_one(f"#{language}-yesterday-word", Label).update(f"Yesterday's word was {yesterday_word}")
            self.get_yesterdays_list(yesterday_word, language)

    @work(thread=True)
    async def get_yesterdays_list(self, word: str, language: str) -> None:
        """gets the list of yesterday's word."""
        url = GAME[language]['url']
        headers = {"Origin": url, "Referer": url}

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{url}/nearby", headers=headers, data={"word": word})
            data = response.json() if response.content else {}
            for w, _, _ in reversed(list(data)):
                if w in GAME[language]['words_tested']:
                    continue
                if w in GAME[language]['words_to_test']:
                    GAME[language]['words_to_test'].remove(w)
                GAME[language]['words_to_test'].append(w)

    @work(exclusive=True)
    async def update_results_shown(self) -> None:
        """Update the results shown."""
        markdown = GAME[self.selected_language]['markdown']
        markdown += f"{getRankings(GAME[self.selected_language]['words_tested'], ranking_size=50)}"
        self.query_one(f"#{self.prefix('guesses-list')}", Markdown).update(markdown)

if __name__ == "__main__":
    CementixApp().run()
