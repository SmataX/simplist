import os
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine, select

# if os.getenv("ENVIRONMENT") == "development":
#     DATABASE_URL = "sqlite:///./database.db"
# else:
#     DATABASE_URL = os.getenv("DATABASE_URL")

DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

SessionDep = Annotated[Session, Depends(get_session)]


class DBStorageHandler:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self, model_type: type[SQLModel]) -> list[SQLModel]:
        result = self.session.exec(select(model_type)).all()
        return list(result)
    
    def get_by_id(self, id: int, model_type: type[SQLModel]) -> SQLModel:
        db_model = self.session.get(model_type, id)
        if not db_model:
            return None
        return db_model
    
    def get_all_where(self, model_type: type[SQLModel], conditions) -> list[SQLModel]:
        result = self.session.exec(select(model_type).where(*conditions)).all()
        return list(result)

    def create(self, model: SQLModel) -> SQLModel:
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model

    def update(self, id: int, model: SQLModel) -> SQLModel:
        db_model = self.session.get(type(model), id)

        if not db_model:
            return None

        model_data = model.model_dump(exclude_unset=True)
        db_model.sqlmodel_update(model_data)
        self.session.add(db_model)
        self.session.commit()
        self.session.refresh(db_model)
        return db_model

    def delete(self, id: int, model_type: type[SQLModel]) -> None:
        db_model = self.get_by_id(id, model_type)

        if not db_model:
            raise ValueError(f"Model with id {id} not found")

        self.session.delete(db_model)
        self.session.commit()

def get_db_storage_handler(session: SessionDep) -> DBStorageHandler:
    return DBStorageHandler(session)


DBStorageHandlerDep = Annotated[DBStorageHandler, Depends(get_db_storage_handler)]