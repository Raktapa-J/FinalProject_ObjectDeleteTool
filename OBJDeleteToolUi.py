try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from shiboken6 import wrapInstance
except:
    from PySide2 import QtCore, QtGui, QtWidgets
    from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import os
import math

ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'icons'))

def rgb_to_hex(rgb_tuple):
    r = int(max(0, min(1, rgb_tuple[0])) * 255)
    g = int(max(0, min(1, rgb_tuple[1])) * 255)
    b = int(max(0, min(1, rgb_tuple[2])) * 255)
    return (r << 16) + (g << 8) + b

def get_materials_of_shape(shape):
    mats = set()
    try:
        sgs = cmds.listConnections(shape, type='shadingEngine') or []
        for sg in sgs:
            mats_conn = cmds.listConnections(sg + ".surfaceShader") or []
            for m in mats_conn:
                mats.add(m)
    except:
        pass
    return list(mats)

def get_base_color_from_material(mat):
    if not mat:
        return None
    attrs = ['color', 'outColor', 'diffuse', 'baseColor', 'Kd', 'colorGain']
    for a in attrs:
        attr = f"{mat}.{a}"
        try:
            if cmds.objExists(attr):
                val = cmds.getAttr(attr)
                if isinstance(val, (list, tuple)):
                    if len(val) == 1 and isinstance(val[0], (list, tuple)):
                        v = val[0]
                    else:
                        v = val
                    if len(v) >= 3:
                        return (float(v[0]), float(v[1]), float(v[2]))
                elif isinstance(val, (float, int)):
                    f = float(val)
                    return (f, f, f)
        except:
            continue
    try:
        conns = cmds.listConnections(mat, s=True, d=False) or []
        for c in conns:
            for a in ['color', 'outColor']:
                if cmds.objExists(f"{c}.{a}"):
                    try:
                        val = cmds.getAttr(f"{c}.{a}")
                        if isinstance(val, (list, tuple)):
                            v = val[0] if len(val) == 1 else val
                            if len(v) >= 3:
                                return (float(v[0]), float(v[1]), float(v[2]))
                    except:
                        pass
    except:
        pass
    return None

def get_shape_world_bbox_diag(transform):
    try:
        bb = cmds.exactWorldBoundingBox(transform)
        dx = bb[3] - bb[0]
        dy = bb[4] - bb[1]
        dz = bb[5] - bb[2]
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    except:
        return 0.0

def object_is_type(transform, wanted_type):
    shapes = cmds.listRelatives(transform, shapes=True, fullPath=True) or []
    for s in shapes:
        t = cmds.nodeType(s)
        if wanted_type == 'Geometry' and t == 'mesh':
            return True
        if wanted_type == 'NURBS' and t in ('nurbsSurface', 'nurbsCurve'):
            return True
        if wanted_type == 'Curve' and t == 'nurbsCurve':
            return True
        if wanted_type == 'Light' and t.lower().endswith('light'):
            return True
    return False

COLOR_RANGES = {
    'Red':    [(0x800000, 0xFF3333)],
    'Orange': [(0xFF7F00, 0xFFB266)],
    'Yellow': [(0xFFFF00, 0xFFFF99)],
    'Green':  [(0x00AA00, 0x99FF99)],
    'Cyan':   [(0x00CED1, 0x99FFFF)],
    'Blue':   [(0x0000AA, 0x6666FF)],
    'Purple': [(0x800080, 0xC080FF)],
    'Pink':   [(0xFF66AA, 0xFFC0CB)],
    'Brown':  [(0x5A3100, 0xA0522D)],
    'White':  [(0xE6E6E6, 0xFFFFFF)],
    'Black':  [(0x000000, 0x1A1A1A)],
}

def color_hex_in_ranges(hexint, ranges):
    for (lo, hi) in ranges:
        if lo <= hexint <= hi:
            return True
    return False

class ObjectDeleteDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(420, 580)
        self.setWindowTitle('Object Delete Tool')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.setStyleSheet('''
            QDialog { background-color: #34B6BA; font-family: Tahoma; }
            QLabel { color: #FFFFFF; font-weight: bold; font-size: 14px; }
            QLabel#TitleLabel { font-size: 28px; font-family: Impact; }
            QLineEdit, QComboBox { background-color: #FFFFFF; color: black; border-radius: 8px; font-size: 14px; padding:4px; }
            QPushButton { background-color: #FFFFFF; color: #34B6BA; border-radius: 10px; font-weight: bold; font-size: 14px; padding:6px; }
            QPushButton:hover { background-color: #009696; color: #FFFFFF; }
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
            btn.setMinimumHeight(44)
            if os.path.exists(icon_path):
                btn.setIcon(QtGui.QIcon(icon_path))
                btn.setIconSize(QtCore.QSize(28, 28))
            btn.setText(obj.capitalize())
            self.icon_grid.addWidget(btn, row, col)
            self.object_buttons[obj] = btn

            btn.toggled.connect(lambda checked, b=btn: self.on_button_toggled(b, checked))
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
        self.num_start.setPlaceholderText('start')
        self.num_end.setPlaceholderText('end')
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
        self.color_combo.addItems(['All'] + list(COLOR_RANGES.keys()))
        self.color_layout.addWidget(self.color_label)
        self.color_layout.addWidget(self.color_combo)
        self.main_layout.addLayout(self.color_layout)

        self.size_layout = QtWidgets.QHBoxLayout()
        self.size_label = QtWidgets.QLabel('Size:')
        self.size_combo = QtWidgets.QComboBox()
        self.size_combo.addItems(['All', 'Small (<5)', 'Medium (5-20)', 'Large (>20)'])
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

        self.options_layout = QtWidgets.QHBoxLayout()
        self.preview_button = QtWidgets.QPushButton('Preview Matches')
        self.invert_check = QtWidgets.QCheckBox('Invert Selection')
        self.options_layout.addWidget(self.preview_button)
        self.options_layout.addWidget(self.invert_check)
        self.main_layout.addLayout(self.options_layout)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.apply_button = QtWidgets.QPushButton('Delete')
        self.cancel_button = QtWidgets.QPushButton('Cancel')
        self.button_layout.addWidget(self.apply_button)
        self.button_layout.addWidget(self.cancel_button)
        self.main_layout.addLayout(self.button_layout)

        self.main_layout.addStretch()

        self.apply_button.clicked.connect(self.on_apply)
        self.cancel_button.clicked.connect(self.close)
        self.preview_button.clicked.connect(self.on_preview)


    def on_button_toggled(self, button, checked):

        if checked:
            button.setStyleSheet("background-color: #018A8F; color: white; border-radius: 10px; font-weight: bold;")
        else:
            button.setStyleSheet("background-color: #FFFFFF; color: #34B6BA; border-radius: 10px; font-weight: bold;")

    def get_selected_base_types(self):

        return [name for name, btn in self.object_buttons.items() if btn.isChecked()]

    def build_candidates(self):
        sel_bases = self.get_selected_base_types()


        if not sel_bases:
            return []

        base_name = (self.name_lineEdit.text() or "").strip()
        start_txt = self.num_start.text().strip()
        end_txt = self.num_end.text().strip()
        candidates = []

        all_transforms = cmds.ls(type='transform', long=False) or []

        if base_name and start_txt and end_txt:
            try:
                s = int(start_txt)
                e = int(end_txt)
                for i in range(s, e + 1):
                    name = f"{base_name}{i}"
                    if cmds.objExists(name):
                      
                        for base in sel_bases:
                            if base.lower() in name.lower():
                                candidates.append(name)
                                break
            except:
                pass


            for obj in all_transforms:
                for base in sel_bases:
                    if base.lower() in obj.lower():
                        candidates.append(obj)
                        break

        if not candidates:
            return []


        return list(dict.fromkeys(candidates))


    def filter_by_color(self, candidates, color_name):
        if not color_name or color_name == 'All':
            return candidates
        ranges = COLOR_RANGES.get(color_name, None)
        if not ranges:
            return candidates
        matched = []
        for obj in candidates:
            shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
            matched_flag = False
            for s in shapes:
                mats = get_materials_of_shape(s)
                for mat in mats:
                    rgb = get_base_color_from_material(mat)
                    if rgb:
                        hexint = rgb_to_hex(rgb)
                        if color_hex_in_ranges(hexint, ranges):
                            matched_flag = True
                            break
                if matched_flag:
                    break
            if matched_flag:
                matched.append(obj)
        return matched

    def filter_by_size(self, candidates, size_text):
        if not size_text or size_text == 'All':
            return candidates
        matched = []
        for obj in candidates:
            diag = get_shape_world_bbox_diag(obj)
            if size_text.startswith('Small') and diag < 5.0:
                matched.append(obj)
            elif size_text.startswith('Medium') and 5.0 <= diag <= 20.0:
                matched.append(obj)
            elif size_text.startswith('Large') and diag > 20.0:
                matched.append(obj)
        return matched

    def filter_by_type(self, candidates, type_text):
        if not type_text or type_text == 'All':
            return candidates
        matched = []
        for obj in candidates:
            if object_is_type(obj, type_text):
                matched.append(obj)
        return matched

    def apply_all_filters(self):
        candidates = self.build_candidates()
        color_sel = self.color_combo.currentText()
        candidates = self.filter_by_color(candidates, color_sel)
        size_sel = self.size_combo.currentText()
        candidates = self.filter_by_size(candidates, size_sel)
        type_sel = self.type_combo.currentText()
        candidates = self.filter_by_type(candidates, type_sel)
        if self.invert_check.isChecked():
            all_transforms = cmds.ls(type='transform') or []
            inverted = [t for t in all_transforms if t not in candidates and cmds.objExists(t)]
            candidates = inverted
        return candidates

    def on_preview(self):
        matches = self.apply_all_filters()
        if not matches:
            QtWidgets.QMessageBox.information(self, "Preview", "No matching objects found.")
            return
        cmds.select(matches, replace=True)
        QtWidgets.QMessageBox.information(self, "Preview", f"{len(matches)} objects selected (preview).")

    def on_apply(self):
        matches = self.apply_all_filters()
        if not matches:
            QtWidgets.QMessageBox.information(self, "Delete", "No matching objects to delete.")
            return
        preview_list = "\n".join(matches[:50])
        more = "" if len(matches) <= 50 else f"\n... and {len(matches)-50} more"
        msg = f"Delete {len(matches)} objects?\n\n{preview_list}{more}\n\nThis action cannot be undone."
        res = QtWidgets.QMessageBox.question(self, "Confirm Delete", msg, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if res != QtWidgets.QMessageBox.Yes:
            return
        deleted = []
        failed = []
        for o in matches:
            try:
                if cmds.objExists(o):
                    cmds.delete(o)
                    deleted.append(o)
            except Exception as e:
                failed.append((o, str(e)))
        if deleted:
            cmds.inViewMessage(amg=f"<hl>Deleted {len(deleted)} objects</hl>", pos='midCenter', fade=True)
        if failed:
            QtWidgets.QMessageBox.warning(self, "Delete", f"Failed to delete {len(failed)} objects (see script editor).")
            for f in failed:
                print("Failed:", f)
        try:
            cmds.select(clear=True)
        except:
            pass


def run():
    global ui
    try:
        ui.close()
    except:
        pass
    ptr = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
    ui = ObjectDeleteDialog(parent=ptr)
    ui.show()

