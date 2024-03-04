import pytest
import os
from api import PetFriendsV2  # Подставьте правильный путь к вашему модулю
from settings import valid_email, valid_password


pf = PetFriendsV2()


# Тест-кейс 1: Невалидный email при запросе API-ключа
def test_invalid_email_for_api_key():
    status, result = pf.get_api_key("invalid_email", valid_password)

    assert status == 403
    assert 'key' not in result


# Тест-кейс 2: Неверный API-ключ при запросе списка питомцев
def test_invalid_auth_key_for_pets_list():
    status, result = pf.get_list_of_pets({"key": "invalid_key"})
    assert status == 403
    assert 'pets' not in result


# Тест-кейс 3: Добавление питомца с невалидными данными
def test_invalid_age_for_create_pet(name='Абра', animal_type='Кадабра', age=-5, pet_photo='images/fix.jpg'):
    """Проверяем, что невалидные данные при создании питомца возвращают ошибку. Передаем возраст меньше 0"""

    # Получаем ключ auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Пытаемся создать питомца с невалидными данными. Заполняем возраст меньше 0
    status, result = pf.post_create_pet(auth_key, name, animal_type, age, pet_photo)

    # Проверяем, что статус ответа == 400 и возраст меньше 0
    assert status == 400
    assert int(result['age']) < 0


# Тест-кейс 4: Невалидный password при запросе API-ключа
def test_invalid_password_for_api_key():
    status, result = pf.get_api_key(valid_email, 'invalid_password')

    assert status == 403
    assert result['key'] not in result


# Тест-кейс 5: Обновление информации о несуществующем питомце
def test_update_nonexistent_pet_id():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.update_pet_info(auth_key, "nonexistent_id", "NewName", "NewType", 5)
    assert status == 400
    assert result['pet_id'] not in result


# Тест-кейс 6: Удаление несуществующего питомца
def test_delete_nonexistent_pet_id():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.delete_pet(auth_key, "nonexistent_id")
    assert status != 200
    assert result['pet_id'] not in result


# Тест-кейс 7: Добавление фото несуществующему питомцу
def test_add_photo_to_nonexistent_pet():
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    pet_photo = "images/fix.jpg"

    status, result = pf.post_add_photo_pet(auth_key, "nonexistent_id", pet_photo)
    assert status == 400
    assert result['pet_id'] not in result


# Тест-кейс 8: Добавление фото питомцу с не верным расширением файла
def test_add_photo_not_valid_data():
    """Проверяем возможность добавить питомцу фотографию или заменить текущее фото на новое"""

    # Запрашиваем ключ auth_key и получаем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    # Сохраняем в переменную pet_photo путь к фотографии
    pet_photo = 'images/fix1.png'

    # Получаем полный путь к изображению питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)



    # Если список не пустой, то добавляем фото питомцу
    if len(my_pets['pets']) > 0:

        # Сохраняем текущее значение pet_photo
        current_photo = my_pets['pets'][0]["pet_photo"]

        status, result = pf.post_add_photo_pet(auth_key, my_pets['pets'][0]['id'], pet_photo)

        # Проверяем, что статус ответа == 400 и фотография питомца не изменилась
        assert status == 400
        assert result["pet_photo"] == current_photo
    else:

        # Если список пустой, то создаем нового питомца и запрашиваем список своих питомцев
        pf.post_create_pet_simple(auth_key, "Рысь", "Кошка", 10)
        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

        # Сохраняем текущее значение pet_photo
        current_photo = my_pets['pets'][0]["pet_photo"]

        status, result = pf.post_add_photo_pet(auth_key, my_pets['pets'][0]['id'], pet_photo)

        # Проверяем, что статус ответа == 400 и фотография питомца изменилась
        assert status == 400
        assert result["pet_photo"] == current_photo


# Тест-кейс 9 Негативный тест-кейс. Удаление чужого питомца
def test_failed_delete_outsider_pet_by_id():
    """Проверяем возможность удаления не нашего питомца.
    Перед выполнением удаляем всех своих питомцев"""

    # Запрашиваем ключ auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Получаем список питомцев всех пользователей
    _, pets = pf.get_list_of_pets(auth_key, '')

    # Берем ID первого питомца из списка и отправляем запрос на удаление
    pet_id = pets['pets'][0]['id']

    status, _ = pf.delete_pet(auth_key, pet_id)

    # Запрашиваем список питомцев всех пользователей
    _, pets = pf.get_list_of_pets(auth_key, '')

    # Проверяем, что статус != 200 и в списке питомцев остался питомец с ID, который мы удаляли
    assert status == 200
    assert pet_id not in pets.values()


# Тест-кейс 10 Негативный тест-кейс. Обновление чужого питомца.
def test_put_update_pet_info_outsider_pet_by_id(name="Чужой", animal_type='Испорченый', age=77777):
    """Проверяем, что обновление информации о питомце работает"""

    # Запрашиваем ключ auth_key и получаем список питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, pets = pf.get_list_of_pets(auth_key, '')

    # Обновляем имя, тип животного и возраст
    status, result = pf.update_pet_info(auth_key, pets['pets'][0]['id'], name, animal_type, age)

    # проверяем, что статус ответа == 200 и измененные данные соответствуют заданным
    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == str(age)
