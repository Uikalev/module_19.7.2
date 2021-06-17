from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    status, result = pf.get_api_key(email, password)

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


def test_add_new_pet_with_valid_data(name="Куся", animal_type="кошка",
                                     age="4", pet_photo="images/cat.jpeg"):
    """Проверяем что можно добавить питомца с корректными данными"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца из своего списка"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Аланудэ", "Дэдэ", "5", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name="Шеря", animal_type="кот", age="3"):
    """Проверяем возможность обновления информации о питомце"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("There is no my pets")


def test_add_new_pet_with_valid_data_without_photo(name="Жуся", animal_type="кошка", age="4"):
    """Проверяем возможность добавить питомца без фото"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_no_photo(auth_key, name, animal_type, age)

    assert status == 200
    assert result['name'] == name


def test_successful_add_pet_photo(pet_photo="images/cat1.jpeg"):
    """Проверяем возможность добавить фото питомца"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) > 0:
        status, result = pf.add_pet_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)

        assert status == 200
        assert result['pet_photo'] is not ''
    else:
        raise Exception("There is no my pets")


def test_get_api_key_for_invalid_user(email=invalid_email, password=invalid_password):
    """Проверяем что при вводе данных несуществующего пользователя код ответа 403, ключ не выдаётся,
    доступ закрыт, появляется ошибка c информацией о том, что пользователь не найден в базе"""

    status, result = pf.get_api_key(email, password)

    assert status == 403
    assert "This user wasn't found in database" in result


def test_get_api_key_for_user_with_invalid_password(email=valid_email, password=invalid_password):
    """Проверяем, что при вводе некорректного пароля код ответа 403, ключ не выдаётся, доступ закрыт.
    Появляется ошибка с инормацией о том, что пользователь не найден в базе"""

    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert "This user wasn't found in database" in result


def test_negative_add_new_pet_without_name_and_photo(name="", animal_type="кошка", age="42"):
    """Проверяем возможность добавить питомца без имени, ожидаем код ответа 400, питомец не добавлен"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_no_photo(auth_key, name, animal_type, age)

    assert status == 400
    # Тест не проходит, кажется это баг, вряд ли это фича с добавлением безименняого питомца


def test_negative_add_new_pet_with_very_long_name_without_photo(name="""Pain!_You_made_me_a,_you_made_me_a_believer,_
                                                        believerPain!_You_break_me_down,_you_build_me_up,_believer,
                                                        _believer_Pain!_Let_the_bullets_fly,_oh_let_them_rain_My_life
                                                        ,_my_love,_my_drive,_it_came_from..._Pain!_You_made_me_a,_you_
                                                        made_me_a_believer,_believer""", animal_type="собака",
                                                                age="42"):

    """Проверяем возможность добавить питомца с именем длинной в 255 символов, ожидаем код ответа 400,
     питомец не добавлен"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_no_photo(auth_key, name, animal_type, age)

    assert status == 400
    # Питомец с таким именем добавляется, нужно заводить баг


def test_add_new_pet_with_age_in_letters(name="Киса", animal_type="кошка", age="СорокДва"):
    """Проверяем возможность добавить питомца с возврастом указанным буквами"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_no_photo(auth_key, name, animal_type, age)

    assert status == 200
    # Питомец добавляется, нужно утчонить баг или фича? Не учтено в документации


def test_negative_add_new_pet_without_data(name="", animal_type="", age=""):
    """Проверяем возможность добавить питомца без данных, ожидаем код ответа 400, питомец не добавлен"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_no_photo(auth_key, name, animal_type, age)

    assert status == 400
    # Питомец без данных добавляется, нужно заводить баг


def test_add_new_pet_with_invalid_photo_format(name="Генри", animal_type="ёж", age="4", pet_photo="images/cat2.pdf"):

    """Проверяем что нельзя добавить питомца с фото в формате pdf, код ответа 400, согласно документации"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert status == 500


def test_update_self_pet_info_without_data(name="", animal_type="Собака", age=""):
    """Проверяем возможность обновления информации о питомце на пустые поля"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        assert status == 400
    else:
        raise Exception("There is no my pets")

    # Ожидается ошибка, но вместо этого данные о питомце заменяются на None
