"""
This script is the main encoding worker class
which runs n-workers async in the threading model of qt.

Author: Alkl58
Date: 07.03.2021
"""
from multiprocessing.dummy import Pool
from functools import partial
from subprocess import call
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class Worker(QObject):
    """
    Worker Class

    Signals
    ----------
    progress : emits the progress of the subprogress in the run function
    finished : returns if all work is finished
    """
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    @pyqtSlot()
    def run(self, pool_size, queue):
        """
        Attributes
        ----------
        pool_size : sets the amount of workers
        queue : queue list
        """
        pool = Pool(pool_size)
        finished_count = 1
        for i, _ in enumerate(pool.imap(partial(call, shell=True), queue)):  # Multi Threaded Encoding
            self.progress.emit(finished_count)
            finished_count += 1
            print("Finished Worker: " + str(i))
        self.finished.emit()
