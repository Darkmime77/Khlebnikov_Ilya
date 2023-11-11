from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,Double,DateTime,Sequence
from database import Base


class Users(Base):
    __tablename__ = "Users"

    userId = Column(Integer, primary_key=True)
    is_auth = Column(Boolean, default=False)
    username = Column("username", String)
    isAdmin = Column("isAdmin", Boolean, nullable=True)
    balance = Column("balance", Integer, nullable=True)
    login = Column("login", String, nullable=True)
    password = Column("password", String, nullable=True)

class Transport(Base):
    __tablename__ = "Transport"

    transportId = Column(Integer, primary_key=True)
    canBeRanted = Column("canBeRented", Boolean, nullable=True)
    model = Column("model", String, nullable=True)
    color = Column("color", String, nullable=True)
    identifier = Column("identifier", String, nullable=True)
    description = Column("description", String)
    latitube = Column("latitube", Integer, nullable=True)
    longitube = Column("longitude", Integer, nullable=True)
    minutePrice = Column("minutePrice", Integer)
    dayPrice = Column("dayPrice", Integer)
    userId = Column("userId", Integer, ForeignKey("Users.userId"), nullable=True)
    transportType = Column("transportType", String)

class Rent(Base):
    __tablename__ = "Rent"

    rentId = Column(Integer, primary_key=True)
    userId = Column("userId", Integer, ForeignKey("Users.userId"), nullable=True)
    timeStart = Column("timeStart", DateTime, nullable=True)
    timeEnd = Column("timeEnd", DateTime)
    priceOfUnit = Column("priceOfUnit", Integer, nullable=True)
    priceType = Column("priceType", String, nullable=True)
    finalPrice = Column("finalPrice", Integer)
    transportId = Column("transportId", Integer, ForeignKey("Transport.transportId"))

