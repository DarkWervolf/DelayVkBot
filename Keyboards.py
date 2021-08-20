from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# buttons in chat
button_delay = 'Попросить отсрочку'
buttons_default = ['Справка', 'Завершить']


# клавиатура с кнопкой отсрочки + стандартными
def keyboard_delay():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button(button_delay, color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button(buttons_default[0])
    keyboard.add_button(buttons_default[1])
    return keyboard


# клавиатура со стандартными кнопками
def keyboard_default():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button(buttons_default[0])
    keyboard.add_button(buttons_default[1])
    return keyboard


# клавиатура с кнопками да,нет + стандартными
def keyboard_yesno():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Да', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Нет', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button(buttons_default[0])
    keyboard.add_button(buttons_default[1])
    return keyboard


def keyboard_admin():
    # админская клавиатура
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Добавить')
    keyboard.add_button('Удалить')
    keyboard.add_button('Изменить')
    keyboard.add_line()
    keyboard.add_button('Показать активные')
    keyboard.add_button('Показать все')
    keyboard.add_line()
    keyboard.add_button('Добавить админа')
    keyboard.add_button('Удалить админа')
    keyboard.add_button('Показать админов')
    keyboard.add_line()
    keyboard.add_button('Выйти')
    return keyboard


def keyboard_cancel():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Отмена')
    return keyboard