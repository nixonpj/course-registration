from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from singleton import singleton


@singleton
class Database:
    def __init__(self):
        self._engine = create_engine('mysql+mysqlconnector://root:root@localhost:3306/regie', echo=True)
        self._Session = sessionmaker(bind=self._engine)
        self._db_session = self._Session()
        self._Base = declarative_base()

    def get_session(self):
        return self._db_session

    def get_base(self):
        return self._Base

