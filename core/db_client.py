import os
import psycopg2
from psycopg2.extras import execute_values
from core.logger import Logger

class DBClient:
    def __init__(self, name="DBClient"):
        self._logger = Logger(name).get_logger()
        self._connection = psycopg2.connect(
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD'),
            host=os.getenv('PG_HOST'),
            port=os.getenv('PG_PORT'),
            database=os.getenv('PG_DBNAME')              
        )
        self._cursor = self._connection.cursor()
        self._table = 'positions'
        self._connection.autocommit = True

    def _table_exists(self):
        query = f'''
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = '{self._table}'
        )
        '''
        self._cursor.execute(query)
        return self._cursor.fetchone()[0]
    
    def create_table(self):
        if self._table_exists():
            log_message = f'Таблица {self._table} уже существует'
        else:
            query = f'''
            CREATE TABLE IF NOT EXISTS {self._table} (
                "name" text NULL,
                brand text NULL,
	            "position" int4 NULL,
	            price int4 NULL,
	            created_at timestamp NULL,
	            query text NULL,
	            city text NULL
            )'''
            self._cursor.execute(query)
            log_message = f'Таблица {self._table} создана'
        self._logger.info(log_message)

    def _get_row_count(self):
        self._cursor.execute(f'SELECT COUNT(*) FROM {self._table}')
        return self._cursor.fetchone()[0]
    
    def insert_data(self, data):
        if not data:
            self._logger.warning('Данных для вставки не найдено')
            return

        values = [(
            row[0], row[1], row[2],
            row[3], row[4], row[5], row[6]
        ) for row in data]

        query = f'''
        INSERT INTO {self._table} (name, brand, position, price, 
        created_at, query, city)
        VALUES %s 
        '''

        try:
            previous_table_size = self._get_row_count()

            psycopg2.extras.execute_values(self._cursor, query, values)

            new_table_size = self._get_row_count()
            new_rows_count = new_table_size - previous_table_size

            self._logger.info(f'В таблицу {self._table} добавлено {new_rows_count} новых строк')
        except Exception as ex:
            self._connection.rollback()
            self._logger.error(f'Ошибка при добавлении данных: {ex}')
    
    def close_connection(self):
        self._cursor.close()
        self._connection.close()
        self._logger.info('Соединение с базой данных закрыто')
    