from datetime import datetime

from Homework import homework


class HWdatabase:
    def __init__(self):
        self.database = []

    def add(self, hw: homework):
        self.database.append(hw)

    def delete(self, hw: homework):
        self.database.remove(hw)

    def delete_by_num(self, n: int):
        for h in self.database:
            if h.num == n:
                self.delete(h)
                return True
        return False

    def read(self, filename: str):
        try:
            with open(filename, 'r') as f:
                hw_all_str = f.readlines()
            for line in hw_all_str:
                hw = homework(int(line[:2]), homework.make_deadline(str.strip(line[2:len(line)-3])), bool(int(line[len(line)-2])))
                self.add(hw)
        except:
            pass

    def get_database(self):
        all = []
        for h in self.database:
            all.append(str(h.num))
        return all

    def get_active(self):
        active = []
        for h in self.database:
            if h.is_active:
                active.append(str(h.num))
        return active

    def print(self):
        for i in self.database:
            i.print()

    def get_by_num(self, n):
        for h in self.database:
            if h.num == n:
                return h
        return False

    def save(self, filename: str):
        all = ''
        for h in self.database:
            all += h.get_str() + '\n'
        with open(filename, 'w') as f:
            f.write(all)

    def deactivate_past(self):
        for h in self.database:
            if datetime.now() > h.deadline:
                h.is_active = False
                temp = h
                self.delete(h)
                self.add(temp)

    def delete_all(self):
        self.database = []