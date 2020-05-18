import sqlalchemy as alchemy
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as declarative

# База для наслевания моделей
SqlAlchemyBase = declarative.declarative_base()

# Для получения сесий подключения к БД
__factory = None


def global_init(db_file):
    global __factory

    # Если инициализация уже проводилась
    if __factory:
        return

    # Если нет файла БД
    if not db_file.strip():
        raise Exception('Укажите файл базы данных!')

    # Путь подключения
    connection_path = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f'Подключение к базе данных по адресу {connection_path}')

    # Движок для работы с БД
    engine = alchemy.create_engine(connection_path, echo=False)
    # Создаём фабрику подключений
    __factory = orm.sessionmaker(bind=engine)

    # Импортируем все модели
    from . import __all_models
    # Создаём всё, что не создано
    SqlAlchemyBase.metadata.create_all(engine)


# Получение сессий подключения к БД
def create_session() -> Session:
    global __factory
    return __factory()
