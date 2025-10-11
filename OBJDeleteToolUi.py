try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from shiboken6 import wrapInstance
except:
    from PySide2 import QtCore, QtGui, QtWidgets
    from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import os
import colorsys

ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'icons'))

# ===== HSV Color Ranges for Filtering =====
COLOR_RANGES = {
    'Red':      ((0.95, 1.0),  (0.7,1.0), (0.3,1.0)),  
    'Orange':   ((0.05,0.1),   (0.7,1.0), (0.3,1.0)),
    'Yellow':   ((0.13,0.18),  (0.5,1.0), (0.5,1.0)),
    'Green':    ((0.25,0.4),   (0.5,1.0), (0.3,1.0)),
    'Cyan':     ((0.45,0.5),   (0.5,1.0), (0.3,1.0)),
    'Blue':     ((0.55,0.7),   (0.5,1.0), (0.3,1.0)),
    'Purple':   ((0.75,0.85),  (0.5,1.0), (0.3,1.0)),
    'Pink':     ((0.9,0.95),   (0.5,1.0), (0.5,1.0)),
    'Brown':    ((0.05,0.1),   (0.5,1.0), (0.2,0.5)),
    'White':    ((0,1),        (0,0.1),   (0.9,1.0)),
    'Black':    ((0,1),        (0,0.1),   (0,0.2))
}

# ===== UI =====
class ObjectDeleteUIDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(400, 550)
        self.setWindowTitle('Object Delete UI')

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.setStyleSheet('''
            QDialog { background-color: #34B6BA; font-family: Tahoma; }
            QLabel { color: #FFFFFF; font-weight: bold; font-size: 14px; }
            QLabel#TitleLabel { font-size: 30px; font-family: Impact; }
            QLineEdit, QComboBox { background-color: #FFFFFF; color: black; border-radius: 8px; font-size: 14px; }
            QPushButton { background-color: #FFFFFF; color: #34B6BA; border-radius: 10px; font-weight: bold; font-size: 14px; }
            QPushButton:hover { background-color: #009696; color: #FFFFFF; }
        ''')

        # Title
        self.title_label = QtWidgets.QLabel('SELECT BASE OBJECT')
        self.title_label.setObjectName('TitleLabel')
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        # Object buttons
        self.icon_grid = QtWidgets.QGridLayout()
        self.main_layout.addLayout(self.icon_grid)
        self.object_buttons = {}
        self.obj_list = ['sphere', 'cube', 'cylinder', 'cone', 'torus', 'prism', 'pyramid', 'pipe', 'plane', 'disc', 'helix']

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

        # Name filter
        self.name_label = QtWidgets.QLabel('NAME')
        self.main_layout.addWidget(self.name_label)
        self.name_lineEdit = QtWidgets.QLineEdit()
        self.main_layout.addWidget(self.name_lineEdit)

        # Number filter
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

        # Extra Filters
        self.filter_label = QtWidgets.QLabel('FILTER OPTIONS')
        self.filter_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.filter_label)

        # Color filter
        self.color_layout = QtWidgets.QHBoxLayout()
        self.color_label = QtWidgets.QLabel('Color:')
        self.color_combo = QtWidgets.QComboBox()
        self.color_combo.addItems([
            'All', 'Red', 'Orange', 'Yellow', 'Green', 'Cyan', 'Blue', 'Purple', 'Pink', 'Brown', 'White', 'Black'
        ])
        self.color_layout.addWidget(self.color_label)
        self.color_layout.addWidget(self.color_combo)
        self.main_layout.addLayout(self.color_layout)

        # Size filter
        self.size_layout = QtWidgets.QHBoxLayout()
        self.size_label = QtWidgets.QLabel('Size:')
        self.size_combo = QtWidgets.QComboBox()
        self.size_combo.addItems(['All', 'Small (1-50)', 'Medium (51-100)', 'Large (101+)'])
        self.size_layout.addWidget(self.size_label)
        self.size_layout.addWidget(self.size_combo)
        self.main_layout.addLayout(self.size_layout)

        # Type filter
        self.type_layout = QtWidgets.QHBoxLayout()
        self.type_label = QtWidgets.QLabel('Type:')
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(['All', 'Geometry', 'NURBS', 'Curve', 'Light'])
        self.type_layout.addWidget(self.type_label)
        self.type_layout.addWidget(self.type_combo)
        self.main_layout.addLayout(self.type_layout)

        # Action buttons
        self.button_layout = QtWidgets.QHBoxLayout()
        self.apply_button = QtWidgets.QPushButton('Apply')
        self.cancel_button = QtWidgets.QPushButton('Cancel')
        self.button_layout.addWidget(self.apply_button)
        self.button_layout.addWidget(self.cancel_button)
        self.main_layout.addLayout(self.button_layout)

        self.main_layout.addStretch()


