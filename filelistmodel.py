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
import os
import os.path

# Package imports.
from PyQt4 import QtCore, QtGui


# The one MIME type this model supports: a '|'-separated list of row indices.
ROW_MIME_TYPE = "x-application/shellgame-sorter-rows"

class ImageListModel(QtCore.QAbstractListModel):
    """An image file name list model that supports arranging the images
       in arbitrary order.  Orders can be imported and exported as lists.
       
       Beside the programmatic reordering, the model implements manual
       arrangement via drag and drop move actions: moving an item A onto
       another item B places A before B in the list.
       
    """
    def __init__(self, path, extensions, order=None, parent=None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self._path = os.path.abspath(str(path))
        self._extensions = extensions

        # Load existing 
        def isImage(f):
            if not os.path.isfile(os.path.join(self._path, f)):
                return False
            for e in extensions:
                if f.lower().endswith("." + e):
                    return True
            return False
        
        self._files = [ QtCore.QFileInfo(os.path.join(self._path, f))
                        for f in os.listdir(self._path) if isImage(f) ]
        if order:
            self.order(order)
        self.__thumbnailCache = QtGui.QPixmapCache()


    def images(self):
        """Get the list of image names in their current order."""
        return [ f.fileName() for f in self._files ]
    
    
    def order(self, order):
        """Arrange the model's image file names in the given order.
           
           Invalid (non-existing) files will be ignored; files not mentioned
           are moved to the end of the list keeping their relative
           current order. 
           
        """ 
        self.beginResetModel()
        
        # Map file names to ranks in the given order
        ranking = dict([ (f, i) for i, f in enumerate(order) ])
        l = len(ranking)
        
        def cmp(f1, f2):
            # Compare tuples (new rank, old rank)
            r1 = ranking.get(f1.fileName(), l + self._files.index(f1))
            r2 = ranking.get(f2.fileName(), l + self._files.index(f2))
            if r1 < r2:
                return -1
            elif r1 == r2:
                return 0
            else:
                return 1
        
        self._files = list(sorted(self._files[:], cmp=cmp))
        self.endResetModel()
        
        
    def rowCount( self, parent = QtCore.QModelIndex() ):
        return len( self._files )
    
    
    def data( self, index, role = QtCore.Qt.DisplayRole ):
        if not index.isValid() or index.row() >= len(self._files):
            return QtCore.QVariant()
        
        fileInfo = self._files[ index.row() ]
        
        if role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant( fileInfo.fileName() )
        
        elif role == QtCore.Qt.DecorationRole:
            thumbnail = self.__thumbnailCache.find(fileInfo.absoluteFilePath())
            if not thumbnail:
                # The thumbnail is a centered square with maximal sides.
                pixmap = QtGui.QPixmap(fileInfo.absoluteFilePath())
                pixmap = pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatioByExpanding)
                quad = QtCore.QRect(0, 0, 100, 100)
                quad.moveCenter(QtCore.QPoint(pixmap.width() / 2, pixmap.height() / 2))
                thumbnail = pixmap.copy(quad)
                self.__thumbnailCache.insert(fileInfo.absoluteFilePath(), thumbnail)

            return QtCore.QVariant( thumbnail )
        
        return QtCore.QVariant() 

    
    #- Drag and Drop ---------------------------------------------------------- 
    
    def flags(self, index):
        f = QtCore.QAbstractListModel.flags(self, index)
        if index.isValid():
            f |= QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
        return f
    

    def supportedDragActions(self):
        return QtCore.Qt.MoveAction
    

    def supportedDropActions(self):
        return QtCore.Qt.MoveAction


    def mimeTypes(self):
        """List the supported MIME types.  This model only exports
           '|'-separated lists of row numbers in the model.
           
        """
        # Drag and drop ceases to work if the custom MIME type is not announced. 
        return [ ROW_MIME_TYPE ]


    def mimeData(self, indexes):
        mimeData = QtCore.QMimeData()
        
        rowString = "|".join([ str(i.row()) for i in indexes if i.isValid() ])
        mimeData.setData(ROW_MIME_TYPE, rowString)
        
        return mimeData
    
    
    def dropMimeData(self, data, action, row, column, parentIndex):
        """Insert the items with the listed row numbers before the parentIndex.
           Their current relative order is preserved.  An invalid parentIndex 
           moves the items to the end of the list.
           
        """
        if action == QtCore.Qt.IgnoreAction:
            return True
        
        if column > 0:
            return False
        
        # An invalid parent index will move the items to the end of the list.
        if parentIndex.isValid():
            targetRow = parentIndex.row()
        else:
            targetRow = self.rowCount()
        
        if data and data.hasFormat(ROW_MIME_TYPE):

            sourceRows = [ int(r) for r in data.data(ROW_MIME_TYPE).split("|") ]
            sourceItems = [ self._files[r] for r in sourceRows ]
            
            for sourceRow in sorted(sourceRows, reverse=True):
                self.beginRemoveRows(QtCore.QModelIndex(), sourceRow, sourceRow)
                del self._files[sourceRow]
                self.endRemoveRows()

                if sourceRow < targetRow:
                    targetRow -= 1

            self.beginInsertRows(QtCore.QModelIndex(), targetRow, targetRow + len(sourceItems))
            self._files = self._files[:targetRow] + sourceItems + self._files[targetRow:]
            self.endInsertRows()

            return True

        return False
