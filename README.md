# Quiz бот

Проект предназначен проведения викторины через телеграм и вк бота.
Примеры реализованных ботов:
- `@dwmn_quiz_bot`
- [https://vk.com/public208966799](https://vk.com/public208966799)

![Пример telegram](https://media.giphy.com/media/O5Fe5bwkrhMEd49YPf/giphy.gif)
![Пример vk](https://media.giphy.com/media/l4pztTS7B0G4vaktKE/giphy.gif)

### Как установить

Создайте файл `.env` со следующими переменными:

- `TG_BOT_TOKEN` — токен телеграм бота службы поддержки.
- `REDIS_HOST` — хост от базы данных Redis.
- `REDIS_PORT` — порт от базы данных Redis.
- `REDIS_PASSWORD` — пароль от базы данных Redis.
- `VK_BOT_TOKEN` — ключ для общения бота через VK.
- `QUESTIONS_FOLDER` - имя папки с файлами викторины.


Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, если есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```

Чтобы запустить бота, необходимо выполнить команду:
```
python3 tg_bot.py
```
или
```
python3 vk_bot.py
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).