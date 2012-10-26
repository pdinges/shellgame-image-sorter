# -*- coding: utf-8 -*-

# Copyright (c) 2011--2012 Peter Dinges <pdinges@acm.org>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# Standard Python imports.
import contextlib
import cPickle
import math
import os
import shutil
import sys

# Package imports.
from PyQt4 import QtGui, Qt

# Local imports.
import shellgamesorter_ui
from filelistmodel import ImageListModel

SUPPORTED_IMAGE_EXTENSIONS = [ "jpg", "jpeg", "png", "gif" ]

class ShellGameSorter(QtGui.QMainWindow):
    """A small program for manually arranging images in order.  After the
       images have been sorted as desired, prepending the file names with
       numbers makes the order permanent.
       
    """
    def __init__(self, parent = None, flags = Qt.Qt.WindowFlags()):
        QtGui.QMainWindow.__init__(self, parent, flags)
        self._ui = shellgamesorter_ui.Ui_ShellGameSortWindow()
        self._ui.setupUi(self)
        self._setupSignals()
        
        self._sourceDirectory = ""
        self._model = None
        self._currentOrder = None
        self.setDirectory(os.getcwd())

    def openDirectory(self):
        """Ask the user to select a directory with images
           he or she wants to sort.
        
        """
        if self._sourceDirectory:
            # TODO Ask about saving changes.
            pass

        openDir = QtGui.QFileDialog.getExistingDirectory
        newDirectory = openDir(parent=self,
                               caption="Select a directory with images to sort",
                               directory=self._sourceDirectory)
        if not newDirectory:
            # User pushed 'Cancel'
            return
        else:
            self.setDirectory( newDirectory )
        
    
    def setDirectory(self, directory):
        """Set the image source directory and refresh the image list."""
        self._sourceDirectory = directory
        self._model = ImageListModel(directory, SUPPORTED_IMAGE_EXTENSIONS, parent=self)
        self._ui.galleryView.setModel(self._model)
        

    def applyOrder(self):
        """Make the current image order permanent.  This copies all images
           into the target directory, prefixing them with a suitable sequence
           number along the way.
           
        """
        fileInfoList = self._model.images()
        digits = int(math.ceil(math.log(len(fileInfoList), 10)))
        
        openDir = QtGui.QFileDialog.getExistingDirectory
        targetDirectory = openDir(parent=self,
                                  caption="Select the directory that receives the image copies",
                                  directory=self._sourceDirectory)
        

        # TODO Handle IOErrors.
        for i, fileInfo in enumerate(fileInfoList):
            targetFile = "{0:0{d}}@{1}".format(i, fileInfo.fileName(), d=digits)
            shutil.copyfile(str(fileInfo.absoluteFilePath()), os.path.join(str(targetDirectory), targetFile))
            
            
    def saveOrder(self):
        """Store the current image order in a file."""
        if not self._currentOrder:
            self.saveOrderAs()
        else:
            config = { "sourceDirectory": self._sourceDirectory,
                       "order": [ f.fileName() for f in self._model.images() ],
                     }
            with contextlib.closing(open(self._currentOrder, "w")) as configFile:
                cPickle.dump(config, configFile)
        
    
    def saveOrderAs(self):
        """Store the current image order in a file; ask which one first."""
        saveFile = QtGui.QFileDialog.getSaveFileName
        configFile = saveFile(parent=self,
                              caption="Save the image order")
        if not configFile:
            # User hit 'Cancel'
            return
        
        self._currentOrder = configFile
        self.saveOrder()


    def loadOrder(self):
        """Restore an image order from a previously saved file."""
        openFile = QtGui.QFileDialog.getOpenFileName
        configFileName = openFile(parent=self,
                                  caption="Load an image order")
        if not configFileName:
            # User hit 'Cancel'
            return
        
        # TODO Sanity checks, exception handling
        with contextlib.closing(open(configFileName, "r")) as configFile:
            config = cPickle.load(configFile)
            # TODO Add a dirty flag to the model to ask about saving
            if self._sourceDirectory != config["sourceDirectory"]:
                self._sourceDirectory = config["sourceDirectory"]
                self.setDirectory(self._sourceDirectory)
            self._model.order(config["order"])
        
        self._currentOrder = configFileName


    def _setupSignals(self):
        # Connect the menu items to local methods
        self._ui.actionOpenDirectory.triggered.connect( self.openDirectory )
        self._ui.actionApplyOrder.triggered.connect( self.applyOrder )
        self._ui.actionSaveOrder.triggered.connect( self.saveOrder )
        self._ui.actionSaveOrderAs.triggered.connect( self.saveOrderAs )
        self._ui.actionLoadOrder.triggered.connect( self.loadOrder )


if __name__ == "__main__":
    app = QtGui.QApplication( sys.argv )
    myapp = ShellGameSorter()
    myapp.show()
    status = app.exec_()
    sys.exit( status )
