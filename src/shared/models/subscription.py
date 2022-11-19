import uuid
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Boolean, Integer, exists, DateTime, String
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import flag_modified
from ...config.database import Base, session


class SubscriptionModel(Base):
	__tablename__ = "subscriptions"
	
	id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
	
	user_id = Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'))
	search_id = Column('search_id', UUID(as_uuid=True), ForeignKey('searches.id'))
	
	subscriber = relationship('User', back_populates='search_association')
	search = relationship('Search', back_populates='subscription_association')
	
	date_created = Column('date_created', DateTime, default=datetime.utcnow)
	is_active = Column(Boolean, default=False)
	is_deleted = Column(Boolean, default=False)
	sizes = Column(ARRAY(String), default=[])


class Subscription(SubscriptionModel):
	def __init__(self, subscriber_id, search_id):
		self.user_id = subscriber_id or ""
		self.search_id = search_id or ""
	
	def add_size(self, size: int):
		subscription_in_db = self.get()
		if subscription_in_db and size not in subscription_in_db.sizes:
			subscription_in_db.sizes.append(size)
			flag_modified(subscription_in_db, "sizes")
			
			session.merge(subscription_in_db)
			session.flush()
			session.commit()
	
	def get(self):
		return session.query(Subscription).filter(Subscription.user_id == self.user_id, Subscription.search_id == self.search_id).first()
	
	def exists(self):
		return session.query(exists().where(Subscription.user_id == self.user_id, Subscription.search_id == self.search_id)).scalar()
	
	def add(self):
		session.add(self)
	
	def commit(self):
		session.commit()
	
	def __repr__(self):
		return f"<Subscription (subscriber_id='{self.user_id}', search_id='{self.search_id}')>"
