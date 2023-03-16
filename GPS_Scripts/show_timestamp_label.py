canvas = iface.mapCanvas()
lbl = QLabel(iface.mainWindow())
lbl.setGeometry(1200, 870, 250, 30)
lbl.setAlignment(Qt.AlignCenter)
lbl.setStyleSheet("QLabel"
                 "{"
                 "border : 4px solid grey;"
                 "background : white;"
                 "}")

def get_time():
    range = canvas.temporalRange()
    time_string = range.begin().toString()
    return time_string
    
def set_time():
    lbl.setText(get_time())

lbl.setText(get_time())
lbl.show()

canvas.temporalRangeChanged.connect(set_time)

#lbl.hide()
#canvas.temporalRangeChanged.disconnect(set_time)