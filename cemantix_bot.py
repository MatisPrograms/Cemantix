import json
import os
import random
import signal
import time
import argparse
from datetime import datetime, timedelta
import shutil
import requests
from lxml import html
import nltk
from nltk.corpus import wordnet

nltk.download('wordnet')

red = "\033[1;31m"
green = "\033[1;32m"
yellow = "\033[1;33m"
blue = "\033[1;34m"
magenta = "\033[1;35m"
cyan = "\033[1;36m"
white = "\033[1;37m"
reset = "\033[0m"

second = 1000
percent = 100
max_score = 1000.0

website_url = 'https://cemantle.certitudes.org'
headers = {"Origin": website_url, "Referer": website_url}

dict_path = 'dic_eng.txt'
days_path = "Days"
today_file_path = f"{days_path}/{datetime.strftime(datetime.now(), '%d-%m-%Y')}.txt"
yesterday_file_path = f"{days_path}/{datetime.strftime(datetime.now() - timedelta(days=1), '%d-%m-%Y')}.txt"

if not os.path.exists('Days'):
    os.makedirs('Days')


def get_max_value(dictionary):
    max_value = 0
    max_key = ''
    for key, value in dictionary.items():
        if value > max_value:
            max_value = value
            max_key = key
    return max_key, max_value


def removeWordFromFile(file_path=dict_path, word='', words=[]):
    with open(file_path, mode="r", encoding="utf-8") as f:
        word_list = f.read().splitlines()
    if not word and not words:
        word_list = list(set(word_list))
    with open(file_path, mode="w", encoding="utf-8") as f:
        for w in word_list:
            if (word and w != word) or (words and w not in words) or (not word and not words):
                f.write(w + "\n")


def showProgress(count, total, width=25, symbol='-', name=''):
    line = "\r " + green + symbol * int(count / total * width) + red + symbol * (width - int(count / total * width)) + reset + f" {(count / total) * percent:.2f}% " + white + (f"[{name}]" if name else name) + reset
    print(line.ljust(shutil.get_terminal_size().columns), end="")


def showRankings(ranking_size=25):
    print(red + '''

     ▄████████   ▄▄▄▄███▄▄▄▄      ▄████████ ███▄▄▄▄       ███      ▄█  ▀████    ▐████▀         ▄████████    ▄████████ ███▄▄▄▄      ▄█   ▄█▄  ▄█  ███▄▄▄▄      ▄██████▄     ▄████████ 
    ███    ███ ▄██▀▀▀███▀▀▀██▄   ███    ███ ███▀▀▀██▄ ▀█████████▄ ███    ███▌   ████▀         ███    ███   ███    ███ ███▀▀▀██▄   ███ ▄███▀ ███  ███▀▀▀██▄   ███    ███   ███    ███ 
    ███    █▀  ███   ███   ███   ███    ███ ███   ███    ▀███▀▀██ ███▌    ███  ▐███           ███    ███   ███    ███ ███   ███   ███▐██▀   ███▌ ███   ███   ███    █▀    ███    █▀  
    ███        ███   ███   ███   ███    ███ ███   ███     ███   ▀ ███▌    ▀███▄███▀          ▄███▄▄▄▄██▀   ███    ███ ███   ███  ▄█████▀    ███▌ ███   ███  ▄███          ███        
    ███        ███   ███   ███ ▀███████████ ███   ███     ███     ███▌    ████▀██▄          ▀▀███▀▀▀▀▀   ▀███████████ ███   ███ ▀▀█████▄    ███▌ ███   ███ ▀▀███ ████▄  ▀███████████ 
    ███    █▄  ███   ███   ███   ███    ███ ███   ███     ███     ███    ▐███  ▀███         ▀███████████   ███    ███ ███   ███   ███▐██▄   ███  ███   ███   ███    ███          ███ 
    ███    ███ ███   ███   ███   ███    ███ ███   ███     ███     ███   ▄███     ███▄         ███    ███   ███    ███ ███   ███   ███ ▀███▄ ███  ███   ███   ███    ███    ▄█    ███ 
    ████████▀   ▀█   ███   █▀    ███    █▀   ▀█   █▀     ▄████▀   █▀   ████       ███▄        ███    ███   ███    █▀   ▀█   █▀    ███   ▀█▀ █▀    ▀█   █▀    ████████▀   ▄████████▀  
                                                                                              ███    ███                          ▀                                                  ''' + reset)
    ranking = {}
    for word, value in words_tested.items():
        ranking[word] = value
    ranking = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
    for i, (word, value) in enumerate(ranking):
        if i == ranking_size or value == 0:
            break
        print(f"{green}{i + 1}{reset}.", word, '-',
              f"{(red if value > (max_score * 0.8) else yellow if value > (max_score * 0.5) else blue) + str(value) + reset}")


