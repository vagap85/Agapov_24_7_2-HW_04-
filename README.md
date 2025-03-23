# Agapov_24_7_2-HW_04

Для запуска тестов откройте файл "test_petfriends.py" установите библиотеки- pip install- pytest, random, toolbelt, logging.
Методы в файле "api.py"
Валидные данные для тестов в файле "settings.py", создавал файл .env, но плагин env не устанавливается(ошибка)

Тесты: с 1-5 те что сделали в модуле.
Начало практической работы с 100 строки файла "test_petfriends.py"
Добавил: 
6. Добавить питомца с корректными данными без фото
7. Добавить фото питомца с корректными данными

Негативные проверки со 160 строки
1. Проверка запроса ключа с невалидными email и password
2. Проверка запроса с валидным email, и невалидным password
3. Проверка запроса с пустыми значениями email, password. Статус200
4. Добавляем питомца с пустыми значениями "Имя" и "Тип животного"
5. Обновляем питомца и вводим спецсимволы в значения "Имя" и "Тип животного"
6. Создаём питомца и в поле "Имя" вводим 260 символов
7. Отправляем запрос без email (передаём пустую строку)
8. Отправляем запрос без password (передаём пустую строку)
9. Отправляем запрос без email и password (передаём пустые строки). Статус 403
