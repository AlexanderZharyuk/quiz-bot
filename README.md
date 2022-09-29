# QUIZ TIME

Bots with quizzes for the VK social network and the Telegram messenger.

### ▽ Getting Started
To get started, you need to install dependencies and libraries:
```shell
pip install -r requirements.txt
```

Then create a `.env` file with environment variables:
```
TELEGRAM_TOKEN=<YOUR-TELEGRAM-BOT-TOKEN>
REDIS_HOST=<REDIS-DB-HOST>
REDIS_PORT=<REDIS-DB-PORT>
REDIS_PASSWORD=<REDIS-DB-PASSWORD>
VK_API_TOKEN=<VK-GROUP-API-TOKEN>
```

- To obtain and access the Redis database, refer to the official website of [Redis](https://redis.com/).
- To get a VK group API token - go to your community settings and create an API key, and allow group messages.


You will also need to fill in the `quiz-questions/quizzes.txt` file with questions - it serves as a template for filling in, you can leave these questions and supplement them with your own according to the template.
### ▽ Launching bots
Bots are launched with the following commands:
```shell
python3bots/telegram_bot.py
python3bots/vk_bot.py
```
### ▽ Author
* [Alexander Zharyuk](https://github.com/AlexanderZharyuk)
