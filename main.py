from datetime import datetime

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_requests

import re
from multiprocessing import Process


class delay:
    def __init__(self, id: int, fullname: list, hw: int):
        self.id = id
        self.fullname = fullname
        self.hw = hw


class homework:
    def __init__(self, num: int, deadline: datetime, is_active: bool):
        self.num = num
        self.deadline = deadline
        self.is_active = is_active

    def print(self):
        print(str(self.num) + " " + str(self.deadline) + " " + str(self.is_active))

    def get_str(self):
        return str(self.num) + " " + str(self.deadline.strftime('%d.%m.%y')) + " " + str(int(self.is_active))


class database:
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
        with open(filename) as f:
            hw_all_str = f.readlines()
        for line in hw_all_str:
            hw = homework(int(line[:2]), make_deadline(str.strip(line[2:len(line)-3])), bool(int(line[len(line)-2])))
            self.add(hw)

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


def make_deadline(date: str):
    date += ' 23:00:00'
    deadline = datetime.strptime(date, '%d.%m.%y %H:%M:%S')
    return deadline


def availability_check(id: int, name, hw_number: int):
    new_delay = delay(id, name, hw_number)
    print(id, name, hw_number)
    return True


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


def listen_main():
    for event in Lslongpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.from_user:

            # admins panel
            if event.text == 'd27fh2fbskrbakq1r' and event.user_id in admins_id:
                listen_admin(event)

            # action for beginning
            if event.text == 'Начать':
                Lsvk.messages.send(
                    user_id=event.user_id,
                    keyboard=keyboard_delay.get_keyboard(),
                    message='Привет!\nЭто бот для получения отсрочек по информатике в Школково.\nЧтобы попросить отсрочку, нажми на кнопку ниже.',
                    random_id=get_random_id()
                )

            # action for delay
            if event.text in buttons_delay:
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message='Выбери номер домашней работы.',
                    keyboard=keyboard_hw_available.get_keyboard(),
                    random_id=get_random_id()
                )
                listen_delay()

            if event.text in buttons_default:
                if event.text == 'Справка':
                    Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Справка',
                        random_id=get_random_id()
                    )


def listen_delay_confirm():
    for event in Lslongpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.from_user:
            if event.text == 'Да':
                return True
            elif event.text == 'Нет':
                return False

            if event.text == 'Справка':
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message='Справка',
                    random_id=get_random_id()
                )
            elif event.text == "Завершить":
                Lsvk.messages.send(
                    user_id=event.user_id,
                    keyboard=keyboard_delay.get_keyboard(),
                    message='Это бот для получения отсрочек по информатике в Школково.\nЧтобы попросить отсрочку, нажми на кнопку ниже.',
                    random_id=get_random_id()
                )
                return
            else:
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message='Некорректная команда. Попробуй ещё раз.',
                    keyboard=keyboard_yesno.get_keyboard(),
                    random_id=get_random_id()
                )


def listen_delay():
    for event in Lslongpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.from_user:
            # action for hw number
            if event.text in hw_all:
                if event.text in hw_available:
                    Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Ты уверен, что хочешь попросить отсрочку? Назад пути не будет!',
                        keyboard=keyboard_yesno.get_keyboard(),
                        random_id=get_random_id()
                    )
                    if listen_delay_confirm():
                        # делаем запрос, чтобы получить фио человека
                        user = api_requests.users.get(user_ids=event.user_id)
                        user_name = [user[0].get('first_name'), user[0].get('last_name')]

                        if datetime.now() > database.get_by_num(int(event.text)).deadline:
                            Lsvk.messages.send(
                                user_id=event.user_id,
                                message='А всё, а всё, а надо было раньше...\nПосле дедлайна отсрочку взять уже нельзя.',
                                keyboard=keyboard_delay.get_keyboard(),
                                random_id=get_random_id()
                            )
                            return

                        if availability_check(event.user_id, user_name, int(event.text)):
                            Lsvk.messages.send(
                                user_id=event.user_id,
                                message='Отсрочка выдана!',
                                keyboard=keyboard_delay.get_keyboard(),
                                random_id=get_random_id()
                            )
                            return
                    else:
                        Lsvk.messages.send(
                            user_id=event.user_id,
                            message='Операция отменена, мизинец спасён.',
                            keyboard=keyboard_delay.get_keyboard(),
                            random_id=get_random_id()
                        )
                        return
                else:
                    Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Отсрочки на это дз уже недоступны. Введите другой номер дз.',
                        keyboard=keyboard_hw_available.get_keyboard(),
                        random_id=get_random_id()
                    )
            if event.text == 'Справка':
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message='Справка',
                    random_id=get_random_id()
                )
            elif event.text == "Завершить":
                Lsvk.messages.send(
                    user_id=event.user_id,
                    keyboard=keyboard_delay.get_keyboard(),
                    message='Это бот для получения отсрочек по информатике в Школково.\nЧтобы попросить отсрочку, нажми на кнопку ниже.',
                    random_id=get_random_id()
                )
                return
            elif re.match("\\s\\.\\s",event.text):
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message='Некорректная команда. Попробуй ещё раз.',
                    keyboard=keyboard_hw_available.get_keyboard(),
                    random_id=get_random_id()
                )


