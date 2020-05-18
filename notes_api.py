from flask import Blueprint, jsonify
from data import db_session
from data.users import Users
from data.notes import Notes

blueprint = Blueprint('notes_api', __name__, template_folder='templates')


# Вход пользователя
@blueprint.route('/api/login_user/<user_login>/<password>', methods=['GET'])
def login_user(user_login, password):
    # Создание сессии подключения к БД
    session = db_session.create_session()

    user = session.query(Users).filter(Users.login == user_login).first()
    if user and user.check_hashed_password(password):
        return jsonify({'success': f'{user.id}'})  # json-ответ
    return jsonify({'error': 'Не удалось выполнить вход!'})  # json-ответ


# Получение всех записей пользователя
@blueprint.route('/api/all_notes/<int:user_id>', methods=['GET'])
def get_all_notes(user_id):
    # Создание сессии подключения к БД
    session = db_session.create_session()
    # Получение пользователя по id
    user = session.query(Users).get(user_id)
    if not user:
        return jsonify({'error': 'Пользователь не найден!'})  # json-ответ
    # Получение записей пользователя
    notes = session.query(Notes).filter(Notes.user_id == user.id)

    if not notes:
        return jsonify({'error': 'Записи не найдены!'})  # json-ответ

    return jsonify({
        'notes': [item.to_dict(only=('title',)) for item in notes]
    })  # json-ответ


# Получение записи по заголовку
@blueprint.route('/api/get_note/<int:user_id>/<notes_title>', methods=['GET'])
def get_note(user_id, notes_title):
    # Создание сессии подключения к БД
    session = db_session.create_session()
    # Получение пользователя по id
    user = session.query(Users).get(user_id)
    if not user:
        return jsonify({'error': 'Пользователь не найден!'})  # json-ответ
    # Получение записи
    note = session.query(Notes).filter(Notes.user_id == user_id, Notes.title == notes_title).first()

    if not note:
        return jsonify({'error': 'Запись не найдена!'})  # json-ответ

    return jsonify({'note': note.to_dict(only=('title', 'body', 'is_important'))})  # json-ответ
