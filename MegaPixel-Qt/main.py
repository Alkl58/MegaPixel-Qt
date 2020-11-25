# This Python file uses the following encoding: utf-8

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from multiprocessing.dummy import Pool
from functools import partial
from subprocess import call
from os import path
from pathlib import Path
import os
import sys
import time
import subprocess
import asyncio
import platform


class megapixel(QtWidgets.QMainWindow):

    imageOutput = None
    outputSet = False
    tempInput = None
    avifParams = None
    webpParams = None
    cjxlParams = None
    djxlParams = None
    mozjParams = None

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
        self.pushButtonRemoveQueue.clicked.connect(self.RemoveFromQueue)
        self.comboBoxEncoders.currentIndexChanged.connect(self.ToggleUiElems)
        self.checkBoxCustomSettings.stateChanged.connect(self.ToggleCustomSettings)

        # Avif
        self.checkBoxAvifLossless.stateChanged.connect(self.ToggleAvifLossless)

        # Webp
        self.checkBoxWebpQuality.stateChanged.connect(self.ToggleWebpQuality)
        self.checkBoxWebpSize.stateChanged.connect(self.ToggleWebpSize)
        self.checkBoxWebpPSNR.stateChanged.connect(self.ToggleWebpPSNR)
        self.checkBoxWebpLossless.stateChanged.connect(self.ToggleWebpLossless)

        # Jpegxl
        self.checkBoxJpegXlQ.stateChanged.connect(self.ToggleJpegXlQ)
        self.checkBoxJpegXlSize.stateChanged.connect(self.ToggleJpegXlSize)
        self.checkBoxJpegXlEncode.stateChanged.connect(self.ToggleJpegXlEncode)
        self.checkBoxJpegXlDecode.stateChanged.connect(self.ToggleJpegXlDecode)
        self.comboBoxJpegXlDecodeFormat.currentIndexChanged.connect(self.ToggleJpegXlDecodeSettings)

        # UI Toggle
        self.checkBoxJpegXlDecodesjpeg.hide()
        self.labelJpegXlDecodeQuality.hide()
        self.spinBoxJpegXlDecodeQ.hide()
        self.groupBoxAvif.show()
        self.groupBoxWebp.hide()
        self.groupBoxJpegXl.hide()
        self.groupBoxMozjpeg.hide()

        # Drag & Drop
        self.listWidgetQueue.setAcceptDrops(True)
        self.listWidgetQueue.viewport().installEventFilter(self)
        types = ['text/uri-list']
        types.extend(self.listWidgetQueue.mimeTypes())
        self.listWidgetQueue.mimeTypes  = lambda: types

        self.show()  # Show the GUI


    def eventFilter(self, source, event):
        # Drag & Drop Stuff
        if (event.type() == QtCore.QEvent.Drop and
            event.mimeData().hasUrls()):
            for url in event.mimeData().urls():
                self.addFile(url.toLocalFile())
            return True
        return super().eventFilter(source, event)

    def addFile(self, filepath):
        if os.path.isfile(filepath):
            # Adding a single File
            self.listWidgetQueue.addItem(filepath)
        else:
            # Batch add files with subfolders
            if self.checkBoxBatchAddSubfolders.isChecked() is True:
                self.tempInput = filepath
                for root, dirs, files in os.walk(filepath):
                    for file in files:
                        filepatha = os.path.join(root, file)
                        if filepatha.endswith((".jpg", ".jpeg", "png")):
                            self.listWidgetQueue.addItem(os.path.join(filepatha))
            else:
                # Batch add files without subfolder
                for filename in os.listdir(filepath):
                    if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg"):
                        self.listWidgetQueue.addItem(os.path.join(filepath, filename))



    def ToggleJpegXlDecodeSettings(self):
        if self.comboBoxJpegXlDecodeFormat.currentIndex() == 1:
            self.checkBoxJpegXlDecodesjpeg.show()
            self.labelJpegXlDecodeQuality.show()
            self.spinBoxJpegXlDecodeQ.show()
        else:
            self.checkBoxJpegXlDecodesjpeg.hide()
            self.labelJpegXlDecodeQuality.hide()
            self.spinBoxJpegXlDecodeQ.hide()

    def ToggleJpegXlEncode(self):
        if self.checkBoxJpegXlEncode.isChecked() is True:
            self.checkBoxJpegXlDecode.setChecked(False)
            self.checkBoxJpegXlQ.setEnabled(True)
            self.spinBoxJpegXlQ.setEnabled(True)
            self.checkBoxJpegXlSize.setEnabled(True)
            self.spinBoxJpegXlSize.setEnabled(True)
            self.labelJpegXlSpeed.setEnabled(True)
            self.comboBoxJpegXlSpeed.setEnabled(True)
            self.labelJpegXlDecodeFormat.setEnabled(False)
            self.comboBoxJpegXlDecodeFormat.setEnabled(False)
            self.checkBoxJpegXlDecodesjpeg.setEnabled(False)
            self.labelJpegXlDecodeQuality.setEnabled(False)
            self.spinBoxJpegXlDecodeQ.setEnabled(False)

    def ToggleJpegXlDecode(self):
        if self.checkBoxJpegXlDecode.isChecked() is True:
            self.checkBoxJpegXlEncode.setChecked(False)
            self.checkBoxJpegXlQ.setEnabled(False)
            self.spinBoxJpegXlQ.setEnabled(False)
            self.checkBoxJpegXlSize.setEnabled(False)
            self.spinBoxJpegXlSize.setEnabled(False)
            self.labelJpegXlSpeed.setEnabled(False)
            self.comboBoxJpegXlSpeed.setEnabled(False)
            self.labelJpegXlDecodeFormat.setEnabled(True)
            self.comboBoxJpegXlDecodeFormat.setEnabled(True)
            self.checkBoxJpegXlDecodesjpeg.setEnabled(True)
            self.labelJpegXlDecodeQuality.setEnabled(True)
            self.spinBoxJpegXlDecodeQ.setEnabled(True)

    # This function disables visually Min/Max Q when lossless is toggled
    def ToggleAvifLossless(self):
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

    # This function disables visually everything when custom settings is toggled
    # It also sets the text inside the textEdit Box
    def ToggleCustomSettings(self):
        if self.checkBoxCustomSettings.isChecked() is True:
            self.textEditCustomSettings.setEnabled(True)
            if self.comboBoxEncoders.currentIndex() == 0:               #  avif
                self.SetAvifParams(True)
                self.textEditCustomSettings.setText(self.avifParams)
                self.groupBoxAvif.setEnabled(False)
            elif self.comboBoxEncoders.currentIndex() == 1:             # webp
                self.SetWebpParams(True)
                self.textEditCustomSettings.setText(self.webpParams)
                self.groupBoxWebp.setEnabled(False)
            elif self.comboBoxEncoders.currentIndex() == 2:             # jpegxl
                if self.checkBoxJpegXlEncode.isChecked() is True:
                    self.SetJpegXlParams(True)
                    self.textEditCustomSettings.setText(self.cjxlParams)
                else:
                    self.SetJpegXlDecodeParams(True)
                    self.textEditCustomSettings.setText(self.djxlParams)
                self.groupBoxJpegXl.setEnabled(False)
            elif self.comboBoxEncoders.currentIndex() == 3:            # mozjpeg
                 self.SetMozJpegParams(True)
                 self.textEditCustomSettings.setText(self.mozjParams)
                 self.groupBoxMozjpeg.setEnabled(False)
        else: # CheckBox Custom Settings not checked
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
            elif self.comboBoxEncoders.currentIndex() == 2:
                self.groupBoxJpegXl.setEnabled(True)
            elif self.comboBoxEncoders.currentIndex() == 3:
                self.groupBoxMozjpeg.setEnabled(True)

    # Toggles the visibility of the encoder settings
    def ToggleUiElems(self):
        if self.comboBoxEncoders.currentIndex() == 0:
            self.groupBoxAvif.show()
            self.groupBoxWebp.hide()
            self.groupBoxJpegXl.hide()
            self.groupBoxMozjpeg.hide()
        elif self.comboBoxEncoders.currentIndex() == 1:
            self.groupBoxAvif.hide()
            self.groupBoxWebp.show()
            self.groupBoxJpegXl.hide()
            self.groupBoxMozjpeg.hide()
        elif self.comboBoxEncoders.currentIndex() == 2:
            self.groupBoxAvif.hide()
            self.groupBoxWebp.hide()
            self.groupBoxJpegXl.show()
            self.groupBoxMozjpeg.hide()
        elif self.comboBoxEncoders.currentIndex() == 3:
            self.groupBoxAvif.hide()
            self.groupBoxWebp.hide()
            self.groupBoxJpegXl.hide()
            self.groupBoxMozjpeg.show()

    # Toggles Target Size, PSNR and Lossless visually off
    def ToggleWebpQuality(self):
        if self.checkBoxWebpQuality.isChecked() is True:
            self.checkBoxWebpSize.setChecked(False)
            self.checkBoxWebpPSNR.setChecked(False)
            self.checkBoxWebpLossless.setChecked(False)
            self.spinBoxWebpPSNR.setEnabled(False)
            self.spinBoxWebpSize.setEnabled(False)
            self.spinBoxWebpQ.setEnabled(True)
            self.comboBoxWebpLossless.setEnabled(False)

    # Toggles Quality, PSNR and Lossless visually off
    def ToggleWebpSize(self):
        if self.checkBoxWebpSize.isChecked() is True:
            self.checkBoxWebpQuality.setChecked(False)
            self.checkBoxWebpPSNR.setChecked(False)
            self.checkBoxWebpLossless.setChecked(False)
            self.spinBoxWebpPSNR.setEnabled(False)
            self.spinBoxWebpSize.setEnabled(True)
            self.spinBoxWebpQ.setEnabled(False)
            self.comboBoxWebpLossless.setEnabled(False)

    # Toggles Quality, Target Size and Lossless visually off
    def ToggleWebpPSNR(self):
        if self.checkBoxWebpPSNR.isChecked() is True:
            self.checkBoxWebpQuality.setChecked(False)
            self.checkBoxWebpSize.setChecked(False)
            self.checkBoxWebpLossless.setChecked(False)
            self.spinBoxWebpPSNR.setEnabled(True)
            self.spinBoxWebpSize.setEnabled(False)
            self.spinBoxWebpQ.setEnabled(False)
            self.comboBoxWebpLossless.setEnabled(False)

    # Toggles Quality, Target Size and PSNR visually off
    def ToggleWebpLossless(self):
        if self.checkBoxWebpLossless.isChecked() is True:
            self.checkBoxWebpQuality.setChecked(False)
            self.checkBoxWebpSize.setChecked(False)
            self.checkBoxWebpPSNR.setChecked(False)
            self.spinBoxWebpPSNR.setEnabled(False)
            self.spinBoxWebpSize.setEnabled(False)
            self.spinBoxWebpQ.setEnabled(False)
            self.comboBoxWebpLossless.setEnabled(True)

    # Visually Toggles JpegXl Target Size / Quality
    def ToggleJpegXlQ(self):
        if self.checkBoxJpegXlQ.isChecked() is True:
            self.checkBoxJpegXlSize.setChecked(False)
            self.spinBoxJpegXlSize.setEnabled(False)
            self.spinBoxJpegXlQ.setEnabled(True)

    # Visually Toggles JpegXl Target Size / Quality
    def ToggleJpegXlSize(self):
        if self.checkBoxJpegXlSize.isChecked() is True:
            self.checkBoxJpegXlQ.setChecked(False)
            self.spinBoxJpegXlQ.setEnabled(False)
            self.spinBoxJpegXlSize.setEnabled(True)

    def OpenImageSource(self):
        if self.checkBoxBatchAdd.isChecked() is True:
            # Batch Adding
            imageInputBatch = str(QFileDialog.getExistingDirectory(self, "Select Input Directory"))
            if self.checkBoxBatchAddSubfolders.isChecked() is True:
                self.tempInput = imageInputBatch
                for root, dirs, files in os.walk(imageInputBatch):
                    for file in files:
                        filepath = root + os.sep + file
                        if filepath.endswith((".jpg", ".jpeg", "png")):
                            self.listWidgetQueue.addItem(str(os.path.join(filepath)))
            else:
                # Batch without Subfolders
                for filename in os.listdir(imageInputBatch):
                    if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg"):
                        self.listWidgetQueue.addItem(str(os.path.join(imageInputBatch, filename)))
        else:
            # Add a single file
            fileName, _ = QFileDialog.getOpenFileName(self, "Select Image...", "", "All Files (*)")
            self.listWidgetQueue.addItem(fileName) # Adds the selected input file to the queue

    def SetDestination(self):
        # Set output dir
        self.imageOutput = str(QFileDialog.getExistingDirectory(self, "Select Output Directory"))
        self.labelOutput.setText("Output: " + self.imageOutput)
        self.outputSet = True

    def ClearQueue(self):
        # Clears the Queue List
        self.listWidgetQueue.clear()

    def RemoveFromQueue(self):
        # Removes item(s) from the Queue List
        listItems = self.listWidgetQueue.selectedItems()
        if not listItems: return
        for item in listItems:
            self.listWidgetQueue.takeItem(self.listWidgetQueue.row(item))

    def showDialog(self, text):
        # Dialog to tell that encoding is finished
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(text)
        msgBox.setWindowTitle("MegaPixel")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

    def StartEncoding(self):
        # Main Encoding function
        if self.outputSet == True:
            self.SetAvifParams(False)
            self.SetWebpParams(False)
            self.SetJpegXlParams(False)
            self.SetMozJpegParams(False)
            asyncio.run(self.Encode())
        else:
            self.showDialog("Output Folder not set!")

    # Sets the params for avif encoding
    def SetAvifParams(self, custom):
        if self.checkBoxCustomSettings.isChecked() is False or custom is True:
            self.avifParams = " --depth " + self.comboBoxAvifDepth.currentText()
            self.avifParams += " --yuv " + self.comboBoxAvifColorFormat.currentText()
            self.avifParams += " --range " + self.comboBoxAvifRange.currentText()
            if self.checkBoxAvifLossless.isChecked() is False:
                self.avifParams += " --min " + str(self.spinBoxAvifMinQ.value()) + " --max " + str(self.spinBoxAvifMaxQ.value())
            else:
                self.avifParams += " --lossless"
            self.avifParams += " --tilerowslog2 " + str(self.spinBoxAvifTileRows.value()) + " --tilecolslog2 " + str(self.spinBoxAvifTileCols.value())
            self.avifParams += " --speed " + str(self.spinBoxAvifSpeed.value()) + " --jobs " + str(self.spinBoxAvifThreads.value())
        else:
            self.avifParams = self.textEditCustomSettings.toPlainText()

    # Sets the params for webp encoding
    def SetWebpParams(self, custom):
        if self.checkBoxCustomSettings.isChecked() is False or custom is True:
            self.webpParams = " -preset " + self.comboBoxWebpPreset.currentText()
            if self.checkBoxWebpLossless.isChecked() is False:
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

    # Sets the params for jpegxl encoding
    def SetJpegXlParams(self, custom):
        if self.checkBoxCustomSettings.isChecked() is False or custom is True:
            self.cjxlParams = " --speed=" + str(self.comboBoxJpegXlSpeed.currentIndex() + 3)
            if self.checkBoxJpegXlSize.isChecked() is True:
                self.cjxlParams += " --target_size=" + str(self.spinBoxJpegXlSize.value() * 1000)
            elif self.checkBoxJpegXlQ.isChecked() is True:
                self.cjxlParams += " --quality=" + str(self.spinBoxJpegXlQ.value())

    # Sets the params for jpegxl decoding
    def SetJpegXlDecodeParams(self, custom):
        if self.checkBoxCustomSettings.isChecked() is False or custom is True:
            self.djxlParams = ""
            if self.comboBoxJpegXlDecodeFormat.currentIndex() == 1:
                self.djxlParams += " --jpeg_quality=" + str(self.spinBoxJpegXlDecodeQ.value())
                if self.checkBoxJpegXlDecodesjpeg.isChecked() is True:
                    self.djxlParams += " --use_sjpeg"

    # Sets the MozJpeg params
    def SetMozJpegParams(self, custom):
        if self.checkBoxCustomSettings.isChecked() is False or custom is True:
            self.mozjParams = ""
            self.mozjParams += " -quality " + str(self.spinBoxMozjpegQ.value())
            self.mozjParams += " -tune-" + self.comboBoxMozjpegTune.currentText()

    # Sets the avif executable path
    def AvifPath(self):
        if platform.system() == "Windows":
            return os.path.join(os.path.dirname(__file__), "Encoders", "avif", "avifenc.exe") + " "
        else:
            return "avifenc "

    # Sets the jpegxl encoder executable path
    def EJpegXlPath(self):
        if platform.system() == "Windows":
            return os.path.join(os.path.dirname(__file__), "Encoders", "jpegxl", "cjpegxl.exe") + " "
        else:
            return "cjxl "

    # Sets the jpegxl decoder executable path
    def DJpegXlPath(self):
        if platform.system() == "Windows":
            return os.path.join(os.path.dirname(__file__), "Encoders", "jpegxl", "djpegxl.exe") + " "
        else:
            return "djxl "

    # Sets the mozjpeg executable path
    def MozJpegPath(self):
        if platform.system() == "Windows":
            return os.path.join(os.path.dirname(__file__), "Encoders", "mozjpeg", "cjpeg.exe") + " "
        else:
            return "cjpeg "

    # Sets the webp executable path
    def WebPPath(self):
        if platform.system() == "Windows":
            return os.path.join(os.path.dirname(__file__), "Encoders", "webp", "cwebp.exe") + " "
        else:
            return "cwebp "


    async def Encode(self):
        commands = [ ]
        # Creates argument list
        for i in range(self.listWidgetQueue.count()):
            imageInput = self.listWidgetQueue.item(i).text()
            if self.checkBoxBatchAddSubfolders.isChecked() is True and self.checkBoxBatchAdd.isChecked() is True:
                # With Subfolders
                tempFileName = os.path.basename(imageInput)
                n = len(self.tempInput)
                sub = imageInput[n:]
                n = len(tempFileName)
                sub = sub[:-n]
                if path.exists(self.imageOutput + sub) is False:
                    (Path(self.imageOutput + sub)).mkdir(parents=True, exist_ok=True)
                imgOutput = os.path.join(self.imageOutput + sub, os.path.splitext(os.path.basename(imageInput))[0])
            else:
                # Without Subfolders
                imgOutput = os.path.join(self.imageOutput, os.path.splitext(os.path.basename(imageInput))[0])

            if self.comboBoxEncoders.currentIndex() == 0:
                # avifencoding
                avifCMD = self.AvifPath() + " " + self.avifParams + " \"" + imageInput + "\" " + " \"" + imgOutput + ".avif\""
                commands.append(avifCMD)
            elif self.comboBoxEncoders.currentIndex() == 1:
                # webp encoding
                webpCMD = self.WebPPath() + self.webpParams + " \"" + imageInput + "\" " + " -o \"" + imgOutput + ".webp\""
                commands.append(webpCMD)
            elif self.comboBoxEncoders.currentIndex() == 2:
                # jpegxl encoding / decoding
                if self.checkBoxJpegXlEncode.isChecked() is True:
                    cjxlCMD = self.EJpegXlPath() + " \"" + imageInput + "\" \"" + imgOutput + ".jpg\"" + self.cjxlParams
                    commands.append(cjxlCMD)
                else:
                    djxlCMD = self.DJpegXlPath() + " \"" + imageInput + "\" \"" + imgOutput + "." + self.comboBoxJpegXlDecodeFormat.currentText() + "\" " + self.djxlParams
                    commands.append(djxlCMD)
            elif self.comboBoxEncoders.currentIndex() == 3:
                # mozjpeg encoding
                mozjCMD = self.MozJpegPath() + self.mozjParams + " -outfile \"" + imgOutput + ".jpg\" \"" + imageInput + "\""
                commands.append(mozjCMD)

        self.progressBar.setMaximum(len(commands))  # Sets the Max Value of Progressbar
        pool = Pool(self.spinBoxParallelWorkers.value())  # Sets the amount of workers
        for i, returncode in enumerate(pool.imap(partial(call, shell=True), commands)):  # Multi Threaded Encoding
            self.progressBar.setValue(self.progressBar.value() + 1 )  # Increases Progressbar Progress

        self.showDialog("Encoding Finished.")  # Message Box Finished Encoding
        self.progressBar.setValue(0)  # Resets the Progressbar


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = megapixel()
    app.exec_()
