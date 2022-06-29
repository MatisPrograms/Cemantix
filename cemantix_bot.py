import json
import os
import random
import signal
import time

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
today_file_path = f"Days/{time.strftime('%d-%m-%Y')}.txt"

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


def saveDict():
    with open(today_file_path, mode="w", encoding="utf-8") as f:
        json.dump(words_tested, f)


def signal_handler(sig, frame):
    saveDict()
    showRankings()
    exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    session = requests.Session()
    words_tested = {}
    words_to_test = []
    last_result = {}

    if os.path.exists(fr_dict_path):
        fr_words_file = open(fr_dict_path, mode="r", encoding="utf-8")
        for line in fr_words_file.readlines():
            if 4 < len(line) < 12:
                words_to_test.append(line.replace("\n", ""))
        fr_words_file.close()
        random.shuffle(words_to_test)

    if os.path.exists(today_file_path):
        with open(today_file_path, encoding="utf-8") as f:
            words_tested = json.load(f)
    else:
        open(today_file_path, mode="w", encoding="utf-8").close()

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

        else:
            words_tested[word] = 0.0

        showProgress(count=get_max_value(words_tested)[1], total=1000,
                     name=f'Best: {get_max_value(words_tested)} | ' +
                          (f'Last: {last_result} | ' if last_result else '') +
                          f'{len(words_to_test)} words left | trying {word}',
                     symbol='█')
        time.sleep(random.randint(500, 1000) / 1000)

    word, value = get_max_value(words_tested)
    tries = len(words_tested)
    showProgress(count=value, total=1000,
                 name=f'{word}: {(green if value == 1000 else red) + str(value) + white} | in {(green if tries < 100 else yellow if tries < 500 else red) + str(tries) + white} tries')

    saveDict()
    showRankings()
