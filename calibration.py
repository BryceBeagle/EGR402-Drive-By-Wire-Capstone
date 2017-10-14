import cv2
import numpy as np


def calibrate():

    cam = cv2.VideoCapture("left01.jpg")

    pattern_size = (9, 6)

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        found, corners_image = cv2.findChessboardCorners(gray, pattern_size, None)

        points_image = []
        if found:
            cv2.drawChessboardCorners(frame, pattern_size, corners_image, found)
            points_image.append(corners_image)

        cv2.imshow("frame", frame)

        c = cv2.waitKey(0) & 0xFF
        if c == 27:
            break

    corners_world = []
    for row in range(pattern_size[1]):
        for col in range(pattern_size[0]):
            corners_world.append((col, row, 0))

    points_world = np.zeros(( ))


if __name__ == "__main__":
    calibrate()