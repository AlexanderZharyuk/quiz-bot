# QUIZ TIME
Боты с викторинами для социальной сети VK и месенджера Telegram.

Ссылки на ботов:
* [VK](https://vk.com/im?sel=-214647142)
* [Telegram](https://t.me/DVMNquizzesBot)

### ▽ Начало работы
Для начала работы необходимо установить зависимости и библиотеки:
```shell
pip install -r requirements.txt
```

После чего создать `.env`-файл с переменными окружения:
```
TELEGRAM_TOKEN=<YOUR-TELEGRAM-BOT-TOKEN>
REDIS_HOST=<REDIS-DB-HOST>
REDIS_PORT=<REDIS-DB-PORT>
REDIS_PASSWORD=<REDIS-DB-PASSWORD>
VK_API_TOKEN=<VK-GROUP-API-TOKEN>
```

- Для получения БД Redis и доступа к ней, обратитесь к официальному сайту [Redis](https://redis.com/).
- Для получения API-токена группы VK - зайдите в настройки своего сообщества и создайте API-ключ, а также разрешите сообщения группы.


Также вам необходимо будет заполнить вопросами файл `quiz-questions/quizzes.txt` - он служит шаблоном для заполнения, вы можете оставить эти вопросы и дополнить их своими по шаблону.
### ▽ Запуск ботов
Запуск ботов осуществляется командами:
```shell
python3 bots/telegram_bot.py
python3 bots/vk_bot.py
```
### ▽ Автор
* [Alexander Zharyuk](https://github.com/AlexanderZharyuk)
