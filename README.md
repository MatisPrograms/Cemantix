# Cemantix Bot

This project is a bot designed to interact with the Cemantix website, which provides a word guessing game. The bot automates the process of guessing words and provides a ranking of the best guesses.

## Features

- Supports multiple languages (English and French).
- Automatically downloads necessary NLTK data.
- Maintains a dictionary of tested words and their scores.
- Provides a progress bar and rankings of the best guesses.
- Handles interruptions gracefully and saves progress.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/cemantix-bot.git
    cd cemantix-bot
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Download the NLTK data:
    ```sh
    python -m nltk.downloader wordnet omw-1.4
    ```

## Usage

To run the bot, use the following command:
```sh
python cemantix_bot.py -l <language_code> -t <word_to_test>
```

- `-l, --language`: Specify the language code (default is 'en' for English).
- `-t, --test`: Test a specific word.

Example:
```sh
python cemantix_bot.py -l en -t example
```

## How It Works

1. The bot initializes by setting up directories and downloading necessary data.
2. It loads the dictionary of previously tested words.
3. If a word is provided via the `-t` option, it is added to the list of words to test.
4. The bot iterates through the list of words, sending requests to the Cemantix website to get the score for each word.
5. It collects synonyms, hypernyms, and hyponyms for each word using NLTK's WordNet and adds them to the list of words to test.
6. The bot displays a progress bar and rankings of the best guesses.
7. If interrupted, the bot saves the current progress and exits gracefully.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
