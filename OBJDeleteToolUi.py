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
        self.resize(400, 550)
        self.setWindowTitle('Object Delete UI')

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.setStyleSheet('''
            QDialog { background-color: #34B6BA;
            	font-family: Tahoma; }
                           
            QLabel { color: #FFFFFF;
            	font-weight: bold; 
            	font-size: 14px; }
                           
            QLabel#TitleLabel { font-size: 30px;
            	font-family: Impact; }
                           
            QLineEdit, QComboBox { background-color: #FFFFFF;
            	color: black; border-radius: 8px;
            	font-size: 14px; }
                           
            QPushButton { background-color: #FFFFFF; 
            	color: #34B6BA; 
            	border-radius: 10px; 
            	font-weight: bold; 
            	font-size: 14px; }
                           
            QPushButton:hover { background-color: #009696;
            	color: #FFFFFF; }
        ''')

        self.title_label = QtWidgets.QLabel('SELECT BASE OBJECT')
        self.title_label.setObjectName('TitleLabel')
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        self.icon_grid = QtWidgets.QGridLayout()
        self.main_layout.addLayout(self.icon_grid)
        self.object_buttons = {}
        self.obj_list = [
            'sphere', 'cube', 'cylinder', 'cone', 'torus', 'prism',
            'pyramid', 'pipe', 'plane', 'disc', 'helix'
        ]

        row, col = 0, 0
        for obj in self.obj_list:
            icon_path = os.path.join(ICON_PATH, f"{obj}.png")
            btn = QtWidgets.QPushButton()
            btn.setCheckable(True)
            btn.setMinimumHeight(50)
            btn.setIcon(QtGui.QIcon(icon_path))
            btn.setIconSize(QtCore.QSize(30, 30))
            btn.setText(obj.capitalize())
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

        self.filter_label = QtWidgets.QLabel('FILTER OPTIONS')
        self.filter_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.filter_label)

        self.color_layout = QtWidgets.QHBoxLayout()
        self.color_label = QtWidgets.QLabel('Color:')
        self.color_combo = QtWidgets.QComboBox()
        self.color_combo.addItems([
            'All', 'Red', 'Orange', 'Yellow', 'Green', 'Cyan',
            'Blue', 'Purple', 'Pink', 'Brown', 'White', 'Black'
        ])
        self.color_layout.addWidget(self.color_label)
        self.color_layout.addWidget(self.color_combo)
        self.main_layout.addLayout(self.color_layout)

        self.size_layout = QtWidgets.QHBoxLayout()
        self.size_label = QtWidgets.QLabel('Size:')
        self.size_combo = QtWidgets.QComboBox()
        self.size_combo.addItems(['All', 'Small (1-50)', 'Medium (51-100)', 'Large (101+)'])
        self.size_layout.addWidget(self.size_label)
        self.size_layout.addWidget(self.size_combo)
        self.main_layout.addLayout(self.size_layout)

        self.type_layout = QtWidgets.QHBoxLayout()
        self.type_label = QtWidgets.QLabel('Type:')
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(['All', 'Geometry', 'NURBS', 'Curve', 'Light'])
        self.type_layout.addWidget(self.type_label)
        self.type_layout.addWidget(self.type_combo)
        self.main_layout.addLayout(self.type_layout)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.apply_button = QtWidgets.QPushButton('Apply')
        self.cancel_button = QtWidgets.QPushButton('Cancel')
        self.button_layout.addWidget(self.apply_button)
        self.button_layout.addWidget(self.cancel_button)
        self.main_layout.addLayout(self.button_layout)

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


    ui.apply_button.clicked.connect(lambda: None)
    ui.cancel_button.clicked.connect(ui.close)
