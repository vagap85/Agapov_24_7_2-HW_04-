from api import PetFriends
from settings import valid_email, valid_password
import os
import random
import pytest

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Барин', animal_type='пук',
                                     age='4', pet_photo='images/owl.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

    # Очистка: удаляем добавленного питомца
    pet_id = result['id']
    pf.delete_pet(auth_key, pet_id)


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Супер", "кот", "3", "images/owl.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мур', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


    # Начало практической работы
def test_add_new_pet_no_photo_valid_data(name='КРОНА', animal_type='ПИТ', age='555'):
    """Проверяем, что можно добавить питомца с корректными данными без фото"""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Сохраняем количество питомцев до добавления
    initial_pet_count = len(my_pets['pets']) if 'pets' in my_pets else 0

    # Добавляем питомца
    status, result = pf.add_new_pet_no_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == age

    # Проверяем, что количество питомцев увеличилось на 1
    _, my_pets_after = pf.get_list_of_pets(auth_key, "my_pets")
    assert len(my_pets_after['pets']) == initial_pet_count + 1

    # Очистка: удаляем добавленного питомца
    pet_id = result['id']
    pf.delete_pet(auth_key, pet_id)


def test_post_new_photo_of_pet_valid_data(pet_photo='images/try.jpg'):
    """Проверяем, что можно добавить фото питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Проверяем, что файл существует
    if not os.path.exists(pet_photo):
        raise FileNotFoundError(f"Файл {pet_photo} не найден.")

    # Запрашиваем ключ API и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Получаем список питомцев и берем id первого питомца
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if not my_pets['pets']:
        raise ValueError("Список питомцев пуст.")
    pet_id = my_pets['pets'][0]['id']

    # Отправляем запрос на добавление фото
    status, result = pf.post_new_photo_of_pet(auth_key, pet_id, pet_photo)

    # Проверяем, что запрос выполнен успешно
    if status is None:
        raise AssertionError("Запрос на добавление фото не выполнен.")

    # Логирование для отладки
    print(f"Статус ответа: {status}")
    print(f"Результат: {result}")

# НЕГАТИВНЫЕ ПРОВЕРКИ

#1. Проверка запроса ключа с невалидными email и password
def test_get_api_key_for_invalid_user(email="invalid@gmail.com", password="pipper"):
    status, result = pf.get_api_key(email, password)
    assert status != 200, "Невалидные данные должны возвращать статус отличный от 200"
    assert 'key' not in result, "Ключ не должен возвращаться для невалидных данных"

#2. Проверка запроса с валидным email, и невалидным password
def test_get_api_key_for_invalid_password(email="vagap007@gmail.com", password="123"):
    status, result = pf.get_api_key(email, password)
    assert status != 200, "Невалидные данные должны возвращать статус отличный от 200"
    assert 'key' not in result, "Ключ не должен возвращаться для невалидных данных"
    print(result)

#3. Проверка запроса с пустыми значениями email, password
def test_get_api_key_for_invalid_email_pass(email="", password=""):
    status, result = pf.get_api_key(email, password)
    assert status != 200, "Невалидные данные должны возвращать статус отличный от 200"
    assert 'key' not in result, "Ключ не должен возвращаться для невалидных данных"
    print(result)

#4. Добавляем питомца с пустыми значениями "Имя" и "Тип животного"
def test_add_new_pet_with_invalid_data(name='', animal_type='',
                                     age='4', pet_photo='images/owl.jpg'):
    """Проверяем что можно добавить питомца без имени и типа животного"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name # Добавлен питомец с пустыми значениями "Имя" и "Тип питомца"

