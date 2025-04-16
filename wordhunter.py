from mouse_control import MouseControl
from wordhunt import WordHunt
import time


class WordHunter:
    def __init__(self):
        self.board = []
        self.get_board()

        self.answers = {}
        self.sorted = []
        self.get_answers()

        self.input_answers()

    def get_answers(self):
        # solve the WordHunt and find the answers
        print("Finding Answers...")
        word_hunt = WordHunt(self.board)
        self.answers = word_hunt.answers
        self.sorted = word_hunt.sorted
        print("Answers Found!")
        print(self.sorted)

    def input_answers(self):
        print("Inputting Answers...")
        # move the mouse to the start position
        mouse_control = MouseControl(0)
        # loop through every word and move the mouse to do them
        start_time = time.time()
        for word in self.sorted:
            word_indexes = self.answers[word]
            mouse_control.do_word(word_indexes)

            # stop once 55 seconds have elapsed
            time_elapsed = time.time() - start_time
            if time_elapsed > 55:
                break

        print("Done Solving WordHunt!")

    def get_board(self):
        # check that the inputted board is valid
        valid_input = False
        board_string = ""
        while not valid_input:
            board_string = input("Input the board:\n").replace(" ", "").lower()  # takes the board input as a string
            valid_input = self.verify_board_string(board_string)

        # converts the board from a string to a list
        self.board = [letter for letter in board_string]

    @staticmethod
    def verify_board_string(board_string: str):
        if len(board_string) != 16:
            print("ERROR: Board must have exactly 16 letters!")
            return False
        for letter in board_string:
            if not 97 <= ord(letter) <= 122:
                print("ERROR: Board must contain only letters!")
                return False
        return True


if __name__ == "__main__":
    word_hunter = WordHunter()
