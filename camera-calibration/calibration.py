import cv2
import numpy as np

# Use webcam
cam = cv2.VideoCapture(1)

# Sources:
# https://longervision.github.io/2017/03/19/opencv-internal-calibration-chessboard/
# https://www.youtube.com/watch?v=FGqG1P36xxo


def calibrate():

    # Criteria for subpixer corner detection
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Chessboard pattern size. Size is the number of vertices, not squares
    pattern_size = (7, 7)

    # Object points (Beagle: Not sure how objp functions)
    objp = np.zeros((7*7, 3), np.float32)
    objp[:, :2] = np.mgrid[0:7, 0:7].T.reshape(-1, 2)

    imgpoints = []
    objpoints = []

    # Get 5 successful chessboard finds
    find_count = 0
    while find_count < 5:

        # Get and display frame to user
        ret, frame = cam.read()
        cv2.imshow("frame", frame)

        # Break if camera is dead
        if not ret:
            break

        # Wait for 'c' key to be pressed before trying to find chessboard
        # This allows user to get oriented before frame is analyzed
        c = cv2.waitKey(20) & 0xFF
        if c != ord('c'):
            continue

        # Convert frame grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Find chessboard corners
        found, corners = cv2.findChessboardCorners(gray, pattern_size, None)

        if found:
            find_count += 1
            print(find_count)

            # Objp will always be the same (Beagle: Not sure how objp functions)
            objpoints.append(objp)

            # Refine corners to have subpixel accuracy
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners)

            # Draw corners detected on chessboard and display to user
            cv2.drawChessboardCorners(frame, pattern_size, corners2, found)
            cv2.imshow("chkbd", frame)

    corners_world = []
    for row in range(pattern_size[1]):
        for col in range(pattern_size[0]):
            corners_world.append((col, row, 0))

    # Calibrate camera using the chessboard corner samples
    ret, matrix, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    return matrix, dist


mat, dst = calibrate()

while True:

    ret, frame = cam.read()
    if not ret:
        break

    cv2.imshow("orig", frame)

    # Undistort frame using calibration matrix and distances
    cv2.imshow("calib", cv2.undistort(frame, mat, dst))

    # Break program if ESC key is pressed
    c = cv2.waitKey(20) & 0xFF
    if c == 27:
        break


if __name__ == "__main__":
    calibrate()