import SpreadsheetsWorker
import os.path
from Homework import homework
from Delay import *

class PostponementsDatabase:
    def __init__(self):
        self.postponements = []
        self.postponementsCount = []

        if os.path.exists("postponements.txt"):
            self.readPostponements("postponements.txt")
        if os.path.exists("postponementsCount.txt"):
            self.readPostponementsCount("postponementsCount.txt")

    def add(self, postponement: delay):
        VkSrc = 'https://vk.com/id' + str(postponement.id)

        self.postponements.append([
            postponement.time,
            postponement.fullname[0] + ' ' + postponement.fullname[1],
            VkSrc,
            'ДЗ ' + str(postponement.hw.num),
            postponement.hw.deadline.strftime('%d.%m.%Y %H:%M:%S')
        ])

        added = False
        for i in range(len(self.postponementsCount)):
            if VkSrc == self.postponementsCount[i][1]:
                self.postponementsCount[i][2] += 1
                added = True

        if not added:
            self.postponementsCount.append([
                postponement.fullname[0] + ' ' + postponement.fullname[1],
                VkSrc,
                1
            ])

        self.save()

    def readPostponements(self, filename: str):
        with open(filename, 'r') as f:
            hw_all_str = f.readlines()
        for line in hw_all_str:
            temp = line.split()
            self.postponements.append([temp[0] + ' ' + temp[1], temp[2] + ' ' + temp[3], temp[4], temp[5] + ' ' + temp[6], temp[7] + ' ' + temp[8]])

    def readPostponementsCount(self, filename: str):
        with open(filename, 'r') as f:
            hw_all_str = f.readlines()
        for line in hw_all_str:
            temp = line.split()
            self.postponementsCount.append([temp[0] + ' ' + temp[1], temp[2], int(temp[3])])

    def get_postponements(self):
        all = []
        for p in self.postponements:
            all.append(p)
        return all

    def clear_postponements(self):
        self.postponements = []
        self.save()

    def get_postponements_count(self):
        all = []
        for p in self.postponementsCount:
            all.append(p)
        return all

    def check_postponements_count(self, user_id, maxPostponements):
        VkSrc = 'https://vk.com/id' + str(user_id)
        for p in self.postponementsCount:
            if p[1] == VkSrc:
                if p[2] < maxPostponements:
                    return True
                else:
                    return False
        return True

    def save(self):
        all = ''
        for p in self.postponements:
            all += str(p[0]) + ' ' + str(p[1]) + ' ' + str(p[2]) + ' ' + str(p[3]) + ' ' + str(p[4]) + '\n'
        with open('postponements.txt', 'w') as f:
            f.write(all)

        all = ''
        for p in self.postponementsCount:
            all += str(p[0]) + ' ' + str(p[1]) + ' ' + str(p[2]) + '\n'
        with open('postponementsCount.txt', 'w') as f:
            f.write(all)