# ToolTip widget based on this code : https://stackoverflow.com/a/56749167
# Was modified to correspond to the color theme of our program.

from tkinter import *
from customtkinter import *

class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        """
        Displays text in tooltip window
        """
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() +15
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.attributes("-topmost", True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT, background="#3B3B3B", 
                      font=("tahoma", "8", "normal"), 
                      foreground="#ffffff", highlightthickness=1)
        label.pack(ipadx=1)


    def hidetip(self):
        """
        Destroys the window ToolTip when the mouse's cursor is moved out of the object
        """
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    """
    Creates a ToolTip when the mouse's cursor is on the object where the ToolTip is a assigned

    Parameters
    ----------
    widget : object
        define the object where the ToolTip is assigned
    text : str
       text which appear with the ToolTip
    """
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)