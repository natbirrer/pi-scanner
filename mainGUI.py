# This application is a GUI interface for op25 designed for Raspberry Pi
# with Adafruit PiTFT 2.8 inch touchscreen
# Python 2.7
#
# Nathaniel Birrer
# 1/5/2019

import sys
import os
import signal
import subprocess
from Tkinter import *
import tkFont


class FullscreenWindow:

    def __init__(self):
        self.tk = Tk()
        #self.tk.attributes('-zoomed', True) #window maximized, not fullscreen
        self.tk.attributes("-fullscreen", True)
        #self.frame = Frame(self.tk)
        #self.frame.pack()
        self.state = True
        self.scanning = False
        self.tk.bind("<F11>", self.toggleFullscreen)
        self.tk.bind("<Escape>", self.exitFullscreen)
        self.tk.title("Fullscreen Test application")

        largeFont = tkFont.Font(family='Helvetica', size=30, weight='bold')
        smallFont = tkFont.Font(family='Helvetica', size=20, weight='bold')

        mainLabelText = StringVar()
        mainLabelText.set("Project 25 Radio Scanner")
        mainLabel = Message(self.tk, textvariable=mainLabelText, font=largeFont, width=500)
        
        self.statusLabelText = StringVar()
        self.statusLabelText.set("Status: idle")
        statusLabel = Message(self.tk, textvariable=self.statusLabelText, font=largeFont, width=500)

        mainButton = Button(self.tk, text="Scan/Stop", command=self.scanCurrentList, font=largeFont)

        global listFile
        listFile = StringVar()
        allListFiles = ["Succasunna_Main", "Succasunna_New",
                        "Morris_County_All"]
        listFile.set(allListFiles[0])
        listDropdown = OptionMenu(self.tk, listFile, *allListFiles)
        listDropdown.config(font=smallFont)
        listDropdownMenu = self.tk.nametowidget(listDropdown.menuname)
        listDropdownMenu.config(font=smallFont)

        self.tk.rowconfigure((0,2), weight=1)
        self.tk.columnconfigure((0,2), weight=1)
        mainLabel.grid(row=0, column=0, columnspan=2, sticky='EWNS')
        statusLabel.grid(row=1, column=0, columnspan=2, sticky='EWNS')
        listDropdown.grid(row=2, column=0, columnspan=1, sticky='EWNS')
        mainButton.grid(row=2, column=1, columnspan=1, sticky='EWNS')


    def toggleFullscreen(self, event=None):
        self.state = not self.state
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def exitFullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

    def scanCurrentList(self, event=None):
        # run op25 with trunk.tsv selected based on listFile
        if self.scanning:
            self.scanning = False
            self.statusLabelText.set("Status: idle")
            os.killpg(os.getpgid(scan.pid), signal.SIGTERM)
        else:
            self.scanning = True
            self.statusLabelText.set("Status: running")
            runOp25(listFile.get())


def runOp25(trunkFile):
    global scan
    fileName = "/home/pi/pi-scanner/"+trunkFile+".sh"
    scan = subprocess.Popen(fileName, shell=True, stdout=subprocess.PIPE,
                            preexec_fn=os.setsid)

if __name__ == '__main__':
    w = FullscreenWindow()
    w.tk.mainloop()

    # kill OP25 before exiting
    os.killpg(os.getpgid(scan.pid), signal.SIGTERM)
