import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import logging

logging.basicConfig(level=logging.INFO)

class PetFriends:
    """апи библиотека к веб приложению Pet Friends"""

    def __init__(self):
        self.base_url = "https://petfriends.skillfactory.ru/"

    def get_api_key(self, email: str, passwd: str) -> json:
        """Метод делает запрос к API сервера и возвращает статус запроса и результат в формате
        JSON с уникальным ключем пользователя, найденного по указанным email и паролем"""

        headers = {
            'email': email,
            'password': passwd,
        }
        res = requests.get(self.base_url+'api/key', headers=headers)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text

        logging.info(f"Ответ сервера: {result}")
        return status, result

    def get_list_of_pets(self, auth_key: json, filter: str = "") -> json:
        """Метод делает запрос к API сервера и возвращает статус запроса и результат в формате JSON
        со списком найденных питомцев, совпадающих с фильтром. На данный момент фильтр может иметь
        либо пустое значение - получить список всех питомцев, либо 'my_pets' - получить список
        собственных питомцев"""

        headers = {'auth_key': auth_key['key']}
        filter = {'filter': filter}

        res = requests.get(self.base_url + 'api/pets', headers=headers, params=filter)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def add_new_pet(self, auth_key: json, name: str, animal_type: str,
                    age: str, pet_photo: str) -> json:
        """Метод отправляет (постит) на сервер данные о добавляемом питомце и возвращает статус
        запроса на сервер и результат в формате JSON с данными добавленного питомца"""

        data = MultipartEncoder(
            fields={
                'name': name,
                'animal_type': animal_type,
                'age': age,
                'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'image/jpeg')
            })
        headers = {'auth_key': auth_key['key'], 'Content-Type': data.content_type}

        res = requests.post(self.base_url + 'api/pets', headers=headers, data=data)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        print(result)
        return status, result

    def delete_pet(self, auth_key: json, pet_id: str) -> json:
        """Метод отправляет на сервер запрос на удаление питомца по указанному ID и возвращает
        статус запроса и результат в формате JSON с текстом уведомления о успешном удалении.
        На сегодняшний день тут есть баг - в result приходит пустая строка, но status при этом = 200"""

        headers = {'auth_key': auth_key['key']}

        res = requests.delete(self.base_url + 'api/pets/' + pet_id, headers=headers)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def update_pet_info(self, auth_key: json, pet_id: str, name: str,
                        animal_type: str, age: int) -> json:
        """Метод отправляет запрос на сервер об обновлении данных питомца по указанному ID и
        возвращает статус запроса и result в формате JSON с обновлённыими данными питомца"""

        headers = {'auth_key': auth_key['key']}
        data = {
            'name': name,
            'age': age,
            'animal_type': animal_type
        }

        res = requests.put(self.base_url + 'api/pets/' + pet_id, headers=headers, data=data)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result


    def add_new_pet_no_photo(self, auth_key: dict, name: str, animal_type: str, age: str) -> tuple:
        """
        Метод отправляет на сервер данные о добавляемом питомце без фотографии и возвращает статус
        запроса на сервер и результат в формате JSON с данными добавленного питомца.
        """
        # Проверка входных данных
        if not isinstance(name, str) or not isinstance(animal_type, str) or not isinstance(age, str):
            raise ValueError("Все параметры (name, animal_type, age) должны быть строками")

        # Подготовка данных
        data = MultipartEncoder(
            fields={
                'name': name,
                'animal_type': animal_type,
                'age': age
            })
        headers = {'auth_key': auth_key['key'], 'Content-Type': data.content_type}

        # Отправка запроса
        try:
            res = requests.post(self.base_url + 'api/create_pet_simple', headers=headers, data=data)
            res.raise_for_status()  # Проверка на ошибки 4xx/5xx
            status = res.status_code
            result = res.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка при выполнении запроса: {e}")
            status = None
            result = str(e)
        except json.decoder.JSONDecodeError:
            logging.warning("Ответ сервера не может быть декодирован как JSON")
            status = res.status_code
            result = res.text

        logging.info(f"Ответ сервера: {result}")
        return status, result

    def post_new_photo_of_pet(self, auth_key: dict, pet_id: str, pet_photo: str) -> tuple[int, dict | str]:
        """Метод отправляет на сервер данные о добавлении фото питомца и возвращает статус
        запроса на сервер и результат в формате JSON с данными добавленного питомца"""

               # Открытие файла и формирование данных
        with open(pet_photo, 'rb') as file:
            data = MultipartEncoder(
                fields={
                    'pet_id': pet_id,
                    'pet_photo': (pet_photo, file, 'image/jpeg')
                })
            headers = {'auth_key': auth_key['key'], 'Content-Type': data.content_type}

            # Выполнение запроса
            try:
                res = requests.post(self.base_url + f'/api/pets/set_photo/{pet_id}', headers=headers, data=data)
                res.raise_for_status()  # Проверка на ошибки 4xx/5xx
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при выполнении запроса: {e}")
                return None

            # Обработка ответа
            status = res.status_code
            try:
                result = res.json()
            except requests.exceptions.JSONDecodeError:
                result = res.text
            print(result)
            return status, result






