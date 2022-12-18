import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QDialog, QDesktopWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

import MainWindow
import CreateFile
import DeleteFile

# Cвободный блок
FreeBlock = {"block_num": 0, "size": 0}

# Минимальный и максимальный размеры создаваемого файла (в Кб)
file_min_size = 18
file_max_size = 32

#=======================================================================================
#-------------------------------------- class File -------------------------------------
#=======================================================================================
# Класс, описывающий единицу хранения информации на диске - файл
class File():
  # в конструктор класса File передаются имя файла, размер файла
  # и номер блока, начиная с которого он располагается на диске
  def __init__(self, name, size, block):
    super().__init__()
    self.name = name
    self.size = size
    self.first_block = block

#=======================================================================================
#-------------------------------------- class Disk -------------------------------------
#=======================================================================================
# Класс, описывающий диск
class Disk():
  # в конструктор класса Disk передаются название диска и его размер
  def __init__(self, name, total_size):
    super().__init__()
    self.name = name
    self.total_size = total_size
    # в момент создания объекта диска на нем нет файлов
    self.free_size = total_size
    # список свободных блоков
    self.free_blocks = []
    # в список свободных блоков (free_blocks) добавляем пока единственный блок -
    # в момент создания объекта диска этот свободный блок занимает весь объем диска
    FreeBlock["block_num"] = 0
    FreeBlock["size"] = self.total_size
    self.free_blocks.append(FreeBlock)
    # список файлов на диске
    self.files = []

  # метод класса Disk - функция
  def EraseAll(self):
    self.free_size = 360
    self.free_blocks = []
    FreeBlock["block_num"] = 0
    FreeBlock["size"] = self.total_size
    self.free_blocks.clear()
    self.files.clear()
    self.free_blocks.append(FreeBlock)

  # метод класса Disk - функция FreeSize, возвращает размер свободного места на диске (кБ)
  def FreeSize(self):
    return self.free_size

  # метод класса Disk - функция UpdateFreeSize, изменяет размер свободного места на диске (переменную self.free_size)
  def UpdateFreeSize(self, size):
    self.free_size = size

  # метод класса Disk - функция FirstFreeBlock, возвращает номер первого свободного блока размером не менее file_size
  def FirstFreeBlock(self, file_size):
    for i in range(len(self.free_blocks)):
      size = self.free_blocks[i]["size"]
      if size >= file_size:
        return self.free_blocks[i]

  # метод класса Disk - функция SaveFile, записывает файл newfile начиная с блока № freeblock
  def SaveFile(self, newfile, freeblock):
    self.files.append(newfile)
    i = 0
    for i in range(len(self.free_blocks)):
      if self.free_blocks[i]["block_num"] == freeblock["block_num"]:
        self.free_blocks[i]["block_num"] += newfile.size
        self.free_blocks[i]["size"] -= newfile.size
        if self.free_blocks[i]["size"] == 0:
          self.free_blocks.pop(i)
        break
      i += 1

  # метод класса Disk - функция FindFile, ищет на диске (в списке self.files[]) файл с названием
  # file_name и, если находит, возвращает его номер в списке self.files[] или None в противном случае
  def FindFile(self, file_name):
    for i in range(len(self.files)):
      if self.files[i].name == file_name:
        return self.files[i]
    return None

  # метод класса Disk - функция ConcatFreeBlocks, объединяет два соседних свободных блока в
  # один после удаления файла из одного из этих соседних блоков
  def ConcatFreeBlocks(self, deleted_file):
    for i in range(len(self.free_blocks)):
      last = self.free_blocks[i]["block_num"] + self.free_blocks[i]["size"]
      if last  == deleted_file.first_block:
        self.free_blocks[i]["size"] += deleted_file.size
        return
    for i in range(len(self.free_blocks)):
      if deleted_file.first_block + deleted_file.size == self.free_blocks[i]["block_num"]:
        self.free_blocks[i]["size"] += deleted_file.size
        self.free_blocks[i]["block_num"] -= deleted_file.size
        return
    new_free_block = {"block_num": deleted_file.first_block, "size": deleted_file.size}
    self.free_blocks.append(new_free_block)

# Класс формы (окна) CreateFile
class CreateFile(QtWidgets.QDialog, CreateFile.Ui_CreateFile):
  def __init__(self):
    super().__init__()
    self.setupUi(self)

# Класс формы (окна) DeleteFile
class DeleteFile(QtWidgets.QDialog, DeleteFile.Ui_DeleteFile):
  def __init__(self):
    super().__init__()
    self.setupUi(self)

