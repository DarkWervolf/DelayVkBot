import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_requests
import requests
from vk_api.bot_longpoll import VkBotLongPoll
import datetime


class delay:
    def __init__(self, id: int, fullname: list, hw: int):
        id = id
        fullname = fullname
        hw = hw


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
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text  and event.from_user:

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
                listen_main()
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
            #action for hw number
            if event.text in hw_all:
                if event.text in hw_available:
                    Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Ты уверен, что хочешь попросить отсрочку? Назад пути не будет!',
                        keyboard=keyboard_yesno.get_keyboard(),
                        random_id=get_random_id()
                    )
                    if listen_delay_confirm():
                        #делаем запрос, чтобы получить фио человека
                        user = api_requests.users.get(user_ids=event.user_id)
                        user_name = [user[0].get('first_name'),user[0].get('last_name')]

                        print(datetime.datetime.now())

                        if availability_check(event.user_id, user_name, int(event.text)):
                            Lsvk.messages.send(
                                user_id=event.user_id,
                                message='Отсрочка выдана!',
                                keyboard=keyboard_delay.get_keyboard(),
                                random_id=get_random_id()
                            )
                            listen_main()
                    else:
                        Lsvk.messages.send(
                            user_id=event.user_id,
                            message='Операция отменена, мизинец спасён.',
                            keyboard=keyboard_delay.get_keyboard(),
                            random_id=get_random_id()
                        )
                        listen_main()
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
                listen_main()
            else:
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message='Некорректная команда. Попробуй ещё раз.',
                    keyboard=keyboard_hw_available.get_keyboard(),
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
            pass


token = 'b592ffd312091f724d2fc6f3d77e08a726f743ab7e721b92a403f53e85c5626d020bdf9e9a7a0ab8d64ea'
#коннект к вк
vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
Lslongpoll = VkLongPoll(vk_session)
Lsvk = vk_session.get_api()
api_requests = vk_requests.create_api(service_token=token)


#todo Запрос всех дз и доступных для отсрочки
hw_all = []
for i in range(1, 15):
    hw_all.append(str(i))
hw_available = ['13', '14']


#buttons in chat
buttons_delay = ['Попросить отсрочку', 'Попросить другую отсрочку']
buttons_default = ['Справка', 'Завершить']

#клавиатура с кнопкой отсрочки + стандартными
keyboard_delay = VkKeyboard(one_time=False)
keyboard_delay.add_button(buttons_delay[0], color=VkKeyboardColor.PRIMARY)
keyboard_delay.add_line()
keyboard_delay.add_button(buttons_default[0])
keyboard_delay.add_button(buttons_default[1])

#клавиатура со стандартными кнопками
keyboard_default = VkKeyboard(one_time=False)
keyboard_default.add_button(buttons_default[0])
keyboard_default.add_button(buttons_default[1])

#клавиатура с доступными дз + стандартными
keyboard_hw_available = VkKeyboard(one_time=False)
for i in range(len(hw_available)):
    keyboard_hw_available.add_button(hw_available[i], color=VkKeyboardColor.PRIMARY)
keyboard_hw_available.add_line()
keyboard_hw_available.add_button('Справка')
keyboard_hw_available.add_button('Завершить')

#клавиатура с кнопками да,нет + стандартными
keyboard_yesno = VkKeyboard(one_time=False)
keyboard_yesno.add_button('Да', color=VkKeyboardColor.PRIMARY)
keyboard_yesno.add_button('Нет', color=VkKeyboardColor.PRIMARY)
keyboard_yesno.add_line()
keyboard_yesno.add_button(buttons_default[0])
keyboard_yesno.add_button(buttons_default[1])


admins_id = [215762369]
keyboard_admin = VkKeyboard(one_time=False)
keyboard_admin.add_button('Добавить дз')
keyboard_admin.add_button('Показать текущие дз')

#start listening to messages
listen_main()