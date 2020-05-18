from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from TOKENS import GEOCODER_TOKEN, YANDEX_TRANSLATE_TOKEN
import requests
import os
from data import db_session
from data.users import Users
from data.notes import Notes
from registration_form import RegistrationForm
from login_form import LoginForm
from notes_form import NotesForm
from edit_notes_form import EditNotesForm
from profile_form import ProfileForm
from search_form import SearchForm
from translate_form import TranslateForm
import notes_api

# Инициализация приложения
app = Flask(__name__)
# Добавление CSRF-ключа
app.config['SECRET_KEY'] = 'dtqopdsmdsreiwpsancxvsdt843634hfdcdjfew8439fjbh20'
app.register_blueprint(notes_api.blueprint)

# Добавление LoginManager
login_manager = LoginManager()
login_manager.init_app(app)


# Инициализация БД и запуск приложения
def main():
    db_session.global_init('db/white_note.db')
    app.run(port=8080, host='127.0.0.1')


# Главная страница
@app.route('/')
def main_page():
    return render_template('main.html')


# Загрузка пользователя
@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()

    return session.query(Users).get(user_id)


# Регистрация
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    # Форма регистрации
    form = RegistrationForm()

    # POST
    if form.validate_on_submit():
        # Проверка паролей на совпадение
        if form.password.data != form.password_again.data:
            return render_template('registration.html', form=form, message='Пароли не совпадают!')

        # Создаём сессию подключения к БД
        session = db_session.create_session()
        # Проверка почты на уникальность
        if session.query(Users).filter(Users.email == form.email.data).first():
            return render_template('registration.html', form=form,
                                   message='Пользователь с такой почтой уже существует!')
        # Проверка логина на уникальность
        if session.query(Users).filter(Users.login == form.login.data).first():
            return render_template('registration.html', form=form,
                                   message='Пользователь с таким логином уже существует!')

        # Добавление пользователя в БД
        user = Users(
            login=form.login.data,
            email=form.email.data)
        # Генерация хешированного пароля
        user.generate_hashed_password(form.password.data)

        session.add(user)
        # Сохранение пользователя
        session.commit()
        # Перенаправление на страницу входа
        return redirect('/login')

    return render_template('registration.html', form=form)


# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Форма входа
    form = LoginForm()

    # POST
    if form.validate_on_submit():
        # Создание сессии подключения к БД
        session = db_session.create_session()

        # Проверка существования пользователя и правильности введённого пароля
        user = session.query(Users).filter(Users.login == form.login.data).first()
        if user and user.check_hashed_password(form.password.data):
            # Логин пользователя
            login_user(user, remember=form.remember_me.data)
            # Перенаправление на главную страницу
            return redirect('/')
        # Если данные не верны, сообщение об ошибке
        return render_template('login.html', message='Неправильный логин или пароль!', form=form)

    return render_template('login.html', form=form)


# Сортировка и вывод всех записей пользователя
@app.route('/note')
@login_required
def note():
    # Создание сессии подключения к БД
    session = db_session.create_session()

    # Получение всех записок текущего пользователя
    notes = session.query(Notes).filter(Notes.user == current_user)
    # Сортировка по важности
    notes = sorted(notes, key=lambda x: x.is_important, reverse=True)
    return render_template('notes.html', notes=notes)


# Добавление записей
@app.route('/add_note', methods=['GET', 'POST'])
@login_required
def add_note():
    # Форма добавления записей
    form = NotesForm()

    # POST
    if form.validate_on_submit():
        image_path = ''
        place = form.place.data
        # Если указан адрес
        if place:
            # Получение фотографии местности с помощью Yandex.Maps Static API
            try:
                lon_lat = get_coordinates(place)
                image = get_map(lon_lat)
                image_path = f'static/image/users_image/map{len(os.listdir("static/image/users_image"))}.png'
                with open(image_path, 'wb') as file:
                    file.write(image)

            except Exception:
                return render_template('notes_form.html', form=form, message='Не удалось получить карту,'
                                                                             ' проверьте'
                                                                             ' корректность введенных данных!')
        # Если загружена картинка
        elif form.image.data.filename:
            # Имя, расширение файла
            name, extension = form.image.data.filename.split(".")

            # Если файл - не изображение, сообщение об ошибке
            if extension not in ['jpg', 'png', 'jpeg', 'tif', 'bmp']:
                return render_template('notes_form.html', form=form, message='Недопустимый формат файла!'
                                                                             ' Только ".jpg",'
                                                                             ' ".png", ".jpeg", ".tif", ".bmp"')
            # Получение изображения
            image = form.image.data
            # Сохранение изображения
            image_path = f'static/image/users_image/{name}{len(os.listdir("static/image/users_image"))}.{extension}'

            image.save(image_path)

        # Создание сессии подключения к БД
        session = db_session.create_session()

        # Добавление новой записи
        note = Notes(
            title=form.title.data,
            body=form.body.data,
            is_important=form.is_important.data,
            user_id=current_user.id
        )
        # Если был указан адрес или загружено изображение
        if image_path:
            note.images = image_path

        session.add(note)
        # Сохранение записи
        session.commit()
        # Перенаправление на страницу с записками
        return redirect('/note')

    return render_template('notes_form.html', form=form)


