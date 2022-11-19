import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, Boolean, exists
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from ...config.database import Base, session
from ...shared.models.userSettings import UserSettings


class UserModel(Base):
	__tablename__ = "users"
	
	id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
	telegram_id = Column(Integer, index=True, unique=True, nullable=False)
	first_name = Column(String, nullable=False)
	last_name = Column(String, nullable=False)
	
	disabled = Column(Boolean, default=False)
	is_authenticated = Column(Boolean, default=False)
	incorrect_password_attempts = Column(Integer, default=0)
	
	search_association = relationship("Subscription", back_populates="subscriber")
	searches = association_proxy("search_association", "search")
	
	settings = relationship("UserSettings", uselist=False, back_populates="user")


class User(UserModel):
	def __init__(self, user):
		self.telegram_id = user.id
		self.first_name = user.first_name
		self.last_name = user.last_name
	
	def get(self):
		if self.telegram_id:
			return session.query(User).filter(User.telegram_id == self.telegram_id).first()
		
		if self.id:
			return session.query(User).filter(User.id == self.id).first()
	
	def exists(self):
		if self.telegram_id:
			return session.query(exists().where(User.telegram_id == self.telegram_id)).scalar()
		
		if self.id:
			return session.query(exists().where(User.id == self.id)).scalar()
	
	def add(self):
		session.add(self)
		session.commit()
		user_in_db = self.get()
		user_settings = UserSettings(user_in_db.id)
		user_settings.add()
		session.commit()
	
	def commit(self):
		session.commit()
	
	def append_search(self, search):
		self.searches.append(search)
	
	def __repr__(self):
		return f"<User (user_id='{self.id}', first_name='{self.first_name}', last_name='{self.last_name}')>"
