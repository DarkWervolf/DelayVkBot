from datetime import datetime
import os.path
from Homework import homework


class HWdatabase:
    def __init__(self):
        self.database = []
        if os.path.exists("hw_all.txt"):
            self.read("hw_all.txt")
            self.deactivate_past()

    def add(self, hw: homework):
        self.database.append(hw)
        self.database.sort(key=self.custom_key)
        self.save("hw_all.txt")

    @staticmethod
    def custom_key(hw: homework):
        return hw.num

    def delete(self, hw: homework):
        self.database.remove(hw)
        self.save("hw_all.txt")

    def delete_by_num(self, n: int):
        for h in self.database:
            if h.num == n:
                self.delete(h)
                filename = "hw_" + str(n) + ".txt"
                if os.path.exists(filename):
                    os.remove(filename)
                return True
        return False

    def read(self, filename: str):
        with open(filename, 'r') as f:
            hw_all_str = f.readlines()
        for line in hw_all_str:
            temp = line.split()
            hw = homework(int(temp[0]), str.strip(temp[1]), bool(int(temp[2])))
            self.database.append(hw)

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
        isChanged = False
        for i in range(0, len(self.database)):
            if datetime.now() > self.database[i].deadline:
                self.database[i].is_active = False
                isChanged = True
        if isChanged:
            self.save("hw_all.txt")
        '''for h in self.database:
            if datetime.now() > h.deadline:
                h.is_active = False
                temp = h
                self.delete(h)
                self.add(temp)'''

    def delete_all(self):
        while len(self.database) != 0:
            filename = "hw_" + str(self.database[0].num) + ".txt"
            if os.path.exists(filename):
                os.remove(filename)
            self.delete(self.database[0])