

from builtins import str
from qgis.PyQt.QtCore import QSettings, QFileInfo
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox


# from module RASTERCALC by Barry Rowlingson

def lastUsedDir(plugin_name):

    settings = QSettings()
    return settings.value("/%s/lastDir" % plugin_name, "", type=str)


def setLastUsedDir(plugin_name, lastDir):

    path = QFileInfo(lastDir).absolutePath()
    settings = QSettings()
    settings.setValue("/%s/lastDir" % plugin_name, str(path))


def new_file_path(parent, show_msg, path, filter_text):
    output_filename, __ = QFileDialog.getSaveFileName(parent,
                                                  show_msg,
                                                  path,
                                                  filter_text)
    if not output_filename:
        return ''
    else:
        return output_filename


def old_file_path(parent, show_msg, filter_extension, filter_text):
    input_filename, __ = QFileDialog.getOpenFileName(parent,
                                                 parent.tr(show_msg),
                                                 filter_extension,
                                                 filter_text)
    if not input_filename:
        return ''
    else:
        return input_filename


def info(main_window, title, msg):

    QMessageBox.information(main_window, title, msg)


def warn(main_window, title, msg):

    QMessageBox.warning(main_window, title, msg)
