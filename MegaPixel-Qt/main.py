# This Python file uses the following encoding: utf-8

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from multiprocessing.dummy import Pool
from functools import partial
from subprocess import call
import os
import sys
import time
import subprocess
import asyncio


class megapixel(QtWidgets.QMainWindow):

    imageOutput = ""
    avifParams = ""

    def __init__(self):

        super(megapixel, self).__init__()
        pth = os.path.join(os.path.dirname(__file__), "form.ui")  # Set path ui
        uic.loadUi(pth, self)  # Load the .ui file
        self.setFixedWidth(800)  # Set Window Width
        self.setFixedHeight(570)  # Set Window Height
        self.setWindowTitle("MegaPixel")  # Set Window Title
        self.pushButtonStart.clicked.connect(self.StartEncoding)
        self.pushButtonOpenSource.clicked.connect(self.OpenImageSource)
        self.pushButtonSaveTo.clicked.connect(self.SetDestination)
        self.pushButtonClearQueue.clicked.connect(self.ClearQueue)
        self.comboBoxEncoders.currentIndexChanged.connect(self.ToggleUiElems)
        self.show()  # Show the GUI

    def ToggleUiElems(self):
        if self.comboBoxEncoders.currentIndex() == 0:
            self.ShowAvifElems()
        elif self.comboBoxEncoders.currentIndex() == 1:
            self.HideAvifElems()

    def HideAvifElems(self):
        self.labelAvifMinQ.hide()
        self.spinBoxAvifMinQ.hide()
        self.labelAvifMaxQ.hide()
        self.spinBoxAvifMaxQ.hide()
        self.labelAvifDepth.hide()
        self.comboBoxAvifDepth.hide()
        self.labelAvifColorFormat.hide()
        self.comboBoxAvifColorFormat.hide()
        self.labelAvifRange.hide()
        self.comboBoxAvifRange.hide()
        self.labelAvifTileRows.hide()
        self.spinBoxAvifTileRows.hide()
        self.labelAvifTileColumns.hide()
        self.spinBoxAvifTileCols.hide()
        self.labelAvifThreads.hide()
        self.spinBoxAvifThreads.hide()
        self.labelAvifSpeed.hide()
        self.spinBoxAvifSpeed.hide()

    def ShowAvifElems(self):
        self.labelAvifMinQ.show()
        self.spinBoxAvifMinQ.show()
        self.labelAvifMaxQ.show()
        self.spinBoxAvifMaxQ.show()
        self.labelAvifDepth.show()
        self.comboBoxAvifDepth.show()
        self.labelAvifColorFormat.show()
        self.comboBoxAvifColorFormat.show()
        self.labelAvifRange.show()
        self.comboBoxAvifRange.show()
        self.labelAvifTileRows.show()
        self.spinBoxAvifTileRows.show()
        self.labelAvifTileColumns.show()
        self.spinBoxAvifTileCols.show()
        self.labelAvifThreads.show()
        self.spinBoxAvifThreads.show()
        self.labelAvifSpeed.show()
        self.spinBoxAvifSpeed.show()

    def OpenImageSource(self):
        if self.checkBoxBatchAdd.isChecked() is True:
            imageInputBatch = str(QFileDialog.getExistingDirectory(self, "Select Input Directory"))
            for filename in os.listdir(imageInputBatch):
                if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg"):
                    self.listWidgetQueue.addItem(str(os.path.join(imageInputBatch, filename)))
        else:
            fileName, _ = QFileDialog.getOpenFileName(self, "Select Image...", "", "All Files (*)")
            self.listWidgetQueue.addItem(fileName) # Adds the selected input file to the queue

    def SetDestination(self):
        self.imageOutput = str(QFileDialog.getExistingDirectory(self, "Select Output Directory"))
        self.labelOutput.setText("Output: " + self.imageOutput)

    def ClearQueue(self):
        self.listWidgetQueue.clear()

    def showDialog(self):
        # Dialog to tell that encoding is finished
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Encoding finished.")
        msgBox.setWindowTitle("Encoding finished.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

    def StartEncoding(self):
        self.SetAvifParams()
        asyncio.run(self.Encode())

    def SetAvifParams(self):
        # Sets the params for avif encoding
        self.avifParams = " --depth " + self.comboBoxAvifDepth.currentText()
        self.avifParams += " --yuv " + self.comboBoxAvifColorFormat.currentText()
        self.avifParams += " --range " + self.comboBoxAvifRange.currentText()
        self.avifParams += " --min " + str(self.spinBoxAvifMinQ.value()) + " --max " + str(self.spinBoxAvifMaxQ.value())
        self.avifParams += " --tilerowslog2 " + str(self.spinBoxAvifTileRows.value()) + " --tilecolslog2 " + str(self.spinBoxAvifTileCols.value())
        self.avifParams += " --speed " + str(self.spinBoxAvifSpeed.value()) + " --jobs " + str(self.spinBoxAvifThreads.value())

    async def Encode(self):
        commands = []
        for i in range(self.listWidgetQueue.count()):
            imageInput = self.listWidgetQueue.item(i).text()
            imgOutput = os.path.join(self.imageOutput, os.path.splitext(os.path.splitext(os.path.basename(imageInput))[0])[0])
            print(imgOutput)
            avifCMD = "avifenc " + self.avifParams + " \"" + imageInput + "\" " + " \"" + imgOutput + ".avif" + "\""
            commands.append(avifCMD)

        self.progressBar.setMaximum(len(commands))  # Sets the Max Value of Progressbar

        pool = Pool(self.spinBoxParallelWorkers.value())  # Sets the amount of workers

        for i, returncode in enumerate(pool.imap(partial(call, shell=True), commands)):  # Multi Threaded Encoding
            self.progressBar.setValue(self.progressBar.value() + 1 )  # Increases Progressbar Progress

        self.showDialog()  # Message Box Finished Encoding
        self.progressBar.setValue(0)  # Resets the Progressbar


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = megapixel()
    app.exec_()