#5. Обновляем питомца и вводим спецсимволы в значения "Имя" и "Тип животного"
def test_update_self_pet_info(name='!@#$%^&', animal_type="@#!$%", age=5):
    """Проверяем возможность обновления информации о питомце с использованием спецсимволов"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

#6. создаём питомца и в поле "Имя" вводим 260 символов
def test_add_new_pet_with_big_name_data(name='Любя, съешь щипцы, — вздохнёт мэр, — кайф жгуч. Шеф взъярён тчк щипцы с эхом гудбай Жюль. Эй, жлоб! Где туз? Прячь юных съёмщиц в шкаф. Экс-граф? Плюш изъят. Бьём чуждый цен хвощ! Эх, чужак! Общий съём цен шляп (юфть) — вдрызг! Любя, съешь щипцы, — вздохнёт мэр, — кайф жгуч. Шеф взъярён тчк щипцы с эхом гудбай Жюль. Эй, жлоб! Где туз? Прячь юных съёмщиц в шкаф. Экс-граф? Плюш изъят. Бьём чуждый цен хвощ! Эх, чужак! Общий съём цен шляп (юфть) — вдрызг! Любя, съешь щипцы, — вздохнёт мэр, — кайф жгуч. Шеф взъярён тчк щипцы с эхом гудбай Жюль. Эй, жлоб! Где туз? Прячь юных съёмщиц в шкаф. Экс-граф? Плюш изъят. Бьём чуждый цен хвощ! Эх, чужак! Общий съём цен шляп (юфть) — вдрызг! Любя, съешь щипцы, — вздохнёт мэр, — кайф жгуч. Шеф взъярён тчк щипцы с эхом гудбай Жюль. Эй, жлоб! Где туз? Прячь юных съёмщиц в шкаф. Экс-граф? Плюш изъят. Бьём чуждый цен хвощ! Эх, чужак! Общий съём цен шляп (юфть) — вдрызг! Любя, съешь щипцы, — вздохнёт мэр, — кайф жгуч. Шеф взъярён тчк щипцы с эхом гудбай Жюль. Эй, жлоб! Где туз? Прячь юных съёмщиц в шкаф. Экс-граф? Плюш изъят. Бьём чуждый цен хвощ! Эх, чужак! Общий съём цен шляп (юфть) — вдрызг! Любя, съешь щипцы, — вздохнёт мэр, — кайф жгуч. Шеф взъярён тчк щипцы с эхом гудбай Жюль. Эй, жлоб! Где туз? Прячь юных съёмщиц в шкаф. Экс-граф? Плюш изъят. Бьём чуждый цен хвощ! Эх, чужак! Общий съём цен шляп (юфть) — вдрызг!Любя, съешь щипцы, — вздохнёт мэр, — кайф', animal_type='тигр',
                                     age='4', pet_photo='images/owl.jpg'):
    """Проверяем что можно добавить питомца с именем в 260 символов"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name # Добавлен питомец с именем длиной в 260 символов

# Очистка: удаляем добавленного питомца
    pet_id = result['id']
    pf.delete_pet(auth_key, pet_id)

#7-8-9
import html


def test_get_api_key_missing_parameter():
    """
    Проверяем, что сервер возвращает ошибку, если отсутствует обязательный параметр (email или password).
    """
#7 Отправляем запрос без email (передаём пустую строку)
    status_without_email, result_without_email = pf.get_api_key("", "valid_password")
    print(f"Ответ сервера (без email): Статус: {status_without_email}, Результат: {result_without_email}")

    # Декодируем HTML-сущности в ответе
    decoded_result_without_email = html.unescape(result_without_email)

    # Проверяем статус и текст ошибки
    assert status_without_email == 403, f"Ожидалась ошибка 403, но получен статус {status_without_email}"
    assert "Forbidden" in decoded_result_without_email, "Ожидалось сообщение об ошибке в ответе"
    assert "This user wasn't found in database" in decoded_result_without_email, "Ожидалось сообщение об ошибке в ответе"

#8 Отправляем запрос без password (передаём пустую строку)
    status_without_password, result_without_password = pf.get_api_key("valid_email@example.com", "")
    print(f"Ответ сервера (без password): Статус: {status_without_password}, Результат: {result_without_password}")

    # Декодируем HTML-сущности в ответе
    decoded_result_without_password = html.unescape(result_without_password)

    # Проверяем статус и текст ошибки
    assert status_without_password == 403, f"Ожидалась ошибка 403, но получен статус {status_without_password}"
    assert "Forbidden" in decoded_result_without_password, "Ожидалось сообщение об ошибке в ответе"
    assert "This user wasn't found in database" in decoded_result_without_password, "Ожидалось сообщение об ошибке в ответе"

#9 Отправляем запрос без email и password (передаём пустые строки)
    status_without_both, result_without_both = pf.get_api_key("", "")
    print(f"Ответ сервера (без email и password): Статус: {status_without_both}, Результат: {result_without_both}")

    # Декодируем HTML-сущности в ответе
    decoded_result_without_both = html.unescape(result_without_both)

    # Проверяем статус и текст ошибки
    assert status_without_both == 403, f"Ожидалась ошибка 403, но получен статус {status_without_both}"
    assert "Forbidden" in decoded_result_without_both, "Ожидалось сообщение об ошибке в ответе"
    assert "This user wasn't found in database" in decoded_result_without_both, "Ожидалось сообщение об ошибке в ответе"


