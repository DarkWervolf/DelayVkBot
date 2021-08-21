import threading
import time

from Bot import *

token = 'b592ffd312091f724d2fc6f3d77e08a726f743ab7e721b92a403f53e85c5626d020bdf9e9a7a0ab8d64ea'
users = []


def new_bot_instance(user, start_event, worker):
    if start_event.text == 'Завершить':
        users.remove(user)
        return
    print('-----------------BEGIN THREAD ' + str(threading.get_ident()) +'-----------------')
    bot = Bot(token, user, worker)
    bot.run(start_event)
    users.remove(user)
    print('-----------------END THREAD ' + str(threading.get_ident()) +'-----------------')


def main():
    while True:
        vk_session = vk_api.VkApi(token=token)
        Lslongpoll = VkLongPoll(vk_session)
        Lsvk = vk_session.get_api()
        worker = SpreadsheetsWorker()
        for event in Lslongpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.from_user:
                if Bot.str_trim(event.text) == 'справка':
                    Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Отсрочка - это персональный сдвиг дедлайна на 5 дней без изменения времени.\nВсего на курс у вас есть 10 отсрочек.\nПопросить отсрочку можно в данном боте, внимательно следуя инструкциям.\nНе советуем играть с ботом - он может и мизинец отхватить.\nПо всем техническим вопросам, касающихся бота, можете писать в учебную беседу курса',
                        random_id=get_random_id()
                    )
                elif Bot.str_trim(event.text) == 'завершить' and event.user_id not in users:
                    Lsvk.messages.send(
                        user_id=event.user_id,
                        message='Но я же...\nНичего не делал...',
                        random_id=get_random_id()
                    )
                elif event.user_id not in users:
                    users.append(event.user_id)
                    thread = threading.Thread(target=new_bot_instance, args=(users[len(users)-1], event, worker, ))
                    thread.start()


if __name__ == "__main__":
    main()