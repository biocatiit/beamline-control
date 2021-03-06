from os import listdir
from os.path import join
from threading import Thread

import wx

from plot_gui import plot_gui
from ..utils.formula import calculate
from ..utils.Plotter import get_cols

class read_gui(wx.Frame):
    """GUI for scan output file reader"""
    def __init__(self, title):
        """
        Initializes the GUI.

        :param str title: The frame title.
        """
        super(read_gui, self).__init__(None, title=title)
        self.file_name = None
        self.files = None
        self.columns = []
        self.initUI()
        self.setConnections()
        self.Show()

    def initUI(self):
        """Initial all ui"""
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel = wx.Panel(self)
        self.panel_sizer = wx.GridBagSizer(10, 10)

        # Add directory field
        self.dir_picker = wx.DirPickerCtrl(self.panel, wx.ID_ANY, message="Select a directory")
        self.panel_sizer.Add(wx.StaticText(self.panel, label='Directory:'), pos=(0, 0), span=(1, 1),
                             flag=wx.ALIGN_CENTER_VERTICAL)
        self.panel_sizer.Add(self.dir_picker, pos=(0, 1), span=(1, 2), flag=wx.EXPAND)

        # Add Filename
        self.panel_sizer.Add(wx.StaticText(self.panel, label='Template Filename:'), pos=(1, 0), span=(1, 1), flag=wx.EXPAND)
        self.filename_widget = wx.StaticText(self.panel, label='-', size=(600, 20))
        self.panel_sizer.Add(self.filename_widget, pos=(1, 1), span=(1, 2), flag=wx.EXPAND)

        # Add Scalers
        self.panel_sizer.Add(wx.StaticText(self.panel, label='Available Devices:'), pos=(2, 0), span=(1, 1), flag=wx.EXPAND)
        self.all_scalers = wx.StaticText(self.panel, label='-', size=(600, 20))
        self.panel_sizer.Add(self.all_scalers, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)

        # Add Formula
        self.panel_sizer.Add(wx.StaticText(self.panel, label='Plot Formula:'), pos=(3, 0), span=(1, 1), flag=wx.EXPAND)
        self.formula = wx.TextCtrl(self.panel, value='It/Io')
        self.panel_sizer.Add(self.formula, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)

        # Add start button
        self.plot_button = wx.Button(self.panel, wx.ID_ANY, "Plot")
        self.panel_sizer.Add(self.plot_button, pos=(4, 0), span=(1, 3), flag=wx.ALIGN_CENTER)

        self.panel.SetSizer(self.panel_sizer)
        self.main_sizer.Add(self.panel, 1, wx.GROW)

        self.SetSizer(self.main_sizer)
        self.SetAutoLayout(True)
        self.main_sizer.Fit(self)

    def setConnections(self):
        """Binds events to GUI widgets and functions."""
        self.Bind(wx.EVT_DIRPICKER_CHANGED, self.onDirChanged, self.dir_picker)
        self.Bind(wx.EVT_BUTTON, self.plotPressed, self.plot_button)

    def onDirChanged(self, e):
        """
        Handle when a directory is selected

        :returns: Nothing. Just used to exit the function at points.
        """
        path = self.dir_picker.GetPath()
        print(str(path+ " is selected."))

        # Get columns from a file
        all_files = listdir(path)
        selected_file = ""
        for f in all_files:
            if '.0' in f and f.find('.') == f.rfind('.'):
                self.file_name = f[:f.find('.')]
                selected_file = f
                break

        if len(selected_file) < 0:
            print("Error : No file")
            return

        self.filename_widget.SetLabelText(str(self.file_name))

        # Get all columns
        self.columns = get_cols(join(path, selected_file))
        self.all_scalers.SetLabelText(", ".join(self.columns))

        self.files = []
        for f in all_files:
            if self.file_name in f and f.find('.') == f.rfind('.'):
                self.files.append(f)
        self.files = sorted(self.files)

        return

    def plotPressed(self, e):
        """Handle when 'Plot' is clicked"""

        if self.checkSettings():
            self.plot_panel = plot_gui(motor_x=self.columns[0], motor_y=self.columns[1], formula=self.formula.GetValue())
            self.plot_panel.Show()

            # Running plot on another thread
            t = Thread(target=self.startPlot)
            t.start()


    def startPlot(self):
        """Start plotting. Intended to be run in a thread."""
        for f in self.files:
            self.callPlot(join(self.dir_picker.GetPath(), f))


    def callPlot(self, full_path):
        """
        Trigger plot panel to read the file and plot

        :param str full_path: full path of the file
        """
        wx.CallAfter(self.plot_panel.plot, full_path)
        wx.Yield()

    def checkSettings(self):
        """
        Check all settings before generating plot

        :return: True if settings are good. False otherwise.
        :rtype: bool
        """
        if len(self.columns) == 0:
            print("Error : No Available Data")
            return False

        d = {c:1 for c in self.columns}
        try:
            calculate(self.formula.GetValue(), d)
        except ZeroDivisionError:
            pass
        except:
            print("Error : Invalid fomula")
            return False

        return True


def begin():
    """Starts the wx App"""
    app = wx.App()
    read_gui('MxMap Read')
    app.MainLoop()
