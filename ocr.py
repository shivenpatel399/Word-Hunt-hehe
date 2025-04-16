import cv2
import pytesseract


class OCR:
    def __init__(self):
        # Tesseract self.config
        self.config = "-l eng --psm 10 -c tessedit_char_whitelist='ABCDEFGHIJKLMNOPQRSTUVWXYZ|'"

        # Crop Ratios
        self.x_crop_ratio = 0.3         # the percentage of the left and right side is cut off
        self.y_crop_top_ratio = 0.35      # the percentage of the top that is cut off
        self.y_crop_bottom_ratio = 0.1

        # Character rectangle margin
        self.margin = 5

        self.board = []

        self.get_video_stream()

    def get_video_stream(self):
        video = cv2.VideoCapture(0)
        while True:         # keep getting each frame of the video stream
            ret, self.img = video.read()

            # if frame is read correctly ret is True
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            cv2.imshow("Video Input", self.img)

            # once space is pressed, stop capture and process the current frame
            if cv2.waitKey(1) == ord(" "):
                video.release()
                break

        self.preprocess_image()

    def preprocess_image(self):
        # Crop the image to just the board
        x_crop = round(self.img.shape[1] * self.x_crop_ratio)   # the actual number of pixels cut off based on the ratio
        y_crop_top = round(self.img.shape[0] * self.y_crop_top_ratio)
        y_crop_bottom = round(self.img.shape[0] * self.y_crop_bottom_ratio)
        self.img = self.img[y_crop_top:-y_crop_bottom, x_crop:-x_crop]

        # Preprocessing the image starts
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)    # Convert the image to gray scale
        ret, thresh = cv2.threshold(gray, 13, 255, cv2.THRESH_BINARY_INV)   # Perform threshold

        # Dilate image and slowly erode back until a letter can be found
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))  # Shape and size of erosion
        self.dilated = cv2.dilate(thresh, rect_kernel, iterations=1)

        self.find_letters()

    def find_letters(self):
        # Finding contours
        contours, hierarchy = cv2.findContours(self.dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Loop through the contours and convert them into rectangles
        rectangles = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            rectangles.append((x, y, w, h))

            # Draw contours of words
            cv2.drawContours(self.img, cnt, -1, (255, 0, 0), 3)

        # Sort rectangles by y position and group into 4
        rectangles.sort(key=lambda elem: elem[1])
        grouped_rectangles = [rectangles[n:n+4] for n in range(0, len(rectangles), 4)]

        # Sort the rectangles by x position within the groups of 4
        self.sorted_rectangles = []
        for group in grouped_rectangles:
            group.sort(key=lambda elem: elem[0])
            self.sorted_rectangles.extend(group)   # also ungroups the rectangles once they are sorted

        # print(sorted_rectangles)

        self.do_ocr()

    def do_ocr(self):
        # Create an inverted copy of image to be used by Tesseract
        img_tesseract = ~self.dilated.copy()

        # Loop through contours and do OCR with Tesseract
        for rect in self.sorted_rectangles:
            x, y, w, h = rect

            # Determine how much the image should be scaled to achieve 32px char height
            scale_factor = h / 32

            # Add margin to the rectangle
            x = x - self.margin
            y = y - self.margin
            w = w + 2 * self.margin
            h = h + 2 * self.margin

            # Drawing a rectangle around the contours
            cv2.rectangle(self.img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Crop to just the letter for giving input to OCR
            cropped = img_tesseract[y:y + h, x:x + w]

            # Rescale the image
            try:
                cropped = cv2.resize(cropped, None, fx=scale_factor, fy=scale_factor)
            except:
                pass

            for i in range(10):
                # Apply OCR on the cropped image
                text = pytesseract.image_to_string(cropped, config=self.config).strip()

                # Replace | symbol with I (JANK AF)
                text = text.replace("|", "I")

                if len(text) == 1:
                    break

                cropped = cv2.erode(cropped, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)), iterations=1)

                if i > 3:
                    print(f"More than {i} iterations required")
                    cv2.imshow(str(i), cropped)

            print(text)
            self.board.append(text)


if __name__ == "__main__":
    OCR()
