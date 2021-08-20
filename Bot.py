from datetime import datetime
import os
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_requests

import re

from Delay import *
from Homework import *
from HWDatabase import *
from Keyboards import *
from AdminDatabase import *


class Bot:
    def __init__(self, token, user):
        self.user = user

        self.token = token
        vk_session = vk_api.VkApi(token=token)
        self.Lslongpoll = VkLongPoll(vk_session)
        self.Lsvk = vk_session.get_api()
        self.api_requests = vk_requests.create_api(service_token=token)

        self.keyboard_default = keyboard_default()
        self.keyboard_delay = keyboard_delay()
        self.keyboard_yesno = keyboard_yesno()
        self.keyboard_admin = keyboard_admin()
        self.keyboard_cancel = keyboard_cancel()

        # загрузка всех дз из файла
        self.database_hw = HWdatabase()
        self.database_hw_filename = "hw_all.txt"
        self.database_hw.read(self.database_hw_filename)
        self.database_hw.deactivate_past()
        self.hw_all = self.database_hw.get_database()

        self.hw_available = self.database_hw.get_active()
        self.hw_none = len(self.database_hw.database) == 0

        self._get_available_hw_()
        self.hw_none = len(self.hw_available) == 0

        # клавиатура с доступными дз + стандартными
        self.keyboard_hw_available = VkKeyboard(one_time=False)
        if not self.hw_none:
            for i in range(len(self.hw_available)):
                self.keyboard_hw_available.add_button(self.hw_available[i], color=VkKeyboardColor.PRIMARY)
            self.keyboard_hw_available.add_line()

        self.keyboard_hw_available.add_button('Справка')
        self.keyboard_hw_available.add_button('Завершить')

        self.god_id = 215762369
        self.database_admin = AdminDatabase()
        self.database_admin_filename = "admins_id.txt"
        self.database_admin.load(self.database_admin_filename)
        self.database_admin.add(self.god_id)

    def run(self, start_event):
        if start_event.text == 'd27fh2fbskrbakq1r' and start_event.user_id in self.database_admin.get_database():
            self._listen_admin_(start_event)

        elif Bot.str_trim(start_event.text) == 'попросить отсрочку' and not self.hw_none:
            self._message_delay_()
            if self._listen_delay_() == 0:
                return

        elif self.hw_none:
            self._message_nodelays_()
            return

        else:
            self._message_start_()
        self._listen_main_()

    def _message_start_(self):
        self.Lsvk.messages.send(
            user_id=self.user,
            keyboard=self.keyboard_delay.get_keyboard(),
            message='Привет!\nЭто бот для получения отсрочек по информатике в Школково.\nЧтобы попросить отсрочку, нажми на кнопку ниже.',
            random_id=get_random_id()
        )

    def _message_delay_(self):
        self.Lsvk.messages.send(
            user_id=self.user,
            message='Выбери номер домашней работы.',
            keyboard=self.keyboard_hw_available.get_keyboard(),
            random_id=get_random_id()
        )

    def _message_help_(self):
        self.Lsvk.messages.send(
            user_id=self.user,
            message='Отсрочка - это персональный сдвиг дедлайна на 5 дней без изменения времени.\nВсего на курс у вас есть 10 отсрочек.\nПопросить отсрочку можно в данном боте, внимательно следуя инструкциям.\nНе советуем играть с ботом - он может и мизинец отхватить.\nПо всем техническим вопросам, касающихся бота, можете писать в учебную беседу курса',
            random_id=get_random_id()
        )

    def _message_success(self):
        self.Lsvk.messages.send(
            user_id=self.user,
            message='Успех!',
            keyboard=self.keyboard_admin.get_keyboard(),
            random_id=get_random_id()
        )

    def _message_cancel(self):
        self.Lsvk.messages.send(
            user_id=self.user,
            keyboard=self.keyboard_admin.get_keyboard(),
            message='Операция отменена',
            random_id=get_random_id()
        )

    def _message_end(self):
        self.Lsvk.messages.send(
            user_id=self.user,
            message='Рад был помочь!',
            random_id=get_random_id()
        )

    def _message_delaycancel_(self):
        self.Lsvk.messages.send(
            user_id=self.user,
            message='Операция отменена, мизинец спасён.',
            keyboard=self.keyboard_delay.get_keyboard(),
            random_id=get_random_id()
        )

    def _message_notfound_(self):
        self.Lsvk.messages.send(
            user_id=self.user,
            message='Домашнее задание с таким номером не найдено.',
            random_id=get_random_id()
        )

    def _message_nodelays_(self):
        self.Lsvk.messages.send(
            user_id=self.user,
            message='Сейчас нет доступных отсрочек.',
            random_id=get_random_id()
        )

    def _listen_main_(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.from_user and event.user_id == self.user:
                # admins panel
                if event.text == 'd27fh2fbskrbakq1r' and event.user_id in self.database_admin.get_database():
                    self._listen_admin_(event)
                    return

                # action for beginning
                if Bot.str_trim(event.text) == 'начать':
                    self._message_start_()

                # action for delay
                if Bot.str_trim(event.text) == 'попросить отсрочку':
                    if self.hw_none:
                        self._message_nodelays_()
                        return

                    self._message_delay_()
                    if self._listen_delay_() == 0:
                        return


                if Bot.str_trim(event.text) == 'завершить':
                    self._message_end()
                    return

    def _listen_delay_confirm_(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.from_user and event.user_id == self.user:
                if Bot.str_trim(event.text) == 'да':
                    return True
                elif Bot.str_trim(event.text) == 'нет':
                    return False

                elif Bot.str_trim(event.text) == "завершить":
                    return False
                elif Bot.str_trim(event.text) == "справка":
                    # сообщение будет отправлено из main
                    pass
                else:
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Некорректная команда. Попробуй ещё раз.',
                        keyboard=self.keyboard_yesno.get_keyboard(),
                        random_id=get_random_id()
                    )

    def _listen_delay_(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.from_user and event.user_id == self.user:
                if event.text in self.hw_all:
                    if event.text in self.hw_available:
                        self.Lsvk.messages.send(
                            user_id=event.user_id,
                            message='Ты уверен, что хочешь попросить отсрочку? Назад пути не будет!',
                            keyboard=self.keyboard_yesno.get_keyboard(),
                            random_id=get_random_id()
                        )
                        if self._listen_delay_confirm_():
                            # делаем запрос, чтобы получить фио человека
                            user = self.api_requests.users.get(user_ids=event.user_id)
                            user_name = [user[0].get('first_name'), user[0].get('last_name')]

                            if Bot.availability_check(event.user_id, user_name, int(Bot.str_trim(event.text))):
                                self._add_id_to_file_(int(Bot.str_trim(event.text)))
                                self.Lsvk.messages.send(
                                    user_id=event.user_id,
                                    message='Отсрочка выдана!',
                                    keyboard=self.keyboard_delay.get_keyboard(),
                                    random_id=get_random_id()
                                )
                                return 0
                        else:
                            self._message_delaycancel_()
                            return 0
                    else:
                        self.Lsvk.messages.send(
                            user_id=event.user_id,
                            message='Отсрочки на это дз уже недоступны. Введите другой номер.',
                            keyboard=self.keyboard_hw_available.get_keyboard(),
                            random_id=get_random_id()
                        )
                elif Bot.str_trim(event.text) == "завершить":
                    self._message_delaycancel_()
                    return 0
                elif re.match('\\s*\\d+\\s*', event.text):
                    self._message_notfound_()

    def _add_id_to_file_(self, homework_num: int):
        filename = "hw_" + str(homework_num) + ".txt"
        with open(filename, 'a') as file:
            file.write(str(self.user) + '\n')

    def _get_available_hw_(self):
        if not self.hw_none:
            to_remove = []
            for a in self.hw_available:
                filename = "hw_" + str(a) + ".txt"
                try:
                    with open(filename, 'r') as file:
                        lines = file.read().splitlines()
                        if str(self.user) in lines:
                            to_remove.append(a)
                except:
                    pass
            for i in range(len(to_remove)):
                self.hw_available.remove(to_remove[i])

    def _add_hw_(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.user_id == self.user:
                if re.match("\\s*\\d?\\d\\s[0-3]\\d\\.(0[1-9]|1[0-2])\\.\\d\\d\\s[0-1]\\s*", event.text):
                    line = str.strip(event.text)
                    print(line)
                    hw = homework(int(line[:2]), homework.make_deadline(str.strip(line[2:len(line) - 2])),
                                  bool(int(line[len(line) - 1])))
                    self.database_hw.add(hw)
                    f = open("hw_" + str(hw.num) + ".txt", 'a')
                    f.close()
                    self._message_success()
                    self.database_hw.save(self.database_hw_filename)
                    self.database_hw.deactivate_past()
                    return
                elif event.text == 'Отмена':
                    self._message_cancel()
                    return

    def _delete_hw_(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.user_id == self.user:
                if Bot.str_trim(event.text) == 'все':
                    #delete all files
                    for h in self.database_hw.get_database():
                        filename = "hw_ " + str(h) + ".txt"
                        if os.path.exists(filename):
                            os.remove(filename)
                    self.database_hw.delete_all()
                    self._message_success()
                    self.database_hw.save(self.database_hw_filename)
                    return

                elif re.match("\\s*\\d?\\d\\s*", event.text):
                    num = str.strip(event.text)
                    if self.database_hw.delete_by_num(int(num)):
                        #delete hw file
                        filename = "hw_ " + str(num) + ".txt"
                        if os.path.exists(filename):
                            os.remove(filename)
                        self._message_success()
                        self.database_hw.save(self.database_hw_filename)
                        self.database_hw.deactivate_past()
                        return
                    else:
                        self._message_notfound_()
                        return
                elif event.text == 'Отмена':
                    self._message_cancel()
                    return

    def _change_hw_(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.user_id == self.user:
                if re.match("\\s*\\d?\\d\\s*", event.text):
                    num = str.strip(event.text)
                    element = self.database_hw.get_by_num(int(num))
                    if element:
                        self.Lsvk.messages.send(
                            user_id=event.user_id,
                            message='Домашняя работа:\n' + element.get_str() + '\nВведите новые данные',
                            random_id=get_random_id()
                        )
                        self.database_hw.delete_by_num(int(num))
                        self._add_hw_()
                        if not self.database_hw.get_by_num(int(num)):
                            self.database_hw.add(element)
                        return
                    else:
                        self._message_notfound_()
                        return
                elif event.text == 'Отмена':
                    self._message_cancel()
                    return

    def _admin_add_(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.user_id == self.user:
                if re.match("\\s*\\d+\\s*", event.text):
                    self.database_admin.add(int(event.text))
                    self.database_admin.save(self.database_admin_filename)
                    self._message_success()
                    return
                elif event.text == 'Отмена':
                    self._message_cancel()
                    return
                else:
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Некорретное ID. Операция отменена',
                        keyboard=self.keyboard_admin.get_keyboard(),
                        random_id=get_random_id()
                    )
                    return

    def _admin_delete_(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.user_id == self.user:
                if event.text == str(self.god_id):
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Нельзя удалить админа админов!\nОперация отменена.',
                        keyboard=self.keyboard_admin.get_keyboard(),
                        random_id=get_random_id()
                    )
                    return
                elif event.text == str(event.user_id):
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Нельзя удалить самого себя.\nОперация отменена.',
                        keyboard=self.keyboard_admin.get_keyboard(),
                        random_id=get_random_id()
                    )
                    return
                elif re.match("\\s*\\d+\\s*", event.text) and int(event.text) in self.database_admin.get_database():
                    self.database_admin.delete(int(event.text))
                    self.database_admin.save(self.database_admin_filename)
                    self._message_success()
                    return
                elif event.text == 'Отмена':
                    self._message_cancel()
                    return
                else:
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Некорретное ID. Операция отменена',
                        keyboard=self.keyboard_admin.get_keyboard(),
                        random_id=get_random_id()
                    )
                    return

    def _show_admins_(self):
        output = 'Текущие админы:\n'
        for a in self.database_admin.get_database():
            user = self.api_requests.users.get(user_ids=a)
            user_name = [user[0].get('first_name'), user[0].get('last_name')]
            output += user_name[0] + " " + user_name[1] + " " + str(a) + "\n"
        self.Lsvk.messages.send(
            user_id=self.user,
            message=output,
            random_id=get_random_id()
        )

    def _listen_admin_(self, last_event):
        self.Lsvk.messages.send(
            user_id=last_event.user_id,
            keyboard=self.keyboard_admin.get_keyboard(),
            message='Панель управления ботом открыта.',
            random_id=get_random_id()
        )

        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.user_id == self.user:
                if event.text == 'Добавить':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_cancel.get_keyboard(),
                        message='Введите номер и дату дедлайна дз в формате:\nнн дд.мм.гг а\nГде нн - номер дз,\nдд.мм.гг - дата дедлайна (время выставляется автоматически),\nа - активно дз или нет (0 или 1).',
                        random_id=get_random_id()
                    )
                    self._add_hw_()
                elif event.text == 'Удалить':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_cancel.get_keyboard(),
                        message='Введите номер дз в формате: нн\nИли слово "все", чтобы удалить все.',
                        random_id=get_random_id()
                    )
                    self._delete_hw_()

                elif event.text == 'Изменить':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_cancel.get_keyboard(),
                        message='Введите номер дз в формате: нн',
                        random_id=get_random_id()
                    )
                    self._change_hw_()

                elif event.text == 'Показать активные':
                    active = ''
                    for h in self.database_hw.database:
                        if h.is_active:
                            active += h.get_str() + '\n'
                    if active == '':
                        self.Lsvk.messages.send(
                            user_id=event.user_id,
                            message='Пусто!',
                            random_id=get_random_id()
                        )
                    else:
                        self.Lsvk.messages.send(
                            user_id=event.user_id,
                            message=active,
                            random_id=get_random_id()
                        )

                elif event.text == 'Показать все':
                    all_hw = ''
                    for h in self.database_hw.database:
                        all_hw += h.get_str() + '\n'
                    if all_hw == '':
                        self.Lsvk.messages.send(
                            user_id=event.user_id,
                            message='Пусто!',
                            random_id=get_random_id()
                        )
                    else:
                        self.Lsvk.messages.send(
                            user_id=event.user_id,
                            message=all_hw,
                            random_id=get_random_id()
                        )

                elif event.text == 'Добавить админа':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_cancel.get_keyboard(),
                        message='Введите id нового админа в формате цифр',
                        random_id=get_random_id()
                    )
                    self._admin_add_()

                elif event.text == 'Удалить админа':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_cancel.get_keyboard(),
                        message='Введите id админа на съедение в формате цифр',
                        random_id=get_random_id()
                    )
                    self._admin_delete_()

                elif event.text == 'Показать админов':
                    self._show_admins_()

                elif event.text == 'Выйти':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_delay.get_keyboard(),
                        message='Привет!\nЭто бот для получения отсрочек по информатике в Школково.\nЧтобы попросить отсрочку, нажми на кнопку ниже.',
                        random_id=get_random_id()
                    )
                    return

    @staticmethod
    def str_trim(s: str):
        return str.lower(str.strip(s))

    @staticmethod
    def availability_check(id: int, name, hw_number: int):
        new_delay = delay(id, name, hw_number)
        print(id, name, hw_number)
        return True

    @staticmethod
    def keyboard_merge(keyboard1: VkKeyboard, keyboard2, one_time):
        """
            Добавляет кнопки из первой клавиатуры в первую строку и из второй во вторую.
            Цвет кнопок первой строки - синий, второй - серый.
        :param keyboard1: первая клавиатура
        :param keyboard2: вторая клавиатура
        :param one_time: параметр клавиатуры one_time
        :return: VkKeyboard
        """
        keyboard = VkKeyboard(one_time=one_time)
        for line_num in range(len(keyboard1.lines)):
            for key in keyboard1.lines[line_num]:
                try:
                    keyboard.add_button(key.get('action').get('label'), color=VkKeyboardColor.PRIMARY)
                except ValueError:
                    keyboard.add_line()
                    keyboard.add_button(key)
        keyboard.add_line()
        for line_num in range(len(keyboard2.lines)):
            for key in keyboard2.lines[line_num]:
                try:
                    keyboard.add_button(key.get('action').get('label'))
                except ValueError:
                    keyboard.add_line()
                    keyboard.add_button(key)
        return keyboard
