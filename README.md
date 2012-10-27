Shell Game Image Sorter
=======================

This is a small program for manually arranging images in a specific
order.  After the images have been sorted as desired, the program can
*export* the order by prepending the file names with numbers.  Thus,
the Shell Game Image Sorter allows using custom orders of images in
programs that would otherwise only support alphabetical order.

The Shell Game Image Sorter is written in [Python2][python] on top of
the [PyQt][pyqt] library.  It runs (should run) on any platform
supported by both Python and PyQt, including Linux, Windows, and Mac
OS X.

### Screenshot

![Screenshot of the Shell Game Image Sorter.](https://raw.github.com/pdinges/shellgame-image-sorter/master/doc/unsorted.png)


Installation
------------

* Download and install version 2.x of the
  [Python programming language][python-dl].
* Download and install the [PyQt4 libraries][pyqt-dl].
* Download and extract, or checkout the contents of this repository.
* Compile the user interface description into a Python class by
  running the command `python2-pyuic4 shellgamesorter.ui >
  shellgamesorter_ui.py` in the directory containing
  `shellgamesorter.ui`.


Usage
-----

* Start the program by running the `shellgamesorter.py` script with
  the Python 2.x interpreter.  On Linux, the command is `python2
  shellgamesorter.py`.
* Open the directory containing the images you want to sort.  For
  example, consider a directory that contains the following files:
  1. `chickenshellgame.jpg`
  2. `shell_game.jpg`
  3. `shellgame.jpg`

  The program window will show thumbnails for all images in the
  directory, sorted by name.
  
  ![Program window after opening the example directory.](https://raw.github.com/pdinges/shellgame-image-sorter/master/doc/unsorted.png)
* Sort the images using drag and drop.  Dropping an image *A* onto
  another image *B* moves *A before B* in the list.  Dropping an image
  past the end of the list moves it to the end of the list.

  ![Program window while dragging an image in the example directory.](https://raw.github.com/pdinges/shellgame-image-sorter/master/doc/unsorted_drag.png)

  ![Program window after dropping an image in the example directory.](https://raw.github.com/pdinges/shellgame-image-sorter/master/doc/unsorted_drop.png)
* Select *Apply order* in the *File* menu to export the ordering.  The
  program will ask you to select a target directory.  All files will
  be *copied* to that directory.  The name of the copy will start with
  a prefix such that the alphabetical order equals the current order
  in the program.  In our example, the target directory will contain
  the files:
  1. `0@shell_game.jpg`
  2. `1@shellgame.jpg`
  3. `2@chickenshellgame.jpg`

  Using the *Save order* and *Load order* commands in the *File* menu,
  you can also save the current state into a file and restore it
  later.


License
-------

Copyright (c) 2011--2012 Peter Dinges.  The Shell Game Image Sorter is
available under the open-source [MIT License][mit-license].



[mit-license]: http://opensource.org/licenses/mit-license.php
[pyqt]: http://www.riverbankcomputing.com/software/pyqt/intro "Python bindings for the Qt toolkit."
[pyqt-dl]: http://www.riverbankcomputing.com/software/pyqt/download "Download PyQt4"
[python]: http://python.org "Python programming language"
[python-dl]: http://python.org/download/ "Download Python"
