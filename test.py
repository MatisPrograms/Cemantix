#!/usr/bin/env python

GAME = {
    'en': {
        'name': 'English',
        'title': 'Cemantle',
        'code': 'eng',
        'url': 'https://cemantle.certitudes.org',
        'flag': '🇬🇧',
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
        'markdown': '',
        'words_tested': {},
        'words_to_test': [],
        'words_not_found': [],
        'last_result': {},
        'today_file_path': '',
        'worker': None,
    },
}

print(f"{'Dicts'}/{GAME['en']['code'][:-1]}.txt")

exit(0)

word = 'prison'
lang='fra'
prompt=f"""
You are a web server that provides the lexical field of a word in a language and you must return an array.
I have the word {word} in {lang} language. Can you provide me with a list of words that are in the same lexical field as {word} with you response in {lang}?
"""

url="http://localhost:11434/api/generate"

# curl http://localhost:11434/api/generate -d '{
#   "model": "llama3.2",
#   "prompt":"Why is the sky blue?"
# }'

import requests

response = requests.post(url, json={
    "model": "llama3.2",
    "prompt": prompt,
    "stream": False,
})

print(response.json()['response'])
