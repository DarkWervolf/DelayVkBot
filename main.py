import threading
import time

from Bot import *

THREADS_COUNT = 10
token = ''
users = []


def new_bot_instance(user):
    bot = Bot(token, user)
    bot.listen_main()


def main():
    vk_session = vk_api.VkApi(token=token)
    Lslongpoll = VkLongPoll(vk_session)
    for event in Lslongpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text and event.from_user:
            if event.user_id not in users:
                users.append(event.user_id)
                thread = threading.Thread(target=new_bot_instance, args=(users[len(users)-1],))
                thread.start()


if __name__ == "__main__":
    main()