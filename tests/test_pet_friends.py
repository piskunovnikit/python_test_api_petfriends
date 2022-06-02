from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os
from requests_toolbelt.multipart.encoder import MultipartEncoder
pf = PetFriends()

def test_api_key_for_valid_users(email=valid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result

def test_get_all_pets_with_valid_key(filter=''):
    _,auth_key = pf.get_api_key(valid_email,valid_password)
    status, result = pf.get_list_of_pets(auth_key,filter)
    assert status == 200
    assert len(result['pets'])>0

def test_add_new_pet_with_valid_data(name='изюм', animal_type='шотландский',
                                     age='4', pet_photo='images/cat.jpeg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()

def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_add_new_pet_without_foto_valid_data(name='изюм', animal_type='шотландский',
                                     age=4):
    """Проверяем что можно добавить питомца с корректными данными без фото"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_add_foto_pet_info(pet_photo='images/cat.jpeg'):
    """Проверяем возможность обновления информации о питомце только фото"""

    # Получаем ключ auth_key и список своих питомцев
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id = my_pets['pets'][0]['id']
    # Еслди список не пустой, то пробуем добавить фото
    if len(my_pets['pets']) > 0:
        status, result = pf.add_pet_foto(auth_key, pet_id, pet_photo)
        data = MultipartEncoder(fields={'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'image/jpeg')
                                        })  # записываем в переменную битовый код фотографии с компьютера
        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        # assert result['pet_photo'] == cat
        assert data == result[
            'pet_photo']  # сравниваем битовый код фотографии с компьютера с кодом фотографии на сервере
    else:
        raise Exception("There is no my pets")



def test_get_api_key_for_invalid_email(email=invalid_email,password=valid_password):
    """проверяем возможность входа с неверным логином"""
    status, result = pf.get_api_key(email, password)
    assert status == 403


def test_get_api_key_for_invalid_password(email=valid_email,password=invalid_password):
    """проверяем возможность входа с неверным паролем"""
    status, result = pf.get_api_key(email, password)
    assert status == 403


def test_add_new_pet_with_invalid_key(name='изюм',animal_type='шотландский',age='1',pet_photo='images/cat.jpeg'):
    """проверяем возможность добавления питомца с неверным ключом"""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_list_of_pets(valid_email, valid_password)
    auth_key = auth_key+'a'
    status,result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 403

def test_successful_delete_self_pet_with_invalid_key():
    """проверяем возможность удаления питомца с неверным ключом"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key,
                                     "my_pets")  # Получаем правильный ключ auth_key и запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:  # если у меня нет никаких питомцев, добавляем питомца
        pf.add_new_pet(auth_key, 'изюм', 'шотландский', "1", 'images/cat.jpeg')
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")  # снова получаем список питомцев - он будет один

    pet_id = my_pets['pets'][0]['id']  # достаем идентификатор последнего добавленного питомца - через словарь
    auth_key = auth_key + 'x'  # "портим" ключ
    status, _ = pf.delete_pet(auth_key,
                                  pet_id)  # получаем статус-код ответа на запрос удаления питомца с испорченным ключом
    assert status == 403
    # проверяем, что id питомца остался в базе
    for i in my_pets['pets']:
        assert pet_id in i.values()



def test_add_new_pet_without_name(animal_type='шотландский',age='2',pet_photo='images/cat.jpeg'):
    """проверяем возможность добавления питомца без имени"""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, animal_type, age, pet_photo)
    assert status == 400


def test_add_new_pet_without_animal_type(name='фрай', age='3', pet_photo='images/cat.jpeg'):
    """проверяем возможность добавления питомца без типа"""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, age, pet_photo)
    assert status == 400



def test_add_new_pet_without_age(name='изюм',animal_type='щотландский',pet_photo='images/cat.jpeg'):
    """проверяем возможность добавления питомца без возраста"""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, pet_photo)
    assert status == 400


def test_add_new_pet_with_long_name_lengt(name='rex'*1000000,animal_type='шотл',age='3',pet_photo='images/cat.jpeg'):
    """проверяем возможность добавления питомца, с очень длинным именем"""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400


# проверяем возможность добавления питомца, с очень длинным типом
def test_add_new_pet_with_long_animal_type_lengt(name='изюм',animal_type='щотл'*100000,age='5',pet_photo='images/cat.jpeg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result=pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400


def test_add_new_pet_with_long_age_lengt(name='ИЗЮМ',animal_type='шотл',age='5'*1000000,pet_photo='images/cat.jpeg'):
    """проверяем возможность добавления питомца, с очень длинным возрастом"""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status,result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400


def test_add_new_pet_with_invalid_photo(name='ИЗЮм',animal_type='шотл',age='3',pet_photo='images/valera.jpg'):
    """проверяем возможность добавления питомца, если такого фото в директории не существует"""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status,result=pf.add_new_pet(auth_key,name,animal_type,age,pet_photo)
    assert status == 400
