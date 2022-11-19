import uuid
from datetime import datetime, timedelta

from sqlalchemy import Column, String, Float, DateTime, Boolean, exists
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from ...config.database import Base, session
from ...config.vars import SEARCH_INTERVAL_IN_MINUTES


class Product(Base):
	__tablename__ = 'products'
	
	id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
	title = Column(String)
	price = Column(Float)
	link = Column(String, unique=True)
	image_url = Column(String, nullable=True)
	available_sizes = Column(ARRAY(String), default=[])
	
	searches_association = relationship("SearchProduct", back_populates="product")
	searches = association_proxy("searches_association", "search")
	
	last_updated = Column(DateTime, default=datetime.utcnow)
	created_at = Column("created_at", DateTime, default=datetime.utcnow)
	
	@hybrid_property
	def currently_on_website(self):
		return self.last_updated > datetime.utcnow() - timedelta(minutes=SEARCH_INTERVAL_IN_MINUTES + 1)
	
	def __init__(
			self,
			title: str,
			price: str,
			link: str,
			image_url: str,
			available_sizes: [str],
			last_updated=datetime.utcnow()
	):
		self.title = title
		self.price = price
		self.link = link
		self.image_url = image_url
		self.available_sizes = available_sizes
		self.last_updated = last_updated
	
	def get(self):
		return session.query(Product).filter(Product.link == self.link).first()
	
	def exists(self):
		return session.query(exists().where(Product.link == self.link)).scalar()
	
	def add(self):
		session.add(self)
	
	def commit(self):
		session.commit()