def add_hw():
    for event in Lslongpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if re.match("\\s*\\d?\\d\\s[0-3]\\d\\.(0[1-9]|1[0-2])\\.\\d\\d\\s[0-1]\\s*", event.text):
                line = str.strip(event.text)
                print(line)
                hw = homework(int(line[:2]), make_deadline(str.strip(line[2:len(line)-2])), bool(int(line[len(line)-1])))
                database.add(hw)
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message='Успех!',
                    random_id=get_random_id()
                )
                database.print()
                database.save("hw_all.txt")
                return
            elif event.text == 'Отмена':
                Lsvk.messages.send(
                    user_id=event.user_id,
                    keyboard=keyboard_admin.get_keyboard(),
                    message='Операция отменена',
                    random_id=get_random_id()
                )
                return


def delete_hw():
    for event in Lslongpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if re.match("\\s*\\d?\\d\\s*", event.text):
                num = str.strip(event.text)
                if database.delete_by_num(int(num)):
                    Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Успех!',
                        random_id=get_random_id()
                    )
                    database.save("hw_all.txt")
                    database.print()
                else:
                    Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Дз не найдено',
                        random_id=get_random_id()
                    )
                return
            elif event.text == 'Отмена':
                Lsvk.messages.send(
                    user_id=event.user_id,
                    keyboard=keyboard_admin.get_keyboard(),
                    message='Операция отменена',
                    random_id=get_random_id()
                )
                return


def change_hw():
    for event in Lslongpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if re.match("\\s*\\d?\\d\\s*", event.text):
                num = str.strip(event.text)
                element = database.get_by_num(int(num))
                if element:
                    Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Домашняя работа:\n'+element.get_str()+'\nВведите новые данные',
                        random_id=get_random_id()
                    )
                    database.delete_by_num(int(num))
                    print("addilka")
                    add_hw()
                    database.print()
                else:
                    Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Дз не найдено',
                        random_id=get_random_id()
                    )
                return
            elif event.text == 'Отмена':
                Lsvk.messages.send(
                    user_id=event.user_id,
                    keyboard=keyboard_admin.get_keyboard(),
                    message='Операция отменена',
                    random_id=get_random_id()
                )
                return


def admin_add():
    for event in Lslongpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if re.match("\\s*\\d+\\s*", event.text):
                admins_id.append(int(event.text))
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message='Успех!',
                    keyboard=keyboard_admin.get_keyboard(),
                    random_id=get_random_id()
                )
                return
            elif event.text == 'Отмена':
                Lsvk.messages.send(
                    user_id=event.user_id,
                    keyboard=keyboard_admin.get_keyboard(),
                    message='Операция отменена',
                    random_id=get_random_id()
                )
                return
            else:
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message='Некорретное ID. Операция отменена',
                    random_id=get_random_id()
                )


def admin_delete():
    for event in Lslongpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if re.match("\\s*\\d+\\s*", event.text) and int(event.text) in admins_id:
                admins_id.remove(int(event.text))
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message='Успех!',
                    keyboard=keyboard_admin.get_keyboard(),
                    random_id=get_random_id()
                )
                return
            elif event.text == 'Отмена':
                Lsvk.messages.send(
                    user_id=event.user_id,
                    keyboard=keyboard_admin.get_keyboard(),
                    message='Операция отменена',
                    random_id=get_random_id()
                )
                return
            else:
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message='Некорретное ID. Операция отменена',
                    random_id=get_random_id()
                )


