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
from Keyboards import *


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

        self.admins_id = [215762369]

    def run(self, start_event):
        if start_event.text == 'Попросить отсрочку':
            self._message_delay_()
            if self._listen_delay_() == 0:
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

    def _listen_main_(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.from_user and event.user_id == self.user:
                # admins panel
                if event.text == 'd27fh2fbskrbakq1r' and event.user_id in self.admins_id:
                    self._listen_admin_(event)
                    return

                # action for beginning
                if event.text == 'Начать':
                    self._message_start_()

                # action for delay
                if event.text == 'Попросить отсрочку':
                    self._message_delay_()
                    if self._listen_delay_() == 0:
                        return

                if event.text == 'Завершить':
                    self._message_end()
                    return

    def _listen_delay_confirm_(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.from_user and event.user_id == self.user:
                if event.text == 'Да':
                    return True
                elif event.text == 'Нет':
                    return False

                elif event.text == "Завершить":
                    return False
                elif event.text == "Справка":
                    #сообщение будет отправлено из main
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

                            if datetime.now() > self.database.get_by_num(int(event.text)).deadline:
                                self.Lsvk.messages.send(
                                    user_id=event.user_id,
                                    message='А всё, а всё, а надо было раньше...\nПосле дедлайна отсрочку взять уже нельзя.',
                                    keyboard=self.keyboard_delay.get_keyboard(),
                                    random_id=get_random_id()
                                )
                                return 0

                            if Bot.availability_check(event.user_id, user_name, int(event.text)):
                                self.Lsvk.messages.send(
                                    user_id=event.user_id,
                                    message='Отсрочка выдана!',
                                    keyboard=self.keyboard_delay.get_keyboard(),
                                    random_id=get_random_id()
                                )
                                print("delay done")
                                return 0
                        else:
                            self._message_delaycancel_()
                            return 0
                    else:
                        self.Lsvk.messages.send(
                            user_id=event.user_id,
                            message='Отсрочки на это дз уже недоступны. Введите другой номер дз.',
                            keyboard=self.keyboard_hw_available.get_keyboard(),
                            random_id=get_random_id()
                        )
                elif event.text == "Завершить":
                    self._message_delaycancel_()
                    return 0
                elif re.match('\\s*\\d+\\s*', event.text):
                    self._message_notfound_()

    def _add_hw_(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.user_id == self.user:
                if re.match("\\s*\\d?\\d\\s[0-3]\\d\\.(0[1-9]|1[0-2])\\.\\d\\d\\s[0-1]\\s*", event.text):
                    line = str.strip(event.text)
                    print(line)
                    hw = homework(int(line[:2]), homework.make_deadline(str.strip(line[2:len(line) - 2])),
                                  bool(int(line[len(line) - 1])))
                    self.database.add(hw)
                    self._message_success()
                    self.database.print()
                    self.database.save("hw_all.txt")
                    return
                elif event.text == 'Отмена':
                    self._message_cancel()
                    return

    def _delete_hw_(self):
        for event in self.Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.user_id == self.user:
                if re.match("\\s*\\d?\\d\\s*", event.text):
                    num = str.strip(event.text)
                    if self.database.delete_by_num(int(num)):
                        self._message_success()
                        self.database.save("hw_all.txt")
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
                    element = self.database.get_by_num(int(num))
                    if element:
                        self.Lsvk.messages.send(
                            user_id=event.user_id,
                            message='Домашняя работа:\n' + element.get_str() + '\nВведите новые данные',
                            random_id=get_random_id()
                        )
                        self.database.delete_by_num(int(num))
                        self._add_hw_()
                        if not self.database.get_by_num(int(num)):
                            self.database.add(element)
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
                    self.admins_id.append(int(event.text))
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
                if re.match("\\s*\\d+\\s*", event.text) and int(event.text) in self.admins_id:
                    self.admins_id.remove(int(event.text))
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
                if event.text == 'Удалить':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_cancel.get_keyboard(),
                        message='Введите номер дз в формате: нн',
                        random_id=get_random_id()
                    )
                    self._delete_hw_()
                if event.text == 'Изменить':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_cancel.get_keyboard(),
                        message='Введите номер дз в формате: нн',
                        random_id=get_random_id()
                    )
                    self._change_hw_()
                if event.text == 'Показать активные':
                    active = ''
                    for h in self.database.database:
                        if h.is_active:
                            active += h.get_str() + '\n'
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message=active,
                        random_id=get_random_id()
                    )
                if event.text == 'Показать все':
                    all_hw = ''
                    for h in self.database.database:
                        all_hw += h.get_str() + '\n'
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        message=all_hw,
                        random_id=get_random_id()
                    )
                if event.text == 'Добавить админа':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_cancel.get_keyboard(),
                        message='Введите id нового админа в формате цифр',
                        random_id=get_random_id()
                    )
                    self._admin_add_()
                if event.text == 'Удалить админа':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_cancel.get_keyboard(),
                        message='Введите id админа на съедение в формате цифр',
                        random_id=get_random_id()
                    )
                    self._admin_delete_()
                if event.text == 'Выйти':
                    self.Lsvk.messages.send(
                        user_id=event.user_id,
                        keyboard=self.keyboard_delay.get_keyboard(),
                        message='Привет!\nЭто бот для получения отсрочек по информатике в Школково.\nЧтобы попросить отсрочку, нажми на кнопку ниже.',
                        random_id=get_random_id()
                    )
                    return

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