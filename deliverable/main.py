from   collections     import deque
from   math            import cos, sin, radians
import re
import signal
import sys

from   PyQt5.QtWidgets import QApplication, QMainWindow
from   PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from   PyQt5.QtWidgets import QGraphicsEllipseItem

from   PyQt5.QtCore    import Qt, QRectF, QThread, pyqtSignal

from   PyQt5.QtGui     import QBrush, QColor, QPen

import sweeppy

CAMERA_WIDTH = 1280
CAMERA_FOV   = 70.42
MAX_POINTS   = 300


class Viewer(QGraphicsView):

    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.scene.addItem(CenterCircle(100))
        self.scene.addItem(CenterCircle(200))
        self.scene.addItem(CenterCircle(300))
        self.scene.addItem(CenterCircle(400))

        # TODO: BAD hack
        self.scene.addText(28*" " + "1m")
        self.scene.addText(53*" " + "2m")
        self.scene.addText(80*" " + "3m")

        self.sweep = Sweep(self.update_points)
        self.sweep.finished.connect(app.exit)
        self.sweep.start()

        self.detect = DetectNet(self.detect_net)
        self.detect.finished.connect(app.exit)
        self.detect.start()

        self.right = None
        self.left  = None

        self.points = deque()

    def update_points(self, samples):

        for sample in samples:

            angle = ((sample.angle / 1000) - 0) % 360
            distance = sample.distance
            strength = sample.signal_strength
            x =  distance * cos(radians(angle))
            y = -distance * sin(radians(angle))

            if self.right and self.left:
                if self.left > self.right:
                    hazard = self.right < angle < self.left
                else:
                    hazard = self.right - 360 < angle - 360 < self.left
                print(self.left, angle, self.right, hazard)
            else:
                hazard = False

            point = Point(x, y, strength, hazard)

            self.scene.addItem(point)

            if len(self.points) == MAX_POINTS:
                del_point = self.points.popleft()
                self.scene.removeItem(del_point)
            self.points.append(point)

    def detect_net(self, left, right):

        offset = (CAMERA_FOV / 2)

        if right - left < 100: return

        left  = offset - ((left  / CAMERA_WIDTH) * CAMERA_FOV)
        right = offset - ((right / CAMERA_WIDTH) * CAMERA_FOV)

        self.left  = left  % 360
        self.right = right % 360

        print(self.left, self.right)

    def resizeEvent(self, QResizeEvent):

        # No idea why this is required, but it is
        self.setSceneRect(0, 0, .1, .1)

        self.scene.setSceneRect(QRectF(self.geometry()))
        QGraphicsView.resizeEvent(self, QResizeEvent)

    def mousePressEvent(self, QMouseEvent):
        click = self.mapToScene(QMouseEvent.pos())
        self.createBall(click.x(), click.y())
        QGraphicsView.mousePressEvent(self, QMouseEvent)


class CenterCircle(QGraphicsEllipseItem):

    def __init__(self, radius):

        super().__init__(-radius, -radius, radius * 2, radius * 2)


class Point(QGraphicsEllipseItem):

    diameter = 10

    def __init__(self, x, y, opacity=255, hazard=False):

        radius = Point.diameter / 2

        super().__init__(x - radius, y - radius, Point.diameter, Point.diameter)

        self.setZValue(1)

        pen = QPen()
        pen.setWidth(0)
        self.setPen(pen)

        color = QColor(Qt.red if hazard else Qt.gray)
        color.setAlpha(opacity)
        brush = QBrush(color)

        self.setBrush(brush)


class DetectNet(QThread):

    signal = pyqtSignal(float, float)

    def __init__(self, func):
        super().__init__()

        self.signal.connect(func)
        self.regex = re.compile(r"bounding box \d\s+\(([-\d.]+), [-\d.]+\)\s+\(([-\d.]+), [-\d.]+\).*")

    def run(self):

        for line in sys.stdin:

            match = self.regex.match(line)

            if match is not None:

                left, right = tuple(map(float, match.groups()))
                self.signal.emit(left, right)


class Sweep(QThread):

    signal = pyqtSignal(object)

    def __init__(self, func):
        super().__init__()

        self.signal.connect(func)

    def run(self):

        with sweeppy.Sweep('/dev/ttyUSB0') as sweep:

            sweep.start_scanning()

            for scan in sweep.get_scans():
                self.signal.emit(scan.samples)


if __name__ == '__main__':

    app = QApplication([])

    window = QMainWindow()

    viewer = Viewer()

    window.setCentralWidget(viewer)
    window.showFullScreen()

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    sys.exit(app.exec_())
