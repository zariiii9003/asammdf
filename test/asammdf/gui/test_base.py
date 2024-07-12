#!/usr/bin/env python
"""
Base Module for Testing GUI
 - responsible to set up Qt in order to run on multiple platforms
 - responsible to set up Application
class TestBase
    - responsible to set up and tearDown test workspace
    - responsible to create easy access to 'resource' directory
    - responsible to set up ErrorDialog for easy evaluation of raised exceptions
    - provide method `manual_use` created to help test development process
class DragAndDrop
    - responsible to perform Drag and Drop operations
     from source widget - specific point, to destination widget - specific point
"""
import os
import pathlib
import shutil
import sys
import threading
import time
import unittest
from unittest import mock

import numpy as np
import pyqtgraph
from PySide6 import QtCore, QtGui, QtTest, QtWidgets

if sys.platform == "win32":
    import win32api
    import win32con

from asammdf.gui.utils import excepthook

if sys.platform == "win32":
    os.environ["QT_QPA_PLATFORM"] = "windows"
elif sys.platform == "linux":
    os.environ["QT_QPA_PLATFORM"] = "xcb"
elif sys.platform == "darwin":
    os.environ["QT_QPA_PLATFORM"] = "cocoa"
else:
    os.environ["QT_QPA_PLATFORM"] = "windows"

app = pyqtgraph.mkQApp()
app.setOrganizationName("py-asammdf")
app.setOrganizationDomain("py-asammdf")
app.setApplicationName("py-asammdf")


@unittest.skipIf(sys.platform == "darwin", "Test Development on MacOS was not done yet.")
class TestBase(unittest.TestCase):
    """
    - setUp and tearDown test workspace
    - provide method to execute widget
    - setUp ErrorDialog for evaluation raised exceptions
    """

    longMessage = False

    resource = os.path.normpath(os.path.join(os.path.dirname(__file__), "resources"))
    test_workspace = os.path.join(os.path.join(os.path.dirname(__file__), "test_workspace"))
    patchers = []
    # MockClass ErrorDialog
    mc_ErrorDialog = None

    def shortDescription(self):
        return self._testMethodDoc

    @staticmethod
    def manual_use(widget, duration=None):
        """
        Execute Widget for debug/development purpose.

        Parameters
        ----------
        duration : float | None
            duration in seconds
        """
        widget.showMaximized()
        app.exec()
        if duration is None:
            duration = 3600
        else:
            duration = abs(duration)

        widget.showNormal()

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(int(duration * 1000), loop.quit)
        loop.exec_()

        widget.showNormal()

    @staticmethod
    def processEvents(timeout=0.001):
        app.sendPostedEvents()

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(int(timeout * 1000), loop.quit)
        loop.exec_()

    def setUp(self) -> None:
        if os.path.exists(self.test_workspace):
            shutil.rmtree(self.test_workspace)
        os.makedirs(self.test_workspace)
        self.mc_ErrorDialog.reset_mock()
        self.processEvents()

    @classmethod
    def setUpClass(cls):
        sys.excepthook = excepthook
        for patcher in (mock.patch("asammdf.gui.utils.ErrorDialog"),):
            _ = patcher.start()
            cls.patchers.append(patcher)
        cls.mc_ErrorDialog = _

    @classmethod
    def tearDownClass(cls):
        for patcher in cls.patchers:
            patcher.stop()

    def tearDown(self):
        self.processEvents()
        if self.test_workspace and pathlib.Path(self.test_workspace).exists():
            shutil.rmtree(self.test_workspace)

    def mouseClick_RadioButton(self, qitem):
        QtTest.QTest.mouseClick(
            qitem,
            QtCore.Qt.MouseButton.LeftButton,
            QtCore.Qt.KeyboardModifiers(),
            QtCore.QPoint(2, qitem.height() / 2),
        )
        self.processEvents()

    def mouseClick_CheckboxButton(self, qitem):
        # Same function
        self.mouseClick_RadioButton(qitem)

    def mouseClick_WidgetItem(self, qitem):
        if isinstance(qitem, QtWidgets.QTreeWidgetItem):
            widget = qitem.treeWidget()
        elif isinstance(qitem, QtWidgets.QListWidgetItem):
            widget = qitem.listWidget()
        else:
            raise NotImplementedError
        QtTest.QTest.mouseClick(
            widget.viewport(),
            QtCore.Qt.MouseButton.LeftButton,
            QtCore.Qt.KeyboardModifiers(),
            widget.visualItemRect(qitem).center(),
        )
        self.processEvents(0.5)

    def mouseDClick_WidgetItem(self, qitem):
        if isinstance(qitem, QtWidgets.QTreeWidgetItem):
            widget = qitem.treeWidget()
        elif isinstance(qitem, QtWidgets.QListWidgetItem):
            widget = qitem.listWidget()
        else:
            raise NotImplementedError
        QtTest.QTest.mouseDClick(
            widget.viewport(),
            QtCore.Qt.MouseButton.LeftButton,
            QtCore.Qt.KeyboardModifiers(),
            widget.visualItemRect(qitem).center(),
        )
        self.processEvents(0.5)


