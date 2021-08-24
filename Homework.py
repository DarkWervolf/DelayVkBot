from datetime import datetime

class homework:
    def __init__(self, num: int, date: str, is_active: bool):
        self.num = num
        self.deadline = self.make_deadline(date)
        self.is_active = is_active

    def print(self):
        print(str(self.num) + " " + str(self.deadline) + " " + str(self.is_active))

    def get_str(self):
        return str(self.num) + " " + str(self.deadline.strftime('%d.%m.%Y')) + " " + str(int(self.is_active))

    def make_deadline(self, date: str):
        date += ' 23:00:00'
        deadline = datetime.strptime(date, '%d.%m.%Y %H:%M:%S')
        return deadline
