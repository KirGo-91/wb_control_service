import os
from datetime import datetime
from dotenv import load_dotenv
from core.api_client import ApiClient
from core.db_client import DBClient
from core.logger import Logger

class App:
    def __init__(self):
        """
        Инициализация приложения: загрузка конфигов, настройка логера,
        создание клиентов API и БД.
        """
        load_dotenv(dotenv_path='.env')
        self._project_name = os.path.basename(os.getcwd())
        self._logger = Logger('App').get_logger()
        self._api_client = ApiClient()
        self._db_client = DBClient()

    def run(self):
        """
        Запуск основного процесса:
        - Создание таблицы в БД,
        - Получение и вставка данных,
        - Логирование временных меток и ошибок,
        - Окончательное закрытие соединения с БД.
        """
        start_time = datetime.now()
        self._logger.info(f'Запуск работы «{self._project_name}»')
        try:
            self._db_client.create_table()
            data = self._api_client.get_data()
            self._db_client.insert_data(data=data)
        except Exception as ex:
            self._logger.error(f'Возникла ошибка: {ex}. Завершение работы')
        finally:
            try:
                self._db_client.close_connection()
            except Exception as close_ex:
                self._logger.error(f'Ошибка при закрытии соединения: {close_ex}')
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            self._logger.info(f'Завершение работы «{self._project_name}»')
            self._logger.info(f'Загрузка завершена за {duration:.2f} секунд')
            self._logger.info('=' * 70 + '\n')