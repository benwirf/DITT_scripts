class AreaCalculationsWidget(QWidget):
    def __init__(self):
        super(AreaCalculationsWidget, self).__init__()
        self.param_lbl = QLabel('Calculate area columns:', self)
        self.param_lbl.setMinimumWidth(175)
        self.param_lbl.setMinimumHeight(30)
        self.area_m2_chk = QCheckBox('Area m2', self)
        self.area_ha_chk = QCheckBox('Area Ha', self)
        self.area_km2_chk = QCheckBox('Area km2', self)
        self.ellipsoidal_rb = QRadioButton('Ellipsoidal', self)
        self.ellipsoidal_rb.setChecked(True)
        self.ellipsoidal_rb.setEnabled(False)
        self.planimetric_rb = QRadioButton('Planimetric', self)
        self.planimetric_rb.setEnabled(False)
        self.method_lbl = QLabel('Area calculation method:', self)
        self.method_lbl.setMinimumWidth(175)
        self.method_lbl.setMinimumHeight(30)
        self.parent_layout = QVBoxLayout(self)
        self.cb_layout = QHBoxLayout(self)
        self.cb_layout.addWidget(self.area_m2_chk)
        self.cb_layout.addWidget(self.area_ha_chk)
        self.cb_layout.addWidget(self.area_km2_chk)
        self.parent_layout.addWidget(self.param_lbl)
        self.rb_layout = QHBoxLayout(self)
        self.rb_layout.addWidget(self.ellipsoidal_rb)
        self.rb_layout.addWidget(self.planimetric_rb)
        self.parent_layout.addLayout(self.cb_layout)
        self.parent_layout.addWidget(self.method_lbl)
        self.parent_layout.addLayout(self.rb_layout)
        
        self.checkboxes = [self.area_m2_chk,
                            self.area_ha_chk,
                            self.area_km2_chk]
                            
        self.radiobuttons = [self.ellipsoidal_rb,
                            self.planimetric_rb]
        
        for cb in self.checkboxes:
                cb.stateChanged.connect(self.manageRadioButtons)
        
    def manageRadioButtons(self):
        if self.area_m2_chk.checkState() == Qt.Checked or self.area_ha_chk.checkState() == Qt.Checked or self.area_km2_chk.checkState() == Qt.Checked:
            self.ellipsoidal_rb.setEnabled(True)
            self.planimetric_rb.setEnabled(True)
        else:
            self.ellipsoidal_rb.setEnabled(False)
            self.planimetric_rb.setEnabled(False)
            
    def getAreaColumns(self):
        return [chk_box.text() for chk_box in self.checkboxes if chk_box.checkState() == Qt.Checked]
        
    def getAreaMethod(self):
        return [rad_btn.text() for rad_btn in self.radiobuttons if rad_btn.isChecked()]
        
w = AreaCalculationsWidget()
w.show()
#print(w.getAreaColumns())
#print(w.getAreaMethod())
        