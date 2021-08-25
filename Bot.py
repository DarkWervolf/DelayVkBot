from datetime import datetime
import os
from vk_api.utils import get_random_id
import vk_requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import time

import re
import enum

from Delay import *
from Homework import *
from HWDatabase import *
from Keyboards import *
from AdminDatabase import *
from SpreadsheetsWorker import *
from PostmestsDatabase import *

class states(enum.Enum):
    ask_postponement = 1
    choose_hw_num = 2
    ask_yes_no = 3
    admin = 4
    add_hw = 5
    delete_hw = 6
    change_hw = 7
    change_hw_finally = 8
    admin_add = 9
    admin_delete = 10


class Bot:
    def __init__(self, token, maxPost):
        self.token = token
        self.vk_session = vk_api.VkApi(token=token)
        # self.Lslongpoll = VkLongPoll(vk_session)
        # self.Lsvk = vk_session.get_api()
        self.api_requests = vk_requests.create_api(service_token=token)

        self.keyboard_default = keyboard_default()
        self.keyboard_delay = keyboard_delay()
        self.keyboard_yesno = keyboard_yesno()
        self.keyboard_admin = keyboard_admin()
        self.keyboard_cancel = keyboard_cancel()

        # загрузка всех дз из файла
        self.database_hw = HWdatabase()
        self.hw_all = self.database_hw.get_database()
        self.hw_available = self.database_hw.get_active()
        self.hw_none = len(self.database_hw.database) == 0

        self.god_ids = [215762369, 137259946]
        self.database_admin = AdminDatabase()
        for god_id in self.god_ids:
            self.database_admin.admins_id.append(god_id)

        self.active_users = []
        self.postponement_database = PostponementsDatabase()
        self.maxPostp = maxPost
        self.last_spreadsheet_send = time.time()
        self.worker = SpreadsheetsWorker.SpreadsheetsWorker()

    def run(self):
        for event in VkLongPoll(self.vk_session).listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.from_user:
                text = event.text.lower()
                user_id = event.user_id

                user_index = -1
                inUsers = False
                for i in range(len(self.active_users)):
                    if (self.active_users[i][0] == user_id):
                        inUsers = True
                        user_index = i
                if not inUsers:
                    self.active_users.append([user_id, states.ask_postponement, -1])
                    user_index = len(self.active_users) - 1

                self.database_hw.deactivate_past()
                self.hw_available = self.database_hw.get_active()
                self.hw_none = len(self.hw_available) == 0

                if text == 'админ' and user_id in self.database_admin.get_database():
                    self.active_users[user_index][1] = states.admin
                    self.active_users[user_index][2] = -1
                    self.send_message(user_id, 'Панель управления ботом открыта.', self.keyboard_admin)

                elif text == 'добавить' and user_id in self.database_admin.get_database() and \
                        self.active_users[user_index][
                            1] == states.admin:
                    self.active_users[user_index][1] = states.add_hw
                    self.send_message(user_id, 'Введите номер и дату дедлайна дз в формате:\nнн дд.мм.гг а\nГде нн - '
                                               'номер дз,\nдд.мм.гг - дата дедлайна (время выставляется автоматически)'
                                               ',\nа - активно дз или нет (0 или 1).',
                                      self.keyboard_cancel)

                elif re.match("^\d+\s\d{2}\.\d{2}\.\d{4}\s\d$", text) \
                        and user_id in self.database_admin.get_database() and self.active_users[user_index][
                    1] == states.add_hw:
                    self.active_users[user_index][1] = states.admin
                    line = str.strip(text)
                    temp = line.split()
                    hw = homework(int(temp[0]), temp[1], bool(temp[2]))
                    self.database_hw.add(hw)
                    f = open("hw_" + str(hw.num) + ".txt", 'a')
                    f.close()
                    self.send_message(user_id, 'Успех!', self.keyboard_admin)

                elif text == 'удалить' and user_id in self.database_admin.get_database() and \
                        self.active_users[user_index][
                            1] == states.admin:
                    self.active_users[user_index][1] = states.delete_hw
                    self.send_message(user_id, 'Введите номер дз в формате: нн\nИли слово "все", чтобы удалить все.',
                                      self.keyboard_cancel)

                elif re.match("^\d+$", text) \
                        and user_id in self.database_admin.get_database() and self.active_users[user_index][
                    1] == states.delete_hw:
                    self.active_users[user_index][1] = states.admin
                    num = str.strip(text)
                    if self.database_hw.delete_by_num(int(num)):
                        filename = "hw_" + str(int(num)) + ".txt"
                        if os.path.exists(filename):
                            os.remove(filename)
                        self.send_message(user_id, 'Успех!', self.keyboard_admin)
                    else:
                        self.send_message(user_id, 'Дз с таким номером не найдено.', self.keyboard_admin)

                elif text == 'все' \
                        and user_id in self.database_admin.get_database() and self.active_users[user_index][
                    1] == states.delete_hw:
                    self.active_users[user_index][1] = states.admin
                    self.database_hw.delete_all()
                    self.send_message(user_id, 'Успех!', self.keyboard_admin)

                elif text == 'изменить' \
                        and user_id in self.database_admin.get_database() and self.active_users[user_index][
                    1] == states.admin:
                    self.active_users[user_index][1] = states.change_hw
                    self.send_message(user_id, 'Введите номер дз в формате: нн', self.keyboard_cancel)

                elif re.match("^\d+$", text) \
                        and user_id in self.database_admin.get_database() and self.active_users[user_index][
                    1] == states.change_hw:
                    num = str.strip(text)
                    hwork = self.database_hw.get_by_num(int(num))
                    if hwork:
                        self.active_users[user_index][1] = states.change_hw_finally
                        self.active_users[user_index][2] = int(num)
                        self.send_message(user_id, 'Введите номер и дату дедлайна дз в формате:\nнн дд.мм.гг а\nГде нн - '
                                               'номер дз,\nдд.мм.гг - дата дедлайна (время выставляется автоматически)'
                                               ',\nа - активно дз или нет (0 или 1).',
                                               self.keyboard_cancel)
                    else:
                        self.active_users[user_index][1] = states.change_hw
                        self.send_message(user_id, 'Дз с таким номером не существет. Введите другое значение.',
                                          self.keyboard_cancel)

                elif re.match("^\d+\s\d{2}\.\d{2}\.\d{4}\s\d$", text) \
                        and user_id in self.database_admin.get_database() and self.active_users[user_index][
                    1] == states.change_hw_finally:
                    self.active_users[user_index][1] = states.admin
                    self.database_hw.delete_by_num(self.active_users[user_index][2])
                    line = str.strip(text)
                    temp = line.split()
                    hw = homework(int(temp[0]), temp[1], bool(int(temp[2])))
                    self.database_hw.add(hw)
                    f = open("hw_" + str(hw.num) + ".txt", 'a')
                    f.close()
                    self.send_message(user_id, 'Успех!', self.keyboard_admin)

                elif text == 'показать активные' \
                        and user_id in self.database_admin.get_database() and self.active_users[user_index][
                    1] == states.admin:
                    active = ''
                    for h in self.database_hw.database:
                        if h.is_active:
                            active += h.get_str() + '\n'
                    if active == '':
                        self.send_message(user_id, 'Пусто!')
                    else:
                        self.send_message(user_id, active)

                elif text == 'показать все' \
                        and user_id in self.database_admin.get_database() and self.active_users[user_index][
                    1] == states.admin:
                    all_hw = ''
                    for h in self.database_hw.database:
                        all_hw += h.get_str() + '\n'
                    if all_hw == '':
                        self.send_message(user_id, 'Пусто!')
                    else:
                        self.send_message(user_id, all_hw)

                elif text == 'добавить админа' \
                        and user_id in self.database_admin.get_database() and self.active_users[user_index][
                    1] == states.admin:
                        self.active_users[user_index][1] = states.admin_add
                        self.send_message(user_id, 'Введите id нового админа в формате цифр', self.keyboard_cancel)

                elif re.match("^\d+$", text) \
                        and user_id in self.database_admin.get_database() and self.active_users[user_index][
                    1] == states.admin_add:
                        self.active_users[user_index][1] = states.admin
                        self.database_admin.add(int(str.strip(text)))
                        self.send_message(user_id, 'Успех!', self.keyboard_admin)

                elif text == 'удалить админа' \
                        and user_id in self.database_admin.get_database() and self.active_users[user_index][
                    1] == states.admin:
                        self.active_users[user_index][1] = states.admin_delete
                        self.send_message(user_id, 'Введите id админа в формате цифр', self.keyboard_cancel)

                elif re.match("^\d+$", text) \
                        and user_id in self.database_admin.get_database() and self.active_users[user_index][
                    1] == states.admin_delete:
                        self.active_users[user_index][1] = states.admin
                        if int(str.strip(text)) in self.god_ids:
                            self.send_message(user_id, 'Этот человек очень важен для нас, мы не можем его удалить', self.keyboard_admin)
                        elif int(str.strip(text)) == user_id:
                            self.send_message(user_id, 'Нельзя удалить самого себя.\nОперация отменена.',
                                              self.keyboard_admin)
                        else:
                            self.database_admin.delete(int(str.strip(text)))
                            self.send_message(user_id, 'Успех!', self.keyboard_admin)

                elif text == 'показать админов' \
                        and user_id in self.database_admin.get_database() and self.active_users[user_index][
                    1] == states.admin:
                        admins_all = 'Текущие админы:\n'
                        for a in self.database_admin.get_database():
                            user = self.api_requests.users.get(user_ids=a)
                            user_name = [user[0].get('first_name'), user[0].get('last_name')]
                            admins_all += user_name[0] + " " + user_name[1] + " " + str(a) + "\n"
                        self.send_message(user_id, admins_all, self.keyboard_admin)


                elif text == 'отмена' and user_id in self.database_admin.get_database() and \
                        (self.active_users[user_index][1] == states.add_hw
                         or self.active_users[user_index][1] == states.delete_hw
                         or self.active_users[user_index][1] == states.change_hw
                         or self.active_users[user_index][1] == states.change_hw_finally
                         or self.active_users[user_index][1] == states.admin_add
                         or self.active_users[user_index][1] == states.admin_delete):
                    self.active_users[user_index][1] = states.admin
                    self.active_users[user_index][2] = -1
                    self.send_message(user_id, 'Операция отменена.', self.keyboard_admin)

                elif text == 'справка':
                    self.send_message(user_id,
                                      'Отсрочка - это персональный сдвиг дедлайна на 5 дней без изменения времени.'
                                      '\nВсего на курс у вас есть ' + str(self.maxPostp) + ' отсрочек.'
                                                                                           '\nПопросить отсрочку можно в данном боте, внимательно следуя инструкциям'
                                                                                           '.\nНе советуем играть с ботом - он может и мизинец отхватить.\nПо всем '
                                                                                           'техническим вопросам, касающихся бота, можете писать в учебную беседу курса')

                elif text == 'завершить' and (self.active_users[user_index][1] == states.choose_hw_num or
                                              self.active_users[user_index][1] == states.ask_yes_no):
                    self.active_users[user_index][1] = states.ask_postponement
                    self.active_users[user_index][2] = -1
                    self.send_message(user_id, 'Рад был помочь!', self.keyboard_delay)

                elif re.match("^\d+$", text) and self.active_users[user_index][1] == states.choose_hw_num:
                    if not (text in self.hw_all):
                        self.send_message(user_id, 'Дз с таким номером не найдено.')
                    elif not (text in self.hw_available):
                        self.send_message(user_id, 'Это дз недоступно для отсрочки.')
                    elif not (text in self._get_available_hwrks_(user_id)):
                        self.send_message(user_id, 'Вы уже взяли отсрочку на это дз.')
                    else:
                        self.active_users[user_index][1] = states.ask_yes_no
                        self.active_users[user_index][2] = int(text)
                        self.send_message(user_id, 'Ты уверен, что хочешь попросить отсрочку? Назад пути не будет!',
                                          self.keyboard_yesno)

                elif text == 'да' and (self.active_users[user_index][1] == states.ask_yes_no):
                    # делаем запрос, чтобы получить фио человека
                    user = self.api_requests.users.get(user_ids=event.user_id)
                    user_name = [user[0].get('first_name'), user[0].get('last_name')]
                    # Добавление в файл
                    self._add_id_to_file_(user_id, self.active_users[user_index][2])

                    self.postponement_database.add(delay(user_id, user_name,
                                                         self.database_hw.get_by_num(self.active_users[user_index][2])))

                    self.active_users[user_index][1] = states.ask_postponement
                    self.active_users[user_index][2] = -1
                    self.send_message(user_id, 'Отсрочка выдана!', self.keyboard_delay)

                elif text == 'нет' and (self.active_users[user_index][1] == states.ask_yes_no):
                    self.active_users[user_index][1] = states.ask_postponement
                    self.active_users[user_index][2] = -1
                    self.send_message(user_id, 'Операция отменена, мизинец спасён.', self.keyboard_delay)

                elif text == 'попросить отсрочку' and self.active_users[user_index][
                    1] == states.ask_postponement:
                    if self.hw_none:
                        self.send_message(user_id, 'Сейчас нет доступных отсрочек.')

                    elif len(self._get_available_hwrks_(user_id)) == 0:
                        self.send_message(user_id, 'Сейчас нет доступных отсрочек для вас.')

                    elif self.postponement_database.check_postponements_count(user_id, self.maxPostp):
                        self.active_users[user_index][1] = states.choose_hw_num
                        nums = self._get_available_hwrks_(user_id)

                        # клавиатура с доступными дз + стандартными
                        keyboard_hw_available = VkKeyboard(one_time=False)
                        already_added_cnt = 0
                        for i in range(len(nums)):
                            if nums[i] in self.hw_available:
                                if already_added_cnt % 5 == 0 and already_added_cnt > 0:
                                    keyboard_hw_available.add_line()
                                keyboard_hw_available.add_button(nums[i], color=VkKeyboardColor.PRIMARY)
                                already_added_cnt += 1

                        keyboard_hw_available.add_line()
                        keyboard_hw_available.add_button('Справка')
                        keyboard_hw_available.add_button('Завершить')

                        self.send_message(user_id, 'Выбери номер домашней работы.',
                                          keyboard_hw_available)

                    else:
                        self.send_message(user_id, 'Вы истратили все свои отсрочки.')

                else:
                    self.active_users[user_index][1] = states.ask_postponement
                    self.active_users[user_index][2] = -1
                    self.send_message(user_id, 'Привет!\nЭто бот для получения отсрочек по информатике в Школково.\n'
                                               'Чтобы попросить отсрочку, нажми на кнопку ниже.',
                                      self.keyboard_delay)

                if time.time() - self.last_spreadsheet_send >= 30:
                    print('start sending')
                    postponements = self.postponement_database.get_postponements()
                    postponementsCount = self.postponement_database.get_postponements_count()
                    self.worker.send_postponement_to_experts(postponements)
                    self.worker.send_postponement_count(postponementsCount)
                    self.postponement_database.clear_postponements()
                    self.last_spreadsheet_send = time.time()
                    print('end sending')



    def send_message(self, user_id, message, keyboard=None):
        post = {
            "user_id": user_id,
            "message": message,
            "random_id": get_random_id()
        }

        if keyboard != None:
            post["keyboard"] = keyboard.get_keyboard()

        self.vk_session.method("messages.send", post)

    def _add_id_to_file_(self, user_id: int, homework_num: int):
        filename = "hw_" + str(homework_num) + ".txt"
        with open(filename, 'a') as file:
            file.write(str(user_id) + '\n')

    def _get_available_hwrks_(self, user_id):
        if not self.hw_none:
            hwrks = []
            for a in self.hw_available:
                filename = "hw_" + str(a) + ".txt"
                if not os.path.exists(filename):
                    with open(filename, 'w') as file:
                        a = 0
                with open(filename, 'r') as file:
                    lines = file.read().splitlines()
                    if not (str(user_id) in lines):
                        hwrks.append(a)
            return hwrks
        return []

    @staticmethod
    def str_trim(s: str):
        return str.lower(str.strip(s))