# ===== HSV Helper Functions =====
def get_object_hsv(obj):
    shapes = cmds.listRelatives(obj, shapes=True) or []
    for s in shapes:
        shader = cmds.listConnections(s, type='shadingEngine')
        if shader:
            materials = cmds.ls(cmds.listConnections(shader), materials=True)
            if materials:
                for mat in materials:
                    if cmds.attributeQuery('color', node=mat, exists=True):
                        rgb = cmds.getAttr(f'{mat}.color')[0]
                        hsv = colorsys.rgb_to_hsv(*rgb)
                        return hsv
    return None

def color_match(hsv, color_name):
    if color_name not in COLOR_RANGES or hsv is None:
        return False
    h_range, s_range, v_range = COLOR_RANGES[color_name]
    h,s,v = hsv
    # Special case for Red wrap-around
    if color_name == 'Red' and (h >= 0.95 or h <= 0.05):
        return True
    return h_range[0]<=h<=h_range[1] and s_range[0]<=s<=s_range[1] and v_range[0]<=v<=v_range[1]

# ===== Main Filtering Function =====
def get_objects_by_filters(name='', num_range=None, color='All', size='All', obj_type='All', base_objs=[]):
    objects = cmds.ls(type='transform')
    filtered = []

    for obj in objects:
        if base_objs and not any(btn.lower() in obj.lower() for btn in base_objs):
            continue

        if name and name.lower() not in obj.lower():
            continue

        if num_range:
            nums = [int(s) for s in ''.join([c if c.isdigit() else ' ' for c in obj]).split()]
            if not nums or not (num_range[0] <= nums[0] <= num_range[1]):
                continue

        if obj_type != 'All':
            type_map = {'Geometry':'mesh','NURBS':'nurbsSurface','Curve':'nurbsCurve','Light':'light'}
            shapes = cmds.listRelatives(obj, shapes=True) or []
            if not any(cmds.objectType(s) == type_map[obj_type] for s in shapes):
                continue

        if color != 'All':
            hsv = get_object_hsv(obj)
            if not color_match(hsv, color):
                continue

        bbox = cmds.exactWorldBoundingBox(obj)
        size_value = max(bbox[3]-bbox[0], bbox[4]-bbox[1], bbox[5]-bbox[2])
        if size != 'All':
            if size == 'Small (1-50)' and size_value > 50:
                continue
            elif size == 'Medium (51-100)' and (size_value < 51 or size_value > 100):
                continue
            elif size == 'Large (101+)' and size_value < 101:
                continue

        filtered.append(obj)

    return filtered

# ===== Apply Button Logic =====
def apply_delete(ui):
    base_objs = [obj for obj, btn in ui.object_buttons.items() if btn.isChecked()]
    name = ui.name_lineEdit.text()
    try:
        num_range = (int(ui.num_start.text()), int(ui.num_end.text()))
    except:
        num_range = None
    color = ui.color_combo.currentText()
    size = ui.size_combo.currentText()
    obj_type = ui.type_combo.currentText()

    to_delete = get_objects_by_filters(name=name, num_range=num_range, color=color, size=size, obj_type=obj_type, base_objs=base_objs)
    if to_delete:
        cmds.delete(to_delete)
        cmds.warning(f"Deleted objects: {to_delete}")
    else:
        cmds.warning("No objects matched the filter.")

# ===== Run UI =====
def run():
    global ui
    try:
        ui.close()
    except:
        pass
    ptr = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
    ui = ObjectDeleteUIDialog(parent=ptr)
    ui.show()
    ui.apply_button.clicked.connect(lambda: apply_delete(ui))
    ui.cancel_button.clicked.connect(ui.close)
