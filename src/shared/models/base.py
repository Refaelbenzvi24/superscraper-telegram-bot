from pydantic import BaseModel


class SQLAlchemyBaseModel(BaseModel):
	class Config:
		orm_mode = True

