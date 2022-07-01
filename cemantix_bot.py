import json
import os
import random
import signal
import time
from datetime import datetime, timedelta

import requests
from lxml import html
from nltk.corpus import wordnet

red = "\033[1;31m"
green = "\033[1;32m"
yellow = "\033[1;33m"
blue = "\033[1;34m"
magenta = "\033[1;35m"
cyan = "\033[1;36m"
white = "\033[1;37m"
reset = "\033[0m"

fr_dict_path = 'dic_fr.txt'
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


def removeWordFromFile(file_path=fr_dict_path, word='', words=[]):
    with open(file_path, mode="r", encoding="utf-8") as f:
        word_list = f.read().splitlines()
    if not word and not words:
        word_list = list(set(word_list))
    with open(file_path, mode="w", encoding="utf-8") as f:
        for w in word_list:
            if (word and w != word) or (words and w not in words) or (not word and not words):
                f.write(w + "\n")


def showProgress(count, total, width=25, symbol='-', name=''):
    print("\r " + green + symbol * int(count / total * width) + red + symbol * (width - int(count / total * width)) +
          reset + f" {(count / total) * 100:.2f}% " + white + (f"[{name}]" if name else name) + reset, end="",
          flush=True)


def showRankings():
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
        print(f"{i + 1}. {word} - {red + str(value) + reset}")
        if i + 1 == 20:
            break


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

    if os.path.exists(fr_dict_path):
        with open(fr_dict_path, mode="r", encoding="utf-8") as f:
            for line in f.readlines():
                words_to_test.append(line.replace("\n", ""))
        random.shuffle(words_to_test)

    if os.path.exists(today_file_path):
        words_tested = loadDict()
    else:
        open(today_file_path, mode="w", encoding="utf-8").close()

    yesterday_best_word = get_max_value(loadDict(yesterday_file_path))
    if yesterday_best_word[1] == 1000.0:
        res = session.post("https://cemantix.herokuapp.com/nearby", data={"word": yesterday_best_word[0]})
        for word in reversed(list(res.json())):
            words_to_test.append(word[0])

    while len(words_to_test) > 0 and max(words_tested.values()) < 1000.0 if words_tested else True:
        word = words_to_test.pop()
        if word.endswith('s'):
            words_to_test.append(word[:-1])
        if word in words_tested:
            continue

        res = session.post("https://cemantix.herokuapp.com/score", data={"word": word})
        data = res.json()
        if 'percentile' in data:
            last_result = {word: data['percentile']}
            words_tested[word] = float(data['percentile'])

            # Using nltk to get synonyms
            try:
                for syn in wordnet.synsets(word, lang="fra"):
                    for l in syn.lemmas(lang="fra"):
                        syno = str(l.name()).replace('_', '-')
                        if syno and syno not in words_tested:
                            words_to_test.append(syno)
                    for h in syn.hyponyms():
                        for l in h.lemmas(lang="fra"):
                            syno = str(l.name()).replace('_', '-')
                            if syno and syno not in words_tested:
                                words_to_test.append(syno)
                    for h in syn.hypernyms():
                        for l in h.lemmas(lang="fra"):
                            syno = str(l.name()).replace('_', '-')
                            if syno and syno not in words_tested:
                                words_to_test.append(syno)
            except:
                pass

            # Using synonymo.fr to get synonyms
            try:
                syno_res = session.post('http://www.synonymo.fr/accueil/recherche_redirect',
                                        data={'model': 'syno', 'syno': word})
                if syno_res.content:
                    for element in html.fromstring(syno_res.content) \
                            .xpath('//*[@id="main-container"]/div[4]/div[1]/div[2]/ul[1]')[0].getchildren():
                        syno = str(element.text_content().strip())
                        if syno and syno not in words_tested:
                            words_to_test.append(syno)
            except:
                pass
        elif 'error' in data:
            words_not_found.append(word)
        else:
            words_tested[word] = 0.0

        best_word, best_value = get_max_value(words_tested)
        showProgress(count=get_max_value(words_tested)[1], total=1000,
                     name=('Best: {' + f'{best_word} {best_value}' + '} | ' if best_word else '') +
                          (f'Last: {last_result} | ' if last_result else '') +
                          f'{len(words_to_test)} words left | trying {word}',
                     symbol='█')
        time.sleep(random.randint(500, 1000) / 1000)

    best_word, best_value = get_max_value(words_tested)
    tries = len(words_tested)
    showProgress(count=best_value, total=1000,
                 name=f'{best_word}: {(green if best_value == 1000 else red) + str(best_value) + white} | in {(green if tries < 100 else yellow if tries < 500 else red) + str(tries) + white} tries')

    signal_handler(None, None)
