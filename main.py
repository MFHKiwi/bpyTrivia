"""
bpyTrivia (Better Python Trivia) is a Python Trivia game.

Classes:
    Question

Functions:
    b64tostring(b64_string)
    get_request(url)
    build_question_queue(encoded_questions)
    ask_question(question)
    start()

Misc variables:
    __version__
    API_URL
"""

__version__ = '0.0.1'

import requests
import base64
import queue
import random
import sys

API_URL = "https://opentdb.com/api.php"
QUERY_PARAMETERS = "?amount=10&encode=base64"
STATUS_OK = 200
DECORATOR = '-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-'


def b64tostring(b64_string):
    """
    Decode base64-encoded string straight to plain text.

    Used internally by Question object, hence why it is
    defined at the top of the script.

        Parameters:
            b64_string (str): A base64-encoded string

        Returns:
            (str): Decoded base64 string.
    """
    return base64.b64decode(b64_string).decode()


class Question:
    """
    A class to represent a trivia question.

    ...
    Attributes
    ----------
        q_type : str
            The type of question (multi-choice or true/false).
        difficulty : str
            The difficulty of the question.
        category : str
            The category that the question is in.
        question : str
            The question text prompt.
        correct_answer : str
            The correct answer to the question.
        incorrect_answer : str
            The incorrect answer(s) to the question.
    """

    def __init__(self, encoded_question):
        """
        Construct the class from encoded question.

        Not much logic, aside from a for loop
        to iterate over each encoded answer in incorrect_answers.

        Parameters
        ----------
            encoded_question : list
                A base64-encoded question as sent by the API.
        """
        self.q_type = b64tostring(encoded_question['type'])
        self.difficulty = b64tostring(encoded_question['difficulty'])
        self.category = b64tostring(encoded_question['category'])
        self.question = b64tostring(encoded_question['question'])
        self.correct_answer = b64tostring(encoded_question['correct_answer'])
        self.incorrect_answers = []
        for incorrect_answer in encoded_question['incorrect_answers']:
            self.incorrect_answers.append(b64tostring(incorrect_answer))


def get_request(url):
    """
    Send request to API.

        Parameters:
            url (str): URL request to send.

        Returns:
            json_data (list): JSON reply from API.
            (None): None type return if request is met with an error.
    """
    response = requests.get(url)
    if response.status_code == STATUS_OK:
        json_data = response.json()
        return json_data
    else:
        return None


def build_question_queue(encoded_questions):
    """
    Create queue of decoded questions.

        Parameters:
            encoded_questions (list): List of encoded questions to queue.

        Returns:
            question_queue (Queue): Queue of decoded questions.
    """
    question_queue = queue.Queue(maxsize=len(encoded_questions))
    for encoded_question in encoded_questions:
        question_queue.put(Question(encoded_question))
    return question_queue


def ask_question(question):
    """
    Ask the user the question.

        Parameters:
            question (Question): Question to display to user.

        Returns:
            (True): Return true if correct.
            (False): Return false if incorrect.
    """
    print(DECORATOR)
    print(f"Difficulty: {question.difficulty}")
    print(f"Category: {question.category}")
    print(DECORATOR)
    print(f"Question: {question.question}")
    print(DECORATOR)
    answers = question.incorrect_answers
    answers.append(question.correct_answer)
    random.shuffle(answers)
    for idx, x in enumerate(answers):
        print(f"[{idx}] {x}")
    while True:
        try:
            input_answer = int(input(":"))
            if input_answer < 0:
                raise ValueError("input_answer should be positive")
            print(DECORATOR)
            if answers[input_answer] == question.correct_answer:
                print("That is the correct answer!\n")
                return True
            else:
                print("That is not the correct answer!")
                print(f"The correct answer was: {question.correct_answer}.\n")
                return False
        except (ValueError, IndexError):
            print("That is not a valid input!")


def start():
    """Start function of program."""
    print(f"bpyTrivia v{__version__}")
    json_data = get_request(API_URL + QUERY_PARAMETERS)
    if json_data is None:
        print("Request received error. Exiting program...")
        sys.exit(1)
    encoded_questions = json_data['results']
    queue = build_question_queue(encoded_questions)
    correct_answers, incorrect_answers = 0, 0
    while not queue.empty():
        correct = ask_question(queue.get())
        if correct:
            correct_answers += 1
        else:
            incorrect_answers += 1
    if incorrect_answers < 1:
        incorrect_answers = 1
    ratio = correct_answers / incorrect_answers
    print(f"Correct answers: {correct_answers}" +
          f" Incorrect answers: {incorrect_answers}")
    print(f"Right/Wrong ratio: {ratio:.2f}:1")


if __name__ == "__main__":
    start()