class Pixmap:
    COLOR_BACKGROUND = "#000000"
    COLOR_RANGE = "#000032"
    COLOR_CURSOR = "#e69138"

    @staticmethod
    def is_black(pixmap):
        """
        Excepting cursor
        """
        cursor_x = None
        cursor_y = None
        cursor_color = None
        image = pixmap.toImage()

        for y in range(image.height()):
            for x in range(image.width()):
                color = QtGui.QColor(image.pixel(x, y))
                if color.name() != Pixmap.COLOR_BACKGROUND:
                    if not cursor_x and not cursor_y and not cursor_color:
                        cursor_x = x
                        cursor_y = y + 1
                        cursor_color = color
                        continue
                    elif cursor_x == x and cursor_y == y and cursor_color == color:
                        cursor_y += 1
                        continue
                    else:
                        return False
        return True

    @staticmethod
    def is_colored(pixmap, color_name, x, y, width=None, height=None):
        image = pixmap.toImage()

        offset = 1
        y = y + offset

        if not width:
            width = image.width()
        if not height:
            height = image.height()

        for _y in range(offset, image.height()):
            for _x in range(image.width()):
                color = QtGui.QColor(image.pixel(_x, _y))
                if _x < x or _y < y:
                    continue
                # De unde 2?
                elif (_x > width - x) or (_y > height - y - 3):
                    break
                if color.name() != color_name:
                    print(x, y, width, height)
                    print(_x, _y, color.name())
                    return False
        return True

    @staticmethod
    def has_color(pixmap, color_name):
        image = pixmap.toImage()

        for y in range(image.height()):
            for x in range(image.width()):
                color = QtGui.QColor(image.pixel(x, y))
                if color.name() == color_name:
                    return True
        return False

    @staticmethod
    def color_names(pixmap):
        color_names = set()

        image = pixmap.toImage()
        for y in range(image.height()):
            for x in range(image.width()):
                color = QtGui.QColor(image.pixel(x, y))
                color_names.add(color.name())
        return color_names

    @staticmethod
    def cursors_x(pixmap):
        image = pixmap.toImage()

        cursors = []
        possible_cursor = None

        for x in range(image.width()):
            count = 0
            for y in range(image.height()):
                color = QtGui.QColor(image.pixel(x, y))
                # Skip Black
                if color.name() == Pixmap.COLOR_BACKGROUND:
                    continue
                if not possible_cursor:
                    possible_cursor = color.name()
                if possible_cursor != color.name():
                    break
                count += 1
            else:
                if count >= image.height() - 3:
                    cursors.append(x)

        return cursors


class DragAndDrop:
    def __init__(self, src_widget, dst_widget, src_pos, dst_pos):
        src_offset = dst_offset = QtCore.QPoint(0, 1)
        if hasattr(src_widget, "header"):
            src_offset = QtCore.QPoint(0, src_widget.header().geometry().height() + 1)
        if hasattr(dst_widget, "header"):
            dst_offset = QtCore.QPoint(0, dst_widget.header().geometry().height() + 1)

        t_move = threading.Thread(
            target=dnd_worker,
            args=(
                src_widget.mapToGlobal(src_pos) + src_offset,
                dst_widget.mapToGlobal(dst_pos) + dst_offset,
            ),
        )
        t_move.start()

        while t_move.is_alive():
            QtWidgets.QApplication.instance().processEvents()
            time.sleep(0.001)
        QtWidgets.QApplication.instance().processEvents()


if sys.platform == "win32":

    def dnd_worker(start, end):
        x_vals = np.linspace(start.x(), end.x(), 10)
        y_vals = np.linspace(start.y(), end.y(), len(x_vals))
        print(x_vals, y_vals)

        # Move the mouse to the starting position
        win32api.SetCursorPos((start.x(), start.y()))

        # Perform left mouse button down event
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, start.x(), start.y(), 0, 0)

        # Move the mouse to the ending position
        for x, y in zip(x_vals, y_vals):
            win32api.SetCursorPos((int(x), int(y)))
            time.sleep(0.01)

        # Perform left mouse button up event
        win32api.SetCursorPos(
            (
                end.x(),
                end.y(),
            )
        )
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, end.x(), end.y(), 0, 0)

        # Perform the mouse left-button down and up events
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, end.x(), end.y(), 0, 0)
        time.sleep(0.05)  # Small delay to simulate a real click
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, end.x(), end.y(), 0, 0)

else:

    def dnd_worker(start, end):
        pass
