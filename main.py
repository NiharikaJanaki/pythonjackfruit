# main.py
import wx
from gui import MainFrame

def main():
    app = wx.App(redirect=False)
    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
