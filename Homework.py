from datetime import datetime

class homework:
    def __init__(self, num: int, deadline: datetime, is_active: bool):
        self.num = num
        self.deadline = deadline
        self.is_active = is_active

    def print(self):
        print(str(self.num) + " " + str(self.deadline) + " " + str(self.is_active))

    def get_str(self):
        return str(self.num) + " " + str(self.deadline.strftime('%d.%m.%y')) + " " + str(int(self.is_active))

    @staticmethod
    def make_deadline(date: str):
        date += ' 23:00:00'
        deadline = datetime.strptime(date, '%d.%m.%y %H:%M:%S')
        return deadline
