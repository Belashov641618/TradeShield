from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, BigInteger, Float, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy import DateTime


Base = declarative_base()


class Codes(Base):
    __tablename__ = "codes"
    __table_args__ = (UniqueConstraint('code_tn_ved', 'code_okpd2', name='uix_tnved_okpd2'),)
    id          = Column(Integer, primary_key=True)
    code_tn_ved = Column(BigInteger, nullable=False)
    name_tn_ved = Column(String, nullable=False)
    code_okpd2  = Column(String, nullable=False)
    name_okpd2  = Column(String, nullable=False)
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Goods(Base):
    __tablename__ = "goods"
    id                      = Column(Integer, primary_key=True)
    code_tn_ved             = Column(BigInteger, nullable=False)
    name_tn_ved             = Column(String, nullable=False)
    code_okpd2              = Column(String, nullable=False)
    name_okpd2              = Column(String, nullable=False)
    current_duty            = Column(Float)
    vto_duty                = Column(Float)
    in_pp_1875_group        = Column(Boolean)
    requires_certification  = Column(Boolean)
    excluded_order_4114     = Column(Boolean)
    imports                 = relationship("Import",        back_populates="good", cascade="all, delete-orphan")
    production              = relationship("Production",    back_populates="good", cascade="all, delete-orphan")
    consumption             = relationship("Consumption",   back_populates="good", cascade="all, delete-orphan")
    geographic              = relationship("Geographic",    back_populates="good", cascade="all, delete-orphan")
    updated_at              = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Import(Base):
    __tablename__ = "import"
    id          = Column(Integer, primary_key=True)
    good_id     = Column(Integer, ForeignKey("goods.id", ondelete="CASCADE"))
    year        = Column(Integer, nullable=False)
    month       = Column(Integer, nullable=False)
    volume      = Column(Float)
    unit        = Column(String)
    good        = relationship(Goods.__name__, back_populates="imports")
    updated_at  = Column(DateTime(timezone=True),  server_default=func.now(), onupdate=func.now())

class Production(Base):
    __tablename__ = "production"
    id          = Column(Integer, primary_key=True)
    good_id     = Column(Integer, ForeignKey("goods.id", ondelete="CASCADE"))
    year        = Column(Integer, nullable=False)
    month       = Column(Integer, nullable=False)
    volume      = Column(Float)
    unit        = Column(String)
    good        = relationship(Goods.__name__, back_populates="production")
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Consumption(Base):
    __tablename__ = "consumption"
    id          = Column(Integer, primary_key=True)
    good_id     = Column(Integer, ForeignKey("goods.id", ondelete="CASCADE"))
    year        = Column(Integer, nullable=False)
    month       = Column(Integer, nullable=False)
    volume      = Column(Float)
    unit        = Column(String)
    good        = relationship(Goods.__name__, back_populates="consumption")
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Countries(Base):
    __tablename__ = "countries"
    id              = Column(Integer, primary_key=True)
    iso2            = Column(String(2), nullable=False, unique=True)
    name            = Column(String, nullable=False)
    region          = Column(String)
    is_unfriendly   = Column(Boolean, default=False)
    updated_at      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Geographic(Base):
    __tablename__ = "geographic"
    id                  = Column(Integer, primary_key=True)
    good_id             = Column(Integer, ForeignKey("goods.id", ondelete="CASCADE"))
    country_id          = Column(Integer, ForeignKey("countries.id"), nullable=False)
    import_share        = Column(Float)
    avg_contract_price  = Column(Float)
    good                = relationship(Goods.__name__, back_populates="geographic")
    country             = relationship("Country")
    updated_at          = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