# Получение координат по указанному адресу
def get_coordinates(address):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": GEOCODER_TOKEN,
        "geocode": address,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if response:
        json_response = response.json()

        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]

        return ','.join(toponym_coodrinates.split())
    else:
        return False


# Получение изображения по полученным координатам
def get_map(lon_lat, delta="0.005"):
    map_params = {
        "ll": lon_lat,
        "spn": ",".join([delta, delta]),
        "l": 'map',
        "pt": lon_lat
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    return requests.get(map_api_server, params=map_params).content


# Удаоение записи
@app.route('/del_note/<int:note_id>')
def delete_note(note_id):
    # Создание сессии подключения к БД
    session = db_session.create_session()

    # Получение записи для удаления
    note = session.query(Notes).filter(Notes.id == note_id).first()
    if note and note.user_id == current_user.id:
        # Удаление
        session.delete(note)
        # Сохранение изменений
        session.commit()

    return redirect('/note')


# Изменение записей
@app.route('/edit_note/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    # Форма изменения записей
    form = EditNotesForm()

    # Отображение текущих данных в записи
    if request.method == 'GET':

        session = db_session.create_session()

        note = session.query(Notes).filter(Notes.id == note_id).first()

        if note and note.user_id == current_user.id:

            form.title.data = note.title
            form.body.data = note.body
            form.is_important.data = note.is_important
            if note.images is not None:
                form.current_image = '../' + note.images
            else:
                form.current_image = ''

        else:
            return redirect('/note')

    # POST
    if form.validate_on_submit():
        # Создание сессии подключения к БД
        session = db_session.create_session()
        # Получение записи
        note = session.query(Notes).filter(Notes.id == note_id).first()

        if note and note.user_id == current_user.id:
            image_path = ''
            place = form.place.data
            # Получение карты, если указан адрес
            if place:
                try:
                    lon_lat = get_coordinates(place)
                    image = get_map(lon_lat)
                    image_path = f'static/image/users_image/map{len(os.listdir("static/image/users_image"))}.png'
                    with open(image_path, 'wb') as file:
                        file.write(image)

                except Exception:
                    return render_template('edit_form.html', form=form, message='Не удалось получить карту,'
                                                                                ' проверьте корректность'
                                                                                ' введенных данных!')
            # Получение изображения, если оно было загружено
            elif form.image.data.filename:
                name, extension = form.image.data.filename.split(".")

                if extension not in ['jpg', 'png', 'jpeg', 'tif', 'bmp']:
                    return render_template('edit_form.html', form=form, message='Недопустимый формат файла!'
                                                                                ' Только ".jpg", ".png",'
                                                                                ' ".jpeg", ".tif", ".bmp"')

                image = form.image.data

                image_path = f'static/image/users_image/{name}{len(os.listdir("static/image/users_image"))}' \
                             f'.{extension}'

                image.save(image_path, len(os.listdir("static/image/users_image")))

            # Внесение изменений
            note.title = form.title.data
            note.body = form.body.data
            note.is_important = form.is_important.data
            note.user_id = current_user.id

            # Если есть новое изображение
            if image_path:
                note.images = image_path
            # Иначе сохранение старого
            else:
                note.images = note.images

            # Сохранение изменений
            session.commit()

            # Перенаправление на страницу с записями
            return redirect('/note')

    return render_template('edit_form.html', form=form)


# Изменение данных в профиле
@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    # Форма для изменения профиля
    form = ProfileForm()

    # Отображение текущих данных профиля
    if request.method == 'GET':
        # Создание сессии подключения к БД
        session = db_session.create_session()

        # Получение информации о пользователе
        user = session.query(Users).filter(Users.id == user_id).first()
        # Если не удалось получить пользователя
        # Или текущий пользователь хочет изменить данные другому пользователю
        if not user or current_user.id != user.id:
            # Страница не найдена
            return abort(404)

        # Добавление текущих данных в форму
        form.login.data = user.login
        form.email.data = user.email

        # Возврощение страницы с заполненной формой
        return render_template('profile.html', form=form)
    # POST
    if form.validate_on_submit():
        # Создание сессии подключения к БД
        session = db_session.create_session()

        # Получение информации о пользователе
        user = session.query(Users).filter(Users.id == user_id).first()
        # Если не удалось получить пользователя
        # Или текущий пользователь хочет изменить данные другому пользователю
        if not user or current_user.id != user.id:
            # Страница не найдена
            return abort(404)

        # Переменные для внесения изменений
        login = ''
        email = ''
        password = ''

        # Если данные в поле с логином не совпадают с текущим логином пользователя
        if user.login != form.login.data:
            # Проверка нового логина на уникальность
            if session.query(Users).filter(Users.login == form.login.data).first():
                # Сообщение об ошибке
                return render_template('profile.html', form=form,
                                       message='Пользователь с таким логином уже существует!')
            # Запись нового логина
            login = form.login.data
        # Если данные в поле с почтой не совпадают с текущей почтой пользователя
        if user.email != form.email.data:
            # Проверка новой почты на уникальность
            if session.query(Users).filter(Users.email == form.email.data).first():
                # Сообщение об ошибке
                return render_template('profile.html', form=form,
                                       message='Пользователь с такой почтой уже существует!')
            # Запись новой почты
            email = form.email.data

        # Если заполнены поля со старым паролем, новым и новым ещё раз
        if form.old_password.data and form.new_password.data and form.new_password_again.data:
            # Если текущий пароль не совпадает с введённым
            if not user.check_hashed_password(form.old_password.data):
                return render_template('profile.html', form=form, message='Неверный пароль!')
            # Если не совпадают новые пароли
            if form.new_password.data != form.new_password_again.data:
                return render_template('profile.html', form=form, message='Новые пароли не совпадают!')
            # Запись нового пароля
            password = form.new_password.data

        # Если изменён логин
        if login:
            user.login = login
        # Если изменена почта
        if email:
            user.email = email
        # Если изменён пароль
        if password:
            # Генерируем хешированный пароль
            user.generate_hashed_password(password)

        # Созранение изменений
        session.commit()

        return render_template('profile.html', form=form, message='Данные успешно изменены!')


# Поиск по записям
@app.route('/search_note', methods=['GET', 'POST'])
def search():
    # Форма поиска по записям
    form = SearchForm()

    # При загрузке страницы
    if request.method == 'GET':
        return render_template('search_form.html', form=form, message='По вашему запросу ничего не найдено!')

    # Поиск по записям
    if form.validate_on_submit():
        # Создание сессии подключения к БД
        session = db_session.create_session()
        # Текст поиска
        text = form.search.data
        # Поиск
        notes = session.query(Notes).filter(Notes.user_id == current_user.id, Notes.title.like(f'%{text}%'))
        # Если записок несколько - сортировка по важности
        notes = sorted(notes, key=lambda x: x.is_important, reverse=True)
        # Ничего не найдено
        if not notes:
            return render_template('search_form.html', form=form, message='По вашему запросу ничего не найдено!')
        # Возвращение записок, удовлетворяющих условию
        return render_template('search_form.html', form=form, notes=notes)


# Переводчик
@app.route('/translate', methods=['GET', 'POST'])
def translate():
    # Форма для перевода
    form = TranslateForm()

    # При загрузке страницы
    if request.method == 'GET':
        return render_template('translate_form.html', form=form)

    # Перевод
    if form.validate_on_submit():
        # С какого языка
        first_lang = form.first_language.data
        # На какой
        second_lang = form.second_language.data
        lang = '-'.join([first_lang, second_lang])
        # Текст перевода
        text = form.text_for_translate.data
        # Получение перевода
        result = yandex_translate(lang, text)
        # Если перевод корректен
        if result is not None:
            # Заполнение формы
            form.first_language.data = first_lang
            form.second_language.data = second_lang
            form.text_for_translate.data = text
            form.translated_text.data = result

            return render_template('translate_form.html', form=form)

        else:
            return render_template('translate_form.html', form=form, message='Не удалось выполнить перевод!')


# Перевод с помошью API Яндекс.Переводчика
def yandex_translate(lang, text):
    yandex_translate_api = 'https://translate.yandex.net/api/v1.5/tr.json/translate'

    params = {
        'key': YANDEX_TRANSLATE_TOKEN,
        'lang': lang,
        'text': text
    }

    try:
        json_response = requests.get(yandex_translate_api, params=params).json()
        return ' '.join(json_response['text'])
    except Exception:
        return None


# Выход пользователя
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


# Ошибка неавторизованного пользователя
@app.errorhandler(401)
def error_401(error):
    return '<h2 style="text-align:center;">Войдите, чтобы просмотреть записи!</h2>'


# Страница не найдена
@app.errorhandler(404)
def error_404(error):
    return '<h2 style="text-align:center;">Похоже, такой страницы не существует!</h2>'


# Ошибка на сервере
@app.errorhandler(500)
def error_500(error):
    return '<h2 style="text-align:center;">Oooppsss, произошла ошибка!</h2>'


# Запуск главной функции
if __name__ == '__main__':
    main()
