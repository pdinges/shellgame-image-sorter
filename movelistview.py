# $Id: movelistview.py 667 2011-05-15 15:43:31Z elwedgo $

# Package imports.
from PyQt4 import QtCore, QtGui

class MoveListView(QtGui.QListView):
    """A specialized QListView that snaps drop events to the closest list item.
       
       Snapping the drop events prevents placing list items in empty space, which
       reorders the items visually without notifying the model. 
    """
    def dropEvent(self, event):
        # The modified behavior only makes sense in icon view mode.
        if self.viewMode() != QtGui.QListView.IconMode:
            return QtGui.QListView.dropEvent(self, event)
        
        # Compute the number of visible item columns and rows.
        gridCols = self.viewport().width() // (self.gridSize().width() + self.spacing())
        gridRows = self.viewport().height() // (self.gridSize().height() + self.spacing())
        
        # Compute the drop event's column and row (these might be greater than
        # the number of grid columns and rows: there is some empty space next
        # to the items).
        point = event.pos()
        pointCol = min(gridCols, point.x() // (self.gridSize().width() + self.spacing()))
        pointRow = min(gridRows, point.y() // (self.gridSize().height() + self.spacing()))

        # Determine which model row is closest to the drop position; if
        # necessary, adjust it to have items dropped to the right of other
        # items go in between.
        modelIndexRow = min((pointRow * gridCols) + pointCol, self.model().rowCount() - 1)
        if (pointRow >= gridRows or
            pointCol >= gridCols or
            point.x() > (pointCol + 0.5) * (self.gridSize().width() + self.spacing())):
            modelIndexRow += 1

        # Find the model index of the drop target.  Use an empty index
        # to denote the end of the list.
        if modelIndexRow < self.model().rowCount(): 
            modelIndex = self.model().index(modelIndexRow, self.modelColumn())
        else:
            modelIndex = QtCore.QModelIndex()
        
        self.model().dropMimeData(event.mimeData(),
                                  event.possibleActions(),
                                  modelIndexRow,
                                  self.modelColumn(),
                                  modelIndex)
