# src/common/db_storage.py

import os
from typing import Annotated, TypeVar, Generic
from collections.abc import Generator

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import ColumnElement

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)

def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

SessionDep = Annotated[Session, Depends(get_session)]


T = TypeVar("T", bound=SQLModel)

class DBStorageHandler(Generic[T]):
    def __init__(self, session: Session):
        self.session = session

    def get_all(self, model_type: type[T]) -> list[T]:
        return list(self.session.exec(select(model_type)).all())
    
    def get_by_id(self, id: int, model_type: type[T]) -> T:
        db_model = self.session.get(model_type, id)
        if not db_model:
            raise ValueError(f"{model_type.__name__} with id {id} not found")
        return db_model
    
    def get_all_where(self, model_type: type[T], *conditions: ColumnElement) -> list[T]:
        stmt = select(model_type).where(*conditions)
        return list(self.session.exec(stmt).all())

    def create(self, model: T) -> T:
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model

    def update(self, id: int, model_type: type[T], updates: dict) -> T:
        db_model = self.session.get(model_type, id)
        if not db_model:
            raise ValueError(f"{model_type.__name__} with id {id} not found")

        for key, value in updates.items():
            setattr(db_model, key, value)

        self.session.add(db_model)
        self.session.commit()
        self.session.refresh(db_model)
        return db_model

    def delete(self, id: int, model_type: type[T]) -> None:
        db_model = self.get_by_id(id, model_type)
        self.session.delete(db_model)
        self.session.commit()


# Dependency
def get_storage(session: SessionDep) -> DBStorageHandler:
    return DBStorageHandler(session)

StorageDep = Annotated[DBStorageHandler, Depends(get_storage)]
