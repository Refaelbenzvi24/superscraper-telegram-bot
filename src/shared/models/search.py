import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, exists
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from ...config.database import Base, session


class SearchModel(Base):
	__tablename__ = "searches"
	
	id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
	search_text = Column(String, nullable=False, index=True, unique=True)
	
	subscription_association = relationship("Subscription", back_populates="search")
	subscribers = association_proxy("subscription_association", "subscriber")
	
	products_association = relationship("SearchProduct", back_populates="search")
	products = association_proxy("products_association", "search")


class Search(SearchModel):
	def __init__(self, search_text):
		self.search_text = search_text
	
	def exists(self):
		if self.search_text:
			return session.query(exists().where(Search.search_text == self.search_text)).scalar()
		
		if self.id:
			return session.query(exists().where(Search.id == self.id)).scalar()
	
	def get(self):
		if self.search_text:
			return session.query(Search).filter(Search.search_text == self.search_text).first()
		
		if self.id:
			return session.query(Search).filter(Search.id == self.id).first()
	
	def add(self):
		session.add(self)
	
	def commit(self):
		session.commit()
	
	def append_subscriber(self, user):
		self.subscribers.append(user)
	
	def __repr__(self):
		return f"<User (user_id='{self.id}', first_name='{self.first_name}', username='{self.username}')>"
