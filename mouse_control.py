import time
import win32api
import win32con
import keyboard


class MouseControl:
    def __init__(self, delay: float = 4):
        self.current_cell = 0          # keeps track of which cell the mouse was last moved to

        self.stop = False
        self.create_escape()

        time.sleep(delay)

        self.initialise_mouse()

    def initialise_mouse(self):
        if not self.stop:
            # move mouse to the bottom left corner
            for i in range(6):
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, -150, 100)
                time.sleep(0.02)
            time.sleep(0.05)

            # move mouse onto the first cell
            for i in range(3):
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 50, -50)
                time.sleep(0.02)
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 47, -38)

    def do_word(self, word_indexes: list):
        if not self.stop:       # don't continue if the mouse control has been stopped
            # go to the start of the word
            self.go_to_cell(word_indexes[0], False)

            # input the rest of the word
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.02)

            for cell in word_indexes[1:]:
                self.go_to_cell(cell)

            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(0.02)

    def go_to_cell(self, target_cell: int, mouse_down: bool = True):
        # compute how far horizontally the mouse needs to move to reach the target cell
        x = (target_cell % 4) - (self.current_cell % 4)

        # compute how far vertically the mouse needs to move to reach the target cell
        y = (target_cell // 4) - (self.current_cell // 4)

        self.move_cells(x, y, mouse_down)               # move to the target cell
        self.current_cell = target_cell     # update where the mouse cursor is

    @staticmethod
    def move_cells(x: int, y: int, mouse_down: bool = True):
        # track the magnitude and direction of x and y separately
        x_magnitude = abs(x)
        y_magnitude = abs(y)
        x_direction = x // x_magnitude if x_magnitude > 0 else 1
        y_direction = y // y_magnitude if y_magnitude > 0 else 1

        while x_magnitude > 0 or y_magnitude > 0:
            if x_magnitude > 0 and y_magnitude > 0:
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x_direction * 43, y_direction * 43)
                x_magnitude -= 1
                y_magnitude -= 1
                if mouse_down:  # if switching between words, and not inputting a word, wait for less
                    time.sleep(0.07)
                else:
                    time.sleep(0.02)
            elif x_magnitude > 0:
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x_direction * 50, 0)
                x_magnitude -= 1
                if mouse_down:
                    time.sleep(0.07)
                else:
                    time.sleep(0.02)
            elif y_magnitude > 0:
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, y_direction * 50)
                y_magnitude -= 1
                if mouse_down:
                    time.sleep(0.07)
                else:
                    time.sleep(0.02)
            else:
                print(f"x={x_magnitude} y={y_magnitude}")

    def create_escape(self):
        keyboard.on_press_key("esc", self.on_press)

    def on_press(self, key):
        print("STOPPED MOUSE CONTROL.")
        self.stop = True


if __name__ == "__main__":
    mouse1 = MouseControl()
    mouse1.do_word([0, 4, 5])
