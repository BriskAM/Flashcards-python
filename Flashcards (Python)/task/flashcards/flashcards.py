import logging
import random
from argparse import ArgumentParser

parser = ArgumentParser(description='This program is a flashcard handler')
parser.add_argument('-if', '--import_from')
parser.add_argument('-et', '--export_to')
args = parser.parse_args()

logging.basicConfig(filename='flashcard.log', level=logging.INFO)


def get_key_from_value(dictionary, target_value):
    for key, value in dictionary.items():
        if value == target_value:
            return key


class AlreadyExists(Exception):
    def __init__(self, card, mode):
        self.message = f'The {"card" if mode else "definition"} "{card}" already exists. Try again:'

    def __str__(self):
        return self.message


class CardDoesNotExist(Exception):
    def __init__(self, card):
        self.message = f'Can\'t remove "{card}": there is no such card.'

    def __str__(self):
        return self.message


class FlashcardHandler:
    def __init__(self):
        self.cards = {}
        self.mistakes = {}

    def add_card(self):
        logging.info('Adding a new flashcard.')
        print('The card:')
        while True:
            try:
                card = input().strip()
                if card in self.cards:
                    raise AlreadyExists(card, 1)
            except AlreadyExists as err:
                logging.warning(err)
                print(err)
            else:
                break
        print('The definition of the card:')
        while True:
            try:
                definition = input().strip()
                if definition in list(self.cards.values()):
                    raise AlreadyExists(definition, 0)
            except AlreadyExists as err:
                logging.warning(err)
                print(err)
            else:
                break
        self.cards.update({card: definition})
        self.mistakes.update({card: 0})
        message = f'The pair ("{card}":"{definition}") has been added.'
        print(message)
        logging.info(message)

    def remove_card(self):
        logging.info('Removing a flashcard.')
        print('Which card?')
        try:
            card = input()
            if card not in self.cards.keys():
                raise CardDoesNotExist(card)
        except CardDoesNotExist as err:
            logging.warning(err)
            print(err)
        else:
            print('The card has been removed.')
            logging.info(f'The card "{card}" has been removed.')
            del self.cards[card]
            del self.mistakes[card]

    def export_cards(self, arg):
        logging.info('Exporting flashcards.')
        if not arg:
            print('File name:')
            with open(input(), 'w') as file:
                for card in self.cards.keys():
                    file.write(f'{card}: {self.cards[card]}\n')
            message = f'{len(self.cards)} cards have been saved.'
            print(message)
            logging.info(message)
        else:
            with open(arg, 'w') as file:
                for card in self.cards.keys():
                    file.write(f'{card}: {self.cards[card]}\n')
            message = f'{len(self.cards)} cards have been saved.'
            print(message)
            logging.info(message)

    def import_cards(self, arg):
        logging.info('Importing flashcards.')
        if not arg:
            print('File name:')
            try:
                with open(input(), 'r') as file:
                    imported_cards = dict(line.strip().split(': ', 1) for line in file)
                    message = f'{len(imported_cards)} cards have been loaded.'
                    print(message)
                    logging.info(message)
                    self.cards.update(imported_cards)
                    self.mistakes.update({key: 0 for key in imported_cards.keys() if key not in self.cards.keys()})
            except FileNotFoundError:
                print("File not found.")
                logging.warning('File was not found to import from.')
        else:
            try:
                with open(arg, 'r') as file:
                    imported_cards = dict(line.strip().split(': ', 1) for line in file)
                    message = f'{len(imported_cards)} cards have been loaded.'
                    print(message)
                    logging.info(message)
                    self.cards.update(imported_cards)
                    self.mistakes.update({key: 0 for key in imported_cards.keys() if key not in self.mistakes.keys()})
            except FileNotFoundError:
                print("File not found.")
                logging.warning('File was not found to import from.')

    def ask(self):
        logging.info('Asking questions.')
        print('How many times to ask?')
        num_of_times = int(input())
        selected_cards = random.sample(list(self.cards.keys()), min(num_of_times, len(self.cards))) + [
            random.choice(list(self.cards.keys())) for _ in range(num_of_times - len(self.cards.keys()))]
        for card in selected_cards:
            print(f'Print the definition of "{card}":')
            answer = input()
            logging.info(f'Print the definition of "{card}": {answer}')
            if answer == self.cards[card]:
                message = 'Correct!'
                print(message)
                logging.info(message)
            elif answer in self.cards.values():
                correct_term = get_key_from_value(self.cards, answer)
                message = (f'Wrong. The right answer is "{self.cards[card]}", but your definition is correct for '
                           f'"{correct_term}".')
                print(message)
                logging.info(message)
                self.mistakes[card] += 1
            else:
                message = f'Wrong. The right answer is "{self.cards[card]}".'
                print(message)
                logging.info(message)
                self.mistakes[card] += 1

    @staticmethod
    def log():
        logging.info('Saving log.')
        print('File name:')
        file_name = input()
        with open(file_name, 'w') as file:
            with open('flashcard.log', 'r') as log_file:
                file.write(log_file.read())
        message = 'The log has been saved.'
        print(message)
        logging.info(message)

    def hardest_card(self):
        logging.info('Finding the hardest flashcard.')
        max_errors = max(self.mistakes.values(), default=0)
        if max_errors == 0:
            message = 'There are no cards with errors.'
            print(message)
            logging.info(message)
            return
        max_error_values = ['"' + key + '"' for key, value in self.mistakes.items() if value == max_errors]
        message = (f'The hardest card{"" if len(max_error_values) == 1 else "s"} '
                   f'{"is" if len(max_error_values) == 1 else "are"} '
                   f'{", ".join(max_error_values)}. You have {max_errors} error'
                   f'{"" if max_errors == 1 else "s"} answering it.')
        print(message)
        logging.info(message)

    def reset_stats(self):
        logging.info('Resetting flashcard statistics.')
        for key in self.mistakes:
            self.mistakes[key] = 0
        message = 'Card statistics have been reset.'
        print(message)
        logging.info(message)


def start_flash_card_handler():
    flash_cards = FlashcardHandler()
    if args.import_from:
        flash_cards.import_cards(args.import_from)
    if args.export_to:
        flash_cards.export_cards(args.export_to)
    while True:
        print('Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):')
        command = input()
        if command == 'add':
            flash_cards.add_card()
        elif command == 'remove':
            flash_cards.remove_card()
        elif command == 'import':
            flash_cards.import_cards(None)
        elif command == 'export':
            flash_cards.export_cards(None)
        elif command == 'ask':
            flash_cards.ask()
        elif command == 'reset stats':
            flash_cards.reset_stats()
        elif command == 'hardest card':
            flash_cards.hardest_card()
        elif command == 'log':
            flash_cards.log()
        elif command == 'exit':
            if args.export_to:
                flash_cards.export_cards(args.export_to)
            else:
                print('Bye bye!')
                logging.info('Exiting the flashcard handler.')
            break
        else:
            print('Not a valid command')
            logging.warning('Invalid command entered.')
            break


if __name__ == "__main__":
    start_flash_card_handler()
