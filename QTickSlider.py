
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class QTickSlider(QSlider):

    """
    QTickSlider is an reimplementation of QSlider that draws tick marks on the slider
    at specified positions. The marks can optionally have labels.
    """

    def __init__(self, *args, **kwargs):
        QSlider.__init__(self, *args, **kwargs)

        self.ticks = {}
        self.font = QFont('helvetica', 8, -1, False)
        self.showLabel = True

        #  define the thickness of the slider handle in pixels.
        self.sliderThickness = 12.


    def addTick(self, name, position, padding=10, color=[0,0,0],
            thickness=3.0, alpha=255):
        """
        addTick adds a tick to the slider.
        """

        self.ticks[name] = [position, padding/2, color, thickness, alpha]
        self.update()


    def removeAllTicks(self):
        """
        removeAllTicks removes all ticks from the slider
        """
        self.ticks = {}
        self.update()


    def keyPressEvent(self, ev):
        """
        keyPressEvent handles application keyboard input and responds to key presses
        """

        val = self.value()

        if (ev.key() == Qt.Key.Key_Right):
            #  increment slider one image
            self.setValue(val + 1)
        elif (ev.key() == Qt.Key.Key_Left):
            #  decrement slider one image
            self.setValue(val - 1)
        elif (ev.key() == Qt.Key.Key_Up):
            #  increment slider ten images
            self.setValue(val + 10)
        elif (ev.key() == Qt.Key.Key_Down):
            #  decrement slider ten images
            self.setValue(val - 10)


    def removeTick(self, tickName):
        """
        removeTick removes the specified tick mark from the slider. It will
        silently ignore ticks that don't exist.
        """
        try:
            #  remove the tick from the tick dict
            self.ticks.pop(tickName)
        except:
            #  silently fail when the tick doesn't exist
            pass

        self.update()


    def setFont(self, font, size=10.0, weight=-1, italics=False):

        self.font = QFont(font, size, weight, italics)


    def paintEvent(self, event):
        """
        paintEvent is called when the slider is drawn on screen. This handles the actual
        drawing of the tick marks on the slider.
        """

        #  paint the slider
        QSlider.paintEvent(self, event)

        #  create a painter to paint our marks
        painter = QPainter(self)
        painter.setFont(self.font)

        #  calculate the slider span
        span = float(self.maximum() - self.minimum() + 1)

        if (self.showLabel):
            #  get the font metrics and calculate text width and height
            fontMetrics = QFontMetrics(self.font)
            textHeight = fontMetrics.height()

        #  iterate through our ticks to plot
        for tick in self.ticks:

            #  calculate the position of the tick
            if (self.orientation() == Qt.Orientation.Horizontal):
                pctX = (self.ticks[tick][0] - self.minimum()) / span
                x1 = (pctX * self.width()) - ((pctX - 0.5) * self.sliderThickness)

                if (self.showLabel):
                    #  adjust the tick length
                    y1 = self.height() / 2

                    #  calculate the horizontal position of the text box
                    textWidth = fontMetrics.horizontalAdvance(tick)
                    textX = x1 - (textWidth / 2.0)
                    textY = -3
                else:
                    y1 = self.ticks[tick][1]
                y2 = self.height() - self.ticks[tick][1] - 1
                p1 = QPointF(x1,y1)
                p2 = QPointF(x1,y2)
            else:
                pctY = (self.ticks[tick][0] - self.minimum()) / span
                y1 = (pctY * self.height()) - ((pctY - 0.5) * self.sliderThickness)

                if (self.showLabel):
                    x1 = self.width() / 2

                    #  calculate the horizontal position of the text box
                    textWidth = fontMetrics.horizontalAdvance(tick)
                    textY = y1 - (textHeight / 2.0)
                    textX = x1
                else:
                    x1 = self.ticks[tick][1]
                x2 = self.width() - self.ticks[tick][1] - 1
                p1 = QPointF(x1,y1)
                p2 = QPointF(x2,y1)

            #  create the line to plot
            tickLine = QLineF(p1, p2)

            #  get the pen to draw the line
            pen = self.getPen(self.ticks[tick][2], self.ticks[tick][4], '_', self.ticks[tick][3])
            painter.setPen(pen)

            #  and finally draw it
            painter.drawLine(tickLine)

            if (self.showLabel):
                painter.drawText(QRectF(textX, textY, textWidth, textHeight), Qt.AlignmentFlag.AlignHCenter, str(tick))



    def getPen(self, color, alpha, style, width):
        """
        Returns a pen set to the color, style, thickness and alpha level provided.
        """

        #  return a pen
        penColor = QColor(color[0], color[1], color[2], alpha)
        pen = QPen(penColor)
        pen.setWidthF(width)
        if style.lower() == '-':
            pen.setStyle(Qt.PenStyle.DashLine)
        elif style.lower() == '.':
            pen.setStyle(Qt.PenStyle.DotLine)
        else:
            pen.setStyle(Qt.PenStyle.SolidLine)

        return pen
