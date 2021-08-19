from datetime import datetime

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_requests

import re

from Delay import *
from Homework import *
from HWDatabase import *


class Bot:
    def __init__(self, token, user):
        self.user = user

        self.token = token
        vk_session = vk_api.VkApi(token=token)
        self.Lslongpoll = VkLongPoll(vk_session)
        self.Lsvk = vk_session.get_api()
        self.api_requests = vk_requests.create_api(service_token=token)

        # buttons in chat
        self.buttons_delay = ['Попросить отсрочку']
        self.buttons_default = ['Справка', 'Завершить']

        # клавиатура с кнопкой отсрочки + стандартными
        self.keyboard_delay = VkKeyboard(one_time=False)
        self.keyboard_delay.add_button(self.buttons_delay[0], color=VkKeyboardColor.PRIMARY)
        self.keyboard_delay.add_line()
        self.keyboard_delay.add_button(self.buttons_default[0])
        self.keyboard_delay.add_button(self.buttons_default[1])

        # клавиатура со стандартными кнопками
        self.keyboard_default = VkKeyboard(one_time=False)
        self.keyboard_default.add_button(self.buttons_default[0])
        self.keyboard_default.add_button(self.buttons_default[1])

        # загрузка всех дз из файла
        self.database = HWdatabase()
        self.database.read("hw_all.txt")
        self.hw_all = self.database.get_database()
        self.hw_available = self.database.get_active()

        # клавиатура с доступными дз + стандартными
        self.keyboard_hw_available = VkKeyboard(one_time=False)
        for i in range(len(self.hw_available)):
            self.keyboard_hw_available.add_button(self.hw_available[i], color=VkKeyboardColor.PRIMARY)
        self.keyboard_hw_available.add_line()
        self.keyboard_hw_available.add_button('Справка')
        self.keyboard_hw_available.add_button('Завершить')

        # клавиатура с кнопками да,нет + стандартными
        self.keyboard_yesno = VkKeyboard(one_time=False)
        self.keyboard_yesno.add_button('Да', color=VkKeyboardColor.PRIMARY)
        self.keyboard_yesno.add_button('Нет', color=VkKeyboardColor.PRIMARY)
        self.keyboard_yesno.add_line()
        self.keyboard_yesno.add_button(self.buttons_default[0])
        self.keyboard_yesno.add_button(self.buttons_default[1])

        # админская клавиатура
        self.admins_id = [215762369]
        self.keyboard_admin = VkKeyboard(one_time=False)
        self.keyboard_admin.add_button('Добавить')
        self.keyboard_admin.add_button('Удалить')
        self.keyboard_admin.add_button('Изменить')
        self.keyboard_admin.add_line()
        self.keyboard_admin.add_button('Показать активные')
        self.keyboard_admin.add_button('Показать все')
        self.keyboard_admin.add_line()
        self.keyboard_admin.add_button('Добавить админа')
        self.keyboard_admin.add_button('Удалить админа')
        self.keyboard_admin.add_button('Выйти')

        self.keyboard_cancel = VkKeyboard(one_time=False)
        self.keyboard_cancel.add_button('Отмена')

        self.Lsvk.messages.send(
            user_id=user,
            keyboard=self.keyboard_delay.get_keyboard(),
            message='Привет!\nЭто бот для получения отсрочек по информатике в Школково.\nЧтобы попросить отсрочку, нажми на кнопку ниже.',
            random_id=get_random_id()
        )

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

    def listen_main(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.from_user and event.user_id == self.user:
                # admins panel
                if event.text == 'd27fh2fbskrbakq1r' and event.user_id in self.admins_id:
                    self.listen_admin(event)

                # action for beginning
                if event.text == 'Начать':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_delay.get_keyboard(),
                        message='Привет!\nЭто бот для получения отсрочек по информатике в Школково.\nЧтобы попросить отсрочку, нажми на кнопку ниже.',
                        random_id=get_random_id()
                    )

                # action for delay
                if event.text in self.buttons_delay:
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Выбери номер домашней работы.',
                        keyboard=self.keyboard_hw_available.get_keyboard(),
                        random_id=get_random_id()
                    )
                    self.listen_delay()

                if event.text in self.buttons_default:
                    if event.text == 'Справка':
                        self.Lsvk.messages.send(
                            user_id=event.user_id,
                            message='Справка',
                            random_id=get_random_id()
                        )

    def listen_delay_confirm(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.from_user and event.user_id == self.user:
                if event.text == 'Да':
                    return True
                elif event.text == 'Нет':
                    return False

                if event.text == 'Справка':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Справка',
                        random_id=get_random_id()
                    )
                elif event.text == "Завершить":
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_delay.get_keyboard(),
                        message='Это бот для получения отсрочек по информатике в Школково.\nЧтобы попросить отсрочку, нажми на кнопку ниже.',
                        random_id=get_random_id()
                    )
                    return
                else:
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Некорректная команда. Попробуй ещё раз.',
                        keyboard=self.keyboard_yesno.get_keyboard(),
                        random_id=get_random_id()
                    )

    def listen_delay(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.from_user  and event.user_id == self.user:
                # action for hw number
                if event.text in self.hw_all:
                    if event.text in self.hw_available:
                        self.Lsvk.messages.send(
                            user_id=event.user_id,
                            message='Ты уверен, что хочешь попросить отсрочку? Назад пути не будет!',
                            keyboard=self.keyboard_yesno.get_keyboard(),
                            random_id=get_random_id()
                        )
                        if self.listen_delay_confirm():
                            # делаем запрос, чтобы получить фио человека
                            user = self.api_requests.users.get(user_ids=event.user_id)
                            user_name = [user[0].get('first_name'), user[0].get('last_name')]

                            if datetime.now() > self.database.get_by_num(int(event.text)).deadline:
                                self.Lsvk.messages.send(
                                    user_id=event.user_id,
                                    message='А всё, а всё, а надо было раньше...\nПосле дедлайна отсрочку взять уже нельзя.',
                                    keyboard=self.keyboard_delay.get_keyboard(),
                                    random_id=get_random_id()
                                )
                                return

                            if Bot.availability_check(event.user_id, user_name, int(event.text)):
                                self.Lsvk.messages.send(
                                    user_id=event.user_id,
                                    message='Отсрочка выдана!',
                                    keyboard=self.keyboard_delay.get_keyboard(),
                                    random_id=get_random_id()
                                )
                                return
                        else:
                            self.Lsvk.messages.send(
                                user_id=event.user_id,
                                message='Операция отменена, мизинец спасён.',
                                keyboard=self.keyboard_delay.get_keyboard(),
                                random_id=get_random_id()
                            )
                            return
                    else:
                        self.Lsvk.messages.send(
                            user_id=event.user_id,
                            message='Отсрочки на это дз уже недоступны. Введите другой номер дз.',
                            keyboard=self.keyboard_hw_available.get_keyboard(),
                            random_id=get_random_id()
                        )
                if event.text == 'Справка':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Справка',
                        random_id=get_random_id()
                    )
                elif event.text == "Завершить":
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_delay.get_keyboard(),
                        message='Это бот для получения отсрочек по информатике в Школково.\nЧтобы попросить отсрочку, нажми на кнопку ниже.',
                        random_id=get_random_id()
                    )
                    return
                elif re.match("\\s\\.\\s", event.text):
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Некорректная команда. Попробуй ещё раз.',
                        keyboard=self.keyboard_hw_available.get_keyboard(),
                        random_id=get_random_id()
                    )

    def add_hw(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                if re.match("\\s*\\d?\\d\\s[0-3]\\d\\.(0[1-9]|1[0-2])\\.\\d\\d\\s[0-1]\\s*", event.text):
                    line = str.strip(event.text)
                    print(line)
                    hw = homework(int(line[:2]), homework.make_deadline(str.strip(line[2:len(line) - 2])),
                                  bool(int(line[len(line) - 1])))
                    self.database.add(hw)
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Успех!',
                        random_id=get_random_id()
                    )
                    self.database.print()
                    self.database.save("hw_all.txt")
                    return
                elif event.text == 'Отмена':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_admin.get_keyboard(),
                        message='Операция отменена',
                        random_id=get_random_id()
                    )
                    return

    def delete_hw(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                if re.match("\\s*\\d?\\d\\s*", event.text):
                    num = str.strip(event.text)
                    if self.database.delete_by_num(int(num)):
                        self.Lsvk.messages.send(
                            user_id=event.user_id,
                            message='Успех!',
                            random_id=get_random_id()
                        )
                        self.database.save("hw_all.txt")
                        self.database.print()
                    else:
                        self.Lsvk.messages.send(
                            user_id=event.user_id,
                            message='Дз не найдено',
                            random_id=get_random_id()
                        )
                    return
                elif event.text == 'Отмена':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_admin.get_keyboard(),
                        message='Операция отменена',
                        random_id=get_random_id()
                    )
                    return

    def change_hw(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                if re.match("\\s*\\d?\\d\\s*", event.text):
                    num = str.strip(event.text)
                    element = self.database.get_by_num(int(num))
                    if element:
                        self.Lsvk.messages.send(
                            user_id=event.user_id,
                            message='Домашняя работа:\n' + element.get_str() + '\nВведите новые данные',
                            random_id=get_random_id()
                        )
                        self.database.delete_by_num(int(num))
                        print("addilka")
                        self.add_hw()
                        self.database.print()
                    else:
                        self.Lsvk.messages.send(
                            user_id=event.user_id,
                            message='Дз не найдено',
                            random_id=get_random_id()
                        )
                    return
                elif event.text == 'Отмена':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_admin.get_keyboard(),
                        message='Операция отменена',
                        random_id=get_random_id()
                    )
                    return

    def admin_add(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                if re.match("\\s*\\d+\\s*", event.text):
                    self.admins_id.append(int(event.text))
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Успех!',
                        keyboard=self.keyboard_admin.get_keyboard(),
                        random_id=get_random_id()
                    )
                    return
                elif event.text == 'Отмена':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_admin.get_keyboard(),
                        message='Операция отменена',
                        random_id=get_random_id()
                    )
                    return
                else:
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Некорретное ID. Операция отменена',
                        random_id=get_random_id()
                    )

    def admin_delete(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                if re.match("\\s*\\d+\\s*", event.text) and int(event.text) in self.admins_id:
                    self.admins_id.remove(int(event.text))
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Успех!',
                        keyboard=self.keyboard_admin.get_keyboard(),
                        random_id=get_random_id()
                    )
                    return
                elif event.text == 'Отмена':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_admin.get_keyboard(),
                        message='Операция отменена',
                        random_id=get_random_id()
                    )
                    return
                else:
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Некорретное ID. Операция отменена',
                        random_id=get_random_id()
                    )

    def listen_admin(self, last_event):
        self.Lsvk.messages.send(
            user_id=last_event.user_id,
            keyboard=self.keyboard_admin.get_keyboard(),
            message='Панель управления ботом открыта.',
            random_id=get_random_id()
        )

        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                if event.text == 'Добавить':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_cancel.get_keyboard(),
                        message='Введите номер и дату дедлайна дз в формате:\nнн дд.мм.гг',
                        random_id=get_random_id()
                    )
                    self.add_hw()
                if event.text == 'Удалить':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_cancel.get_keyboard(),
                        message='Введите номер дз в формате: нн',
                        random_id=get_random_id()
                    )
                    self.delete_hw()
                if event.text == 'Изменить':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_cancel.get_keyboard(),
                        message='Введите номер дз в формате: нн',
                        random_id=get_random_id()
                    )
                    self.change_hw()
                if event.text == 'Показать активные':
                    active = ''
                    for h in self.database.self.database:
                        if h.is_active:
                            active += h.get_str() + '\n'
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message=active,
                        random_id=get_random_id()
                    )
                if event.text == 'Показать все':
                    all = ''
                    for h in self.database.self.database:
                        all += h.get_str() + '\n'
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message=all,
                        random_id=get_random_id()
                    )
                if event.text == 'Добавить админа':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_cancel.get_keyboard(),
                        message='Введите id нового админа в формате цифр',
                        random_id=get_random_id()
                    )
                    self.admin_add()
                if event.text == 'Удалить админа':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_cancel.get_keyboard(),
                        message='Введите id админа на съедение в формате цифр',
                        random_id=get_random_id()
                    )
                    self.admin_delete()
                if event.text == 'Выйти':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_delay.get_keyboard(),
                        message='Привет!\nЭто бот для получения отсрочек по информатике в Школково.\nЧтобы попросить отсрочку, нажми на кнопку ниже.',
                        random_id=get_random_id()
                    )
                    return
