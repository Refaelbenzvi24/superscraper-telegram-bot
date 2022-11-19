import uuid

from sqlalchemy import Column, Integer, ForeignKey, exists, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import flag_modified
from ...config.database import Base, session


class UserSettingsModel(Base):
	__tablename__ = 'user_settings'
	
	id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
	user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
	user = relationship("User", back_populates="settings")
	
	current_editing_search_text = Column(String, default=None, nullable=True)


class UserSettings(UserSettingsModel):
	def __init__(self, user_id):
		self.user_id = user_id
	
	def __repr__(self):
		return f"<UserSettings (user_id='{self.user_id}')>"
	
	def get(self):
		return session.query(UserSettings).filter(UserSettings.user_id == self.user_id).first()
	
	def exists(self):
		return session.query(exists().where(UserSettings.user_id == self.user_id)).scalar()
	
	def add(self):
		session.add(self)
	
	def update_current_editing_search_text(self, search_text):
		user_settings_in_db = self.get()
		user_settings_in_db.current_editing_search_text = search_text
		flag_modified(user_settings_in_db, "current_editing_search_text")
		session.merge(user_settings_in_db)
		session.flush()
	
	def commit(self):
		session.commit()
