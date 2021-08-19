import threading
import time

from Bot import *

token = 'token'
users = []


def new_bot_instance(user, start_event):
    print("-----------------BEGIN")
    bot = Bot(token, user)
    bot.run(start_event)
    users.remove(user)
    print("-----------------END")


def main():
    vk_session = vk_api.VkApi(token=token)
    Lslongpoll = VkLongPoll(vk_session)
    for event in Lslongpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.from_user:
            if event.user_id not in users:
                users.append(event.user_id)
                thread = threading.Thread(target=new_bot_instance, args=(users[len(users)-1], event, ))
                thread.start()
            print(threading.enumerate())


if __name__ == "__main__":
    main()