def listen_admin(last_event):
    Lsvk.messages.send(
        user_id=last_event.user_id,
        keyboard=keyboard_admin.get_keyboard(),
        message='Панель управления ботом открыта.',
        random_id=get_random_id()
    )

    for event in Lslongpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.text == 'Добавить':
                Lsvk.messages.send(
                    user_id=event.user_id,
                    keyboard=keyboard_cancel.get_keyboard(),
                    message='Введите номер и дату дедлайна дз в формате:\nнн дд.мм.гг',
                    random_id=get_random_id()
                )
                add_hw()
            if event.text == 'Удалить':
                Lsvk.messages.send(
                    user_id=event.user_id,
                    keyboard=keyboard_cancel.get_keyboard(),
                    message='Введите номер дз в формате: нн',
                    random_id=get_random_id()
                )
                delete_hw()
            if event.text == 'Изменить':
                Lsvk.messages.send(
                    user_id=event.user_id,
                    keyboard=keyboard_cancel.get_keyboard(),
                    message='Введите номер дз в формате: нн',
                    random_id=get_random_id()
                )
                change_hw()
            if event.text == 'Показать активные':
                active = ''
                for h in database.database:
                    if h.is_active:
                        active += h.get_str()+'\n'
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message=active,
                    random_id=get_random_id()
                )
            if event.text == 'Показать все':
                all = ''
                for h in database.database:
                    all += h.get_str() + '\n'
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message=all,
                    random_id=get_random_id()
                )
            if event.text == 'Добавить админа':
                Lsvk.messages.send(
                    user_id=event.user_id,
                    keyboard=keyboard_cancel.get_keyboard(),
                    message='Введите id нового админа в формате цифр',
                    random_id=get_random_id()
                )
                admin_add()
            if event.text == 'Удалить админа':
                Lsvk.messages.send(
                    user_id=event.user_id,
                    keyboard=keyboard_cancel.get_keyboard(),
                    message='Введите id админа на съедение в формате цифр',
                    random_id=get_random_id()
                )
                admin_delete()
            if event.text == 'Выйти':
                Lsvk.messages.send(
                    user_id=event.user_id,
                    keyboard=keyboard_delay.get_keyboard(),
                    message='Привет!\nЭто бот для получения отсрочек по информатике в Школково.\nЧтобы попросить отсрочку, нажми на кнопку ниже.',
                    random_id=get_random_id()
                )
                return


token = 'token'
# коннект к вк
vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
Lslongpoll = VkLongPoll(vk_session)
Lsvk = vk_session.get_api()
api_requests = vk_requests.create_api(service_token=token)

#загрузка всех дз из файла
database = database()
database.read("hw_all.txt")
hw_all = database.get_database()
hw_available = database.get_active()

# buttons in chat
buttons_delay = ['Попросить отсрочку']
buttons_default = ['Справка', 'Завершить']

# клавиатура с кнопкой отсрочки + стандартными
keyboard_delay = VkKeyboard(one_time=False)
keyboard_delay.add_button(buttons_delay[0], color=VkKeyboardColor.PRIMARY)
keyboard_delay.add_line()
keyboard_delay.add_button(buttons_default[0])
keyboard_delay.add_button(buttons_default[1])

# клавиатура со стандартными кнопками
keyboard_default = VkKeyboard(one_time=False)
keyboard_default.add_button(buttons_default[0])
keyboard_default.add_button(buttons_default[1])

# клавиатура с доступными дз + стандартными
keyboard_hw_available = VkKeyboard(one_time=False)
for i in range(len(hw_available)):
    keyboard_hw_available.add_button(hw_available[i], color=VkKeyboardColor.PRIMARY)
keyboard_hw_available.add_line()
keyboard_hw_available.add_button('Справка')
keyboard_hw_available.add_button('Завершить')

# клавиатура с кнопками да,нет + стандартными
keyboard_yesno = VkKeyboard(one_time=False)
keyboard_yesno.add_button('Да', color=VkKeyboardColor.PRIMARY)
keyboard_yesno.add_button('Нет', color=VkKeyboardColor.PRIMARY)
keyboard_yesno.add_line()
keyboard_yesno.add_button(buttons_default[0])
keyboard_yesno.add_button(buttons_default[1])

#админская клавиатура
admins_id = [215762369]
keyboard_admin = VkKeyboard(one_time=False)
keyboard_admin.add_button('Добавить')
keyboard_admin.add_button('Удалить')
keyboard_admin.add_button('Изменить')
keyboard_admin.add_line()
keyboard_admin.add_button('Показать активные')
keyboard_admin.add_button('Показать все')
keyboard_admin.add_line()
keyboard_admin.add_button('Добавить админа')
keyboard_admin.add_button('Удалить админа')
keyboard_admin.add_button('Выйти')

keyboard_cancel = VkKeyboard(one_time=False)
keyboard_cancel.add_button('Отмена')


#listen_main()
'''
if __name__ == '__main__':
    proc = Process(target=listen_main)
    proc.start()
'''
listen_main()
'''
# start listening to messages
while True:
    try:
        listen_main()
    except Exception as e:
        print(e)
        print("Произошла ошибка. Перезапуск программы...")
        time.sleep(5)
        listen_main()
'''