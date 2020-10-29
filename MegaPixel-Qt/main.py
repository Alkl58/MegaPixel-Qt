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
    webpParams = ""

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
        self.checkBoxCustomSettings.stateChanged.connect(self.ToggleCustomSettings)
        # Avif
        self.checkBoxAvifLossless.stateChanged.connect(self.ToggleAvifLossless)
        # Webp
        self.checkBoxWebpQuality.stateChanged.connect(self.ToggleWebpQuality)
        self.checkBoxWebpSize.stateChanged.connect(self.ToggleWebpSize)
        self.checkBoxWebpPSNR.stateChanged.connect(self.ToggleWebpPSNR)
        self.checkBoxWebpLossless.stateChanged.connect(self.ToggleWebpLossless)
        self.groupBoxAvif.show()
        self.groupBoxWebp.hide()
        self.show()  # Show the GUI


    def ToggleAvifLossless(self):
        # This function disables visually Min/Max Q when lossless is toggled
        if self.checkBoxAvifLossless.isChecked() is True:
            self.spinBoxAvifMinQ.setEnabled(False)
            self.spinBoxAvifMaxQ.setEnabled(False)
            self.labelAvifMinQ.setEnabled(False)
            self.labelAvifMaxQ.setEnabled(False)
        else:
            self.spinBoxAvifMinQ.setEnabled(True)
            self.spinBoxAvifMaxQ.setEnabled(True)
            self.labelAvifMinQ.setEnabled(True)
            self.labelAvifMaxQ.setEnabled(True)

    def ToggleCustomSettings(self):
        # This function disables visually everything when custom settings is toggled
        if self.checkBoxCustomSettings.isChecked() is True:
            self.textEditCustomSettings.setEnabled(True)
            if self.comboBoxEncoders.currentIndex() == 0:
                self.SetAvifParams(True)
                self.textEditCustomSettings.setText(self.avifParams)
                self.groupBoxAvif.setEnabled(False)
            elif self.comboBoxEncoders.currentIndex() == 1:
                self.SetWebpParams(True)
                self.textEditCustomSettings.setText(self.webpParams)
                self.groupBoxWebp.setEnabled(False)
        else:
            self.textEditCustomSettings.setEnabled(False)
            if self.comboBoxEncoders.currentIndex() == 0:
                if self.checkBoxAvifLossless.isChecked() is False:
                    self.spinBoxAvifMinQ.setEnabled(True)
                    self.spinBoxAvifMaxQ.setEnabled(True)
                    self.labelAvifMinQ.setEnabled(True)
                    self.labelAvifMaxQ.setEnabled(True)
                self.groupBoxAvif.setEnabled(True)
            elif self.comboBoxEncoders.currentIndex() == 1:
                self.groupBoxWebp.setEnabled(True)


    def ToggleUiElems(self):
        if self.comboBoxEncoders.currentIndex() == 0:
            self.groupBoxWebp.hide()
            self.groupBoxAvif.show()
        elif self.comboBoxEncoders.currentIndex() == 1:
            self.groupBoxAvif.hide()
            self.groupBoxWebp.show()

    def ToggleWebpQuality(self):
        # Toggles Target Size, PSNR and Lossless visually off
        if self.checkBoxWebpQuality.isChecked() is True:
            self.checkBoxWebpSize.setChecked(False)
            self.checkBoxWebpPSNR.setChecked(False)
            self.checkBoxWebpLossless.setChecked(False)
            self.spinBoxWebpPSNR.setEnabled(False)
            self.spinBoxWebpSize.setEnabled(False)
            self.spinBoxWebpQ.setEnabled(True)
            self.comboBoxWebpLossless.setEnabled(False)

    def ToggleWebpSize(self):
        # Toggles Quality, PSNR and Lossless visually off
        if self.checkBoxWebpSize.isChecked() is True:
            self.checkBoxWebpQuality.setChecked(False)
            self.checkBoxWebpPSNR.setChecked(False)
            self.checkBoxWebpLossless.setChecked(False)
            self.spinBoxWebpPSNR.setEnabled(False)
            self.spinBoxWebpSize.setEnabled(True)
            self.spinBoxWebpQ.setEnabled(False)
            self.comboBoxWebpLossless.setEnabled(False)

    def ToggleWebpPSNR(self):
        # Toggles Quality, Target Size and Lossless visually off
        if self.checkBoxWebpPSNR.isChecked() is True:
            self.checkBoxWebpQuality.setChecked(False)
            self.checkBoxWebpSize.setChecked(False)
            self.checkBoxWebpLossless.setChecked(False)
            self.spinBoxWebpPSNR.setEnabled(True)
            self.spinBoxWebpSize.setEnabled(False)
            self.spinBoxWebpQ.setEnabled(False)
            self.comboBoxWebpLossless.setEnabled(False)

    def ToggleWebpLossless(self):
        # Toggles Quality, Target Size and PSNR visually off
        if self.checkBoxWebpLossless.isChecked() is True:
            self.checkBoxWebpQuality.setChecked(False)
            self.checkBoxWebpSize.setChecked(False)
            self.checkBoxWebpPSNR.setChecked(False)
            self.spinBoxWebpPSNR.setEnabled(False)
            self.spinBoxWebpSize.setEnabled(False)
            self.spinBoxWebpQ.setEnabled(False)
            self.comboBoxWebpLossless.setEnabled(True)

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
        self.SetAvifParams(False)
        self.SetWebpParams(False)
        asyncio.run(self.Encode())

    def SetAvifParams(self, custom):
        # Sets the params for avif encoding
        if self.checkBoxCustomSettings.isChecked is False or custom is True:
            self.avifParams = " --depth " + self.comboBoxAvifDepth.currentText()
            self.avifParams += " --yuv " + self.comboBoxAvifColorFormat.currentText()
            self.avifParams += " --range " + self.comboBoxAvifRange.currentText()
            if self.checkBoxAvifLossless.isChecked is False:
                self.avifParams += " --min " + str(self.spinBoxAvifMinQ.value()) + " --max " + str(self.spinBoxAvifMaxQ.value())
            else:
                self.avifParams += " --lossless"
            self.avifParams += " --tilerowslog2 " + str(self.spinBoxAvifTileRows.value()) + " --tilecolslog2 " + str(self.spinBoxAvifTileCols.value())
            self.avifParams += " --speed " + str(self.spinBoxAvifSpeed.value()) + " --jobs " + str(self.spinBoxAvifThreads.value())
        else:
            self.avifParams = self.textEditCustomSettings.toPlainText()

    def SetWebpParams(self, custom):
        if self.checkBoxCustomSettings.isChecked is False or custom is True:
            self.webpParams = " -preset " + self.comboBoxWebpPreset.currentText()
            if self.checkBoxAvifLossless.isChecked() is False:
                if self.checkBoxWebpPSNR.isChecked() is True:
                    self.webpParams += " -psnr " + str(self.spinBoxWebpPSNR.value())
                if self.checkBoxWebpSize.isChecked() is True:
                    self.webpParams += " -size " + str(self.spinBoxWebpSize.value() * 1000)
                if self.checkBoxWebpQuality.isChecked() is True:
                    self.webpParams += " -q " + str(self.spinBoxWebpQ.value())
                self.webpParams += " -m " + str(self.comboBoxWebpSpeed.currentIndex())
                self.webpParams += " -segments " + str(self.spinBoxWebpSegments.value())
                self.webpParams += " -sns " + str(self.spinBoxWebNoiseShaping.value())
                self.webpParams += " -f " + str(self.spinBoxWebFilterStrength.value())
                self.webpParams += " -sharpness " + str(self.spinBoxWebpFilterSharpness.value())
                if self.checkBoxWebpMultiThreading.isChecked() is True:
                    self.webpParams += " -mt "
            else:
                self.webpParams += " -z " + str(self.comboBoxWebpLossless.currentIndex())


    async def Encode(self):
        commands = [ ]
        for i in range(self.listWidgetQueue.count()):
            imageInput = self.listWidgetQueue.item(i).text()
            imgOutput = os.path.join(self.imageOutput, os.path.splitext(os.path.splitext(os.path.basename(imageInput))[0])[0])
            if self.comboBoxEncoders.currentIndex() == 0:
                avifCMD = "avifenc " + self.avifParams + " \"" + imageInput + "\" " + " \"" + imgOutput + ".avif\""
                commands.append(avifCMD)
                print(avifCMD)
            elif self.comboBoxEncoders.currentIndex() == 1:
                webpCMD = "cwebp " + self.webpParams + " \"" + imageInput + "\" " + " -o \"" + imgOutput + ".webp\""
                commands.append(webpCMD)
                print(webpCMD)

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
