from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, BigInteger, Float, Boolean, ForeignKey, UniqueConstraint, DateTime, Index, func


Base = declarative_base()


class AbstractTable(Base):
    __abstract__ = True
    id        = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True))
    updated   = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    source    = Column(String, nullable=False)

class Codes(AbstractTable):
    __tablename__ = "codes"
    __table_args__ = (UniqueConstraint('code', 'code_okpd2', name='uix_tnved_okpd2'),)
    code       = Column(BigInteger, nullable=False)
    name       = Column(String, nullable=False)
    code_okpd2 = Column(String, nullable=False)
    name_okpd2 = Column(String, nullable=False)

class Countries(AbstractTable):
    __tablename__ = "countries"
    iso2       = Column(String(2), nullable=False, unique=True)
    name       = Column(String, nullable=True)
    region     = Column(String, nullable=True)
    unfriendly = Column(Boolean, default=False)
    metrics = relationship("GoodsMetrics", back_populates="country", cascade="all, delete-orphan")

class Goods(AbstractTable):
    __tablename__ = "goods"
    code = Column(BigInteger, unique=True, nullable=False)
    name = Column(String, nullable=False)
    metrics  = relationship("GoodsMetrics", back_populates="good", cascade="all, delete-orphan")
    requests = relationship("Requests", back_populates="good", cascade="all, delete-orphan")
    rarities = relationship("Rarities", back_populates="good", cascade="all, delete-orphan")
    @classmethod
    def by_code(cls, session, code: int) -> Goods:
        return session.query(cls).filter_by(code=code).first()
    def get_metric(self, name:str, country:Optional[str]=None, latest:bool=True) -> tuple[Optional[GoodsMetrics],str]:
        metric_obj = self.metrics.session.query(Metrics).filter_by(name=name).first()
        if not metric_obj: return None, f"Метрика '{name}' отсутствует в справочнике Metrics"
        query = self.metrics.filter(GoodsMetrics.metric_id == metric_obj.id)
        if country: query = query.join(GoodsMetrics.country).filter(Countries.iso2 == country)
        if latest: query = query.order_by(GoodsMetrics.timestamp.desc())
        gm = query.first()
        if not gm: return None, f"Для метрики '{metric_obj.full_name}' отсутствуют данные"
        return gm, "ok"

class Metrics(AbstractTable):
    __tablename__ = "metrics"
    name        = Column(String, nullable=False, unique=True)
    full_name   = Column(String, nullable=False, unique=True)
    unit        = Column(String, nullable=False)
    goods_metrics = relationship("GoodsMetrics", back_populates="metric", cascade="all, delete-orphan")

class GoodsMetrics(AbstractTable):
    __tablename__ = "goods_metrics"
    __table_args__ = (
        UniqueConstraint('good_id', 'metric_id', 'country_id', 'timestamp', name='uix_good_metric_country_time'),
        Index('ix_goods_metrics_good_metric_time', 'good_id', 'metric_id', 'timestamp')
    )
    good_id     = Column(Integer, ForeignKey("goods.id", ondelete="CASCADE"), nullable=False)
    metric_id   = Column(Integer, ForeignKey("metrics.id", ondelete="CASCADE"), nullable=False)
    country_id  = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), nullable=True)
    value_float = Column(Float, nullable=True)
    value_int   = Column(Integer, nullable=True)
    value_bool  = Column(Boolean, nullable=True)
    value_str   = Column(String, nullable=True)
    country = relationship("Countries", back_populates="metrics")
    metric  = relationship("Metrics", back_populates="goods_metrics")
    good    = relationship("Goods", back_populates="metrics")
    @property
    def value(self):
        for v in (self.value_float, self.value_int, self.value_bool, self.value_str):
            if v is not None:
                return v
        return None
    @value.setter
    def value(self, v):
        self.value_float = self.value_int = self.value_bool = self.value_str = None
        if isinstance(v, float):    self.value_float = v
        elif isinstance(v, int):    self.value_int = v
        elif isinstance(v, bool):   self.value_bool = v
        elif isinstance(v, str):    self.value_str = v
        else: raise ValueError(f"Unsupported type: {type(v)}")

class Requests(AbstractTable):
    __tablename__ = "requests"
    good_id = Column(Integer, ForeignKey("goods.id", ondelete="CASCADE"), nullable=False)
    inn     = Column(BigInteger, nullable=False)
    good    = relationship("Goods", back_populates="requests")

class Rarities(AbstractTable):
    __tablename__ = "rarities"
    good_id     = Column(Integer, ForeignKey("goods.id", ondelete="CASCADE"), nullable=False)
    amplitude   = Column(Float, nullable=False)
    attenuation = Column(Float, nullable=False)
    good        = relationship("Goods", back_populates="rarities")
