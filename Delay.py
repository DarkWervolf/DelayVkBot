from Homework import homework
import datetime

class delay:

    id = None
    hw = None
    fullname = None
    time = None

    def __init__(self, id: int, fullname: list, hw: homework):
        self.id = id
        self.fullname = fullname
        self.hw = hw
        self.time = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')