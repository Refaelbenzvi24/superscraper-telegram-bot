import uuid

from sqlalchemy import Column, ForeignKey, exists
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ...config.database import Base, session


class SearchProduct(Base):
	__tablename__ = 'search_products'
	
	id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
	
	search_id = Column("search_id", UUID(as_uuid=True), ForeignKey('searches.id'))
	product_id = Column("product_id", UUID(as_uuid=True), ForeignKey('products.id'))
	
	search = relationship("Search", back_populates="products_association")
	product = relationship("Product", back_populates="searches_association")
	
	def __init__(self, search_id, product_id):
		self.search_id = search_id
		self.product_id = product_id
	
	def get(self):
		return session.query(SearchProduct).filter(SearchProduct.search_id == self.search_id, SearchProduct.product_id == self.product_id).first()
	
	def exists(self):
		return session.query(exists().where(SearchProduct.search_id == self.search_id, SearchProduct.product_id == self.product_id)).scalar()
	
	def add(self):
		session.add(self)
	
	def commit(self):
		session.commit()