def loadDict(file_path=today_file_path):
    if os.path.getsize(file_path) == 0:
        return {}
    with open(file_path, mode="r", encoding="utf-8") as f:
        return json.load(f)


def saveDict():
    with open(today_file_path, mode="w", encoding="utf-8") as f:
        json.dump(words_tested, f)


def signal_handler(sig, frame):
    saveDict()
    removeWordFromFile(words=words_not_found)
    showRankings()
    exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    session = requests.Session()
    words_tested = {}
    words_to_test = []
    words_not_found = []
    last_result = {}

    parser = argparse.ArgumentParser(description='Cemantix bot')
    parser.add_argument('-t', '--test', help='Test a word', type=str)
    args = parser.parse_args()

    if os.path.exists(dict_path):
        with open(dict_path, mode="r", encoding="utf-8") as f:
            for line in f.readlines():
                words_to_test.append(line.replace("\n", ""))
        random.shuffle(words_to_test)

    if os.path.exists(today_file_path):
        words_tested = loadDict()
    else:
        open(today_file_path, mode="w", encoding="utf-8").close()

    if os.path.exists(yesterday_file_path):
        yesterday_best_word = get_max_value(loadDict(yesterday_file_path))
        if yesterday_best_word[1] == max_score:
            res = session.post(website_url + "/nearby", headers=headers, data={"word": yesterday_best_word[0]})
            for word in reversed(list(res.json())):
                words_to_test.append(word[0])

    if args.test:
        words_to_test.append(args.test)

    while len(words_to_test) > 0 and max(words_tested.values()) < max_score if words_tested else True:
        word = words_to_test.pop()
        
        if word.endswith('s'):
            words_to_test.append(word[:-1])
        if word in words_tested:
            continue

        res = session.post(website_url + "/score", headers=headers, data={"word": word})
        data = res.json() if res.content else {}

        if 'percentile' in data:
            last_result = {word: data['percentile']}
            words_tested[word] = float(data['percentile'])

            try:
                # Collect lexical field words
                lexical_field = set()

                # Get synsets (sense groupings)
                for synset in wordnet.synsets(word, lang="eng"):
                    # Add synonyms
                    for lemma in synset.lemmas():
                        lexical_field.add(lemma.name())
                    # Add hypernyms (broader terms)
                    for hypernym in synset.hypernyms():
                        lexical_field.update(lemma.name() for lemma in hypernym.lemmas())
                    # Add hyponyms (narrower terms)
                    for hyponym in synset.hyponyms():
                        lexical_field.update(lemma.name() for lemma in hyponym.lemmas())

                lexical_field = [lf.replace('_', '-') for lf in list(lexical_field)]

            except Exception as e:
                with open('error.log', mode='a', encoding='utf-8') as f:
                    f.write(f'{word}: {e}\n')

            for lf in lexical_field:
                if lf in words_tested:
                    continue
                if lf in words_to_test:
                    words_to_test.remove(lf)
                words_to_test.append(lf)

        elif 'error' in data:
            words_not_found.append(word)
        else:
            words_tested[word] = 0.0

        best_word, best_value = get_max_value(words_tested)
        showProgress(count=get_max_value(words_tested)[1], total=max_score,
                     name=('Best: ' + f'{best_word}' + ' | ' if best_word else '') +
                          (f'Found: {list(last_result.keys())[0]} - {list(last_result.values())[0]/max_score*percent:.2f}% | ' if last_result else '') +
                          f'Trying {word}',
                     symbol='█')
        time.sleep(random.randint(100, 500) / second)

    best_word, best_value = get_max_value(words_tested)
    tries = len(words_tested)
    showProgress(count=best_value, total=max_score,
                 name=f'{best_word}: {(green if best_value == max_score else red) + str(best_value) + white} | in {(green if tries < (max_score * 0.1) else yellow if tries < (max_score * 0.5) else red) + str(tries) + white} tries',
                 symbol='█')

    signal_handler(None, None)
