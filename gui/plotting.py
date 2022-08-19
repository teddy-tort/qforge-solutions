from PySide6.QtGui import QPen
import pyqtgraph as pg


color = {'dark red': (155, 0, 0),
         'dark green': (76, 145, 0),
         'dark blue': (0, 0, 200),
         'purple': (122, 23, 220),
         'dark orange': (204, 102, 0),
         'rose': (255, 101, 102),
         'light green': (51, 255, 153),
         'cyan': (0, 204, 204),
         'magenta': (228, 104, 232),
         'orange': (255, 152, 51),
         'red': (255, 0, 0),
         'blue': (0, 0, 255)}


class Plot(pg.PlotWidget):

    def __init__(self, x_label: str, y_label: str, pen: QPen,
                 right_axis: pg.ViewBox = None, date_axis_item: bool = False):
        """
        Create a plot widget with some shortcuts
        :param x_label: Label for the x-axis
        :param y_label: Label for the y-axis
        :param right_axis: a view box you wish to plot to the right axis
        :param date_axis_item: for time.time() style time stamp data on the x-axis
        """
        super(self.__class__, self).__init__()
        self.x_label = x_label
        self.y_label = y_label
        self.right_axis = right_axis
        self.setLabel('bottom', x_label)
        self.setLabel('left', y_label)
        if right_axis:
            self.scene().addItem(right_axis)
            self.getAxis('right').linkToView(right_axis)
            self.setXLink(right_axis)
            self.setLabel('right', right_axis.label)
            self.addLegend()
        if date_axis_item:
            self.setAxisItems({'bottom': pg.DateAxisItem('bottom')})

        self.pen = pen
        self.curve = self.plot(pen=pen, name=y_label)

        self.column_data_index_x = []
        self.column_data_index_y = []

    def initialize_plotter(self, column_data_x: list, column_data_y: list):
        if len(column_data_x) != len(column_data_y):
            raise ValueError("The number of x columns should match the number of y_columns")
        self.column_data_index_x = column_data_x
        self.column_data_index_y = column_data_y

        # need as many curves as there are columns to plot
        if self.right_axis:
            self.right_axis.column_data_index_x        # if there's a right axis, need those too
        else:
            self.curves *= len(column_data_y)

        for c in column_data_x:
            self.curves



class RightAxisPlot(pg.ViewBox):
    def __init__(self, label: str, pen: QPen):
        super(self.__class__, self).__init__()
        self.label = label

        self.pen = pen
        self.curve = pg.PlotCurveItem(pen=self.pens, name=label)
        self.addItem(self.curve)
        self.column_data_index_y = []

    def initialize_plotter(self, columns_data_y):
        pass