# Класс формы MainWindow - главного окна программы
class MainWindow(QtWidgets.QMainWindow, MainWindow.Ui_MainWindow):
  def __init__(self, disk):
    super().__init__()
    self.setupUi(self)

    # tableDiskView - это таблица, описывающая Диск
    self.tableWidget = self.tableDiskView
    self.tableWidget.setRowCount(20) # 20 строк
    self.tableWidget.setColumnCount(18) # 18 столбцов

    # Кнопки: Создать файл, Удалить файл, Удалить все файлы
    self.pushButtonCreateFile.clicked.connect(self.CreateNewFile)
    self.pushButtonDeleteFile.clicked.connect(self.DeleteFile)
    self.pushButtonDeleteAllFiles.clicked.connect(self.DeleteAllFiles)

    # Делаем так, чтобы таблица была растянута на все главное окно MainWindow
    header = self.tableDiskView.horizontalHeader()
    header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

    # Выводим название диска и свободный размер в главное окно MainWindow
    self.labelDiskName.setText(disk.name)
    self.labelDiskFreeSize.setText(str(disk.free_size) + " Kb")

    # Отображаем даблицу в главном окное MainWindow
    self.tableDiskView.show()

  # метод класса MainWindow - функция center, выводит главное окно программы по центру экрана
  def center(self):
    qr = self.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())

  # метод класса MainWindow - функция PantFileBlocks, визуально отображает место, занятое файлом
  def PaintFileBlocks(self, newfile):
    row = newfile.first_block // 18
    col = newfile.first_block % 18
    self.tableWidget.setItem(row, col, QTableWidgetItem(newfile.name))
    self.tableWidget.item(row, col).setBackground(QtGui.QColor(60, 120, 255))
    for i in range(newfile.size-1):
      col += 1
      if col >= 18:
        col = 0
        row += 1
      self.tableWidget.setItem(row, col, QTableWidgetItem())
      self.tableWidget.item(row, col).setBackground(QtGui.QColor(150, 180, 240))

  # метод класса MainWindow - функция CleanFileBlocks, "стирает" место, визуально занятое файлом
  def CleanFileBlocks(self, delfile):
    row = delfile.first_block // 18
    col = delfile.first_block % 18
    self.tableWidget.setItem(row, col, QTableWidgetItem(""))
    self.tableWidget.item(row, col).setBackground(QtGui.QColor(255, 255, 255))
    for i in range(delfile.size-1):
      col += 1
      if col >= 18:
        col = 0
        row += 1
      self.tableWidget.setItem(row, col, QTableWidgetItem())
      self.tableWidget.item(row, col).setBackground(QtGui.QColor(255, 255, 255))

  # метод класса MainWindow - функция DeleteFromDisk, удаляет файл из списка disk.files
  def DeleteFromDisk(self, delfile):
    for i in range(len(disk.files)):
      if disk.files[i].name == delfile.name:
        disk.files.pop(i)
        return

  # метод класса MainWindow - функция CreateNewFile, выводит на экран окно CreateFile,
  # после того как пользователь ввел название файла и его размер, создается новый
  # объект класса Файл и записывается на диск
  def CreateNewFile(self):
    dlg = CreateFile()
    if dlg.exec():
      file_size = int(dlg.filesize.text())
      if file_size < file_min_size or file_size > file_max_size:
        print("File size must be greater than 18 and less than 32 Kb!")
        return
      if file_size > disk.FreeSize():
        print("There is no free space on the disk!")
      else:
        file_name = dlg.filename.text()
        file_exists = disk.FindFile(file_name)
        if (file_exists):
          print("File with the same name already exists on disk!")
        else:
          block = disk.FirstFreeBlock(file_size)
          newfile = File(file_name, file_size, block["block_num"])
          disk.SaveFile(newfile, block)
          disk.UpdateFreeSize(disk.FreeSize() - file_size)
          self.PaintFileBlocks(newfile)
          self.labelDiskFreeSize.setText(str(disk.FreeSize()) + " Kb")

  # метод класса MainWindow - функция DeleteFile, выводит на экран окно DeleteFile,
  # после того как пользователь ввел название файла, данный файл ищется на диске, и,
  # если такой файл имеется на диске, то он удаляется
  def DeleteFile(self):
    dlg = DeleteFile()
    if dlg.exec():
      file_name = dlg.filename.text()
      file_to_del = disk.FindFile(file_name)
      if file_to_del == None:
        print("File not found!")
      else:
        disk.ConcatFreeBlocks(file_to_del)
        self.CleanFileBlocks(file_to_del)
        self.DeleteFromDisk(file_to_del)
        self.labelDiskFreeSize.setText(str(disk.FreeSize()) + " Kb")
        print("File deleted successfully!")

  # метод класса MainWindow - функция DeleteAllFiles, данная функция удаляет все файлы с диска
  def DeleteAllFiles(self):
    disk.EraseAll()
    row = 0
    col = 0
    for i in range(disk.total_size):
      self.tableWidget.setItem(row, col, QTableWidgetItem(""))
      self.tableWidget.item(row, col).setBackground(QtGui.QColor(255, 255, 255))
      col += 1
      if col >= 18:
        col = 0
        row += 1
    print("All files deleted successfully!")
    self.labelDiskFreeSize.setText(str(disk.FreeSize()) + " Kb")


app = QtWidgets.QApplication(sys.argv)
disk = Disk("DP360-V1", 360)
window = MainWindow(disk)
window.center()
window.show()
app.exec_()
