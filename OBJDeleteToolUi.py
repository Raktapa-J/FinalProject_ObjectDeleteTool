try:
	from PySide6 import QtCore, QtGui, QtWidgets
	from shiboken6 import wrapInstance
except:
	from PySide2 import QtCore, QtGui, QtWidgets
	from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import os

ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'icons'))

class ObjectDeleteUIDialog(QtWidgets.QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.resize(350, 420)
		self.setWindowTitle('Object Delete UI')

		self.main_layout = QtWidgets.QVBoxLayout()
		self.setLayout(self.main_layout)
		self.setStyleSheet('''
			QDialog {
				background-color: #34B6BA;
				font-family: Tahoma;
			}
			QLabel {
				color: #FFFFFF;
				font-weight: bold;
				font-size: 14px;
			}
			QLabel#TitleLabel {
				color: #FFFFFF;  
				font-weight: bold;
				font-size: 20px;
			}
			QLineEdit {
				background-color: #FFFFFF;
				color: black;
				border-radius: 8px;
				font-size: 14px;
			}
			QPushButton {
				background-color: #A1E0E5;
				color: #34B6BA;
				border-radius: 10px;
				font-weight: bold;
				font-size: 14px;
			}
			QPushButton:hover {
				background-color: #66C7D1;
				color: #FFFFFF;
			}
		''')


		self.title_label = QtWidgets.QLabel('SELECT BASE OBJECT')
		self.title_label.setObjectName('TitleLabel') 
		self.title_label.setAlignment(QtCore.Qt.AlignCenter)
		self.main_layout.addWidget(self.title_label)


		self.icon_grid = QtWidgets.QGridLayout()
		self.main_layout.addLayout(self.icon_grid)

		self.object_buttons = {}
		self.obj_list = [
			'sphere', 'cube', 'cylinder', 'cone',
			'torus', 'prism', 'pyramid', 'pipe',
			'plane', 'disc', 'helix'
		]

		row, col = 0, 0
		for obj in self.obj_list:
			btn = QtWidgets.QPushButton(obj.capitalize())
			btn.setCheckable(True)
			btn.setMinimumHeight(30)
			self.icon_grid.addWidget(btn, row, col)
			self.object_buttons[obj] = btn

			col += 1
			if col > 2:
				col = 0
				row += 1


		self.name_label = QtWidgets.QLabel('NAME')
		self.main_layout.addWidget(self.name_label)
		self.name_lineEdit = QtWidgets.QLineEdit()
		self.main_layout.addWidget(self.name_lineEdit)


		self.number_label = QtWidgets.QLabel('NUMBER')
		self.main_layout.addWidget(self.number_label)

		self.number_layout = QtWidgets.QHBoxLayout()
		self.num_start = QtWidgets.QLineEdit()
		self.num_end = QtWidgets.QLineEdit()
		self.num_start.setPlaceholderText('num')
		self.num_end.setPlaceholderText('num')
		self.number_layout.addWidget(self.num_start)
		self.number_layout.addWidget(QtWidgets.QLabel('-'))
		self.number_layout.addWidget(self.num_end)
		self.main_layout.addLayout(self.number_layout)


		self.button_layout = QtWidgets.QHBoxLayout()
		self.main_layout.addLayout(self.button_layout)

		self.apply_button = QtWidgets.QPushButton('Apply')
		self.cancel_button = QtWidgets.QPushButton('Cancel')
		self.button_layout.addWidget(self.apply_button)
		self.button_layout.addWidget(self.cancel_button)

		self.main_layout.addStretch()

def run():
	global ui
	try:
		ui.close()
	except:
		pass
	ptr = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
	ui = ObjectDeleteUIDialog(parent=ptr)
	ui.show()
