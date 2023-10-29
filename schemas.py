from pydantic import BaseModel, Field



class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str

class UserEdit(UserBase):
    password: str
    login: str

class UserCreate(UserBase):
    password: str
    login: str

class User(UserBase):
    username: str 
    isAdmin: bool 
    balance: int 
    login: str
    password: str

class AdminUserEdit(User):
    userId: int

class DeleteUser(BaseModel):
    userId: int

class Credentials(BaseModel):
    username: str
    password: str


class Cars(BaseModel):
    canBeRanted: bool
    model: str
    color: str
    identifier: str
    description: str
    latitube: int
    longitube: int
    minutePrice: int
    dayPrice: int
    transportType: str

class TransportEdit(BaseModel):
    transportId: int
    canBeRanted: bool
    model: str
    color: str
    identifier: str
    description: str
    latitube: int
    longitube: int
    minutePrice: int
    dayPrice: int

class TransportDelete(BaseModel):
    transportId: int

class PaymentController(BaseModel):
    userId: int

class AdminTransport(Cars):
    userId: int

class EditAdminTransport(TransportEdit):
    userId: int

class DeleteTransport(BaseModel):
    trasportId: int

class RentAll(BaseModel):
    lat: int
    long: int
    radius: int
    type: str

class GetRent(BaseModel):
    id: int

class Rent(DeleteTransport):
    rentType: str = Field(example='minutes | day')

class EndRent(BaseModel):
    rentId: int
    lat: int
    long: int

class adminRent(Rent):
    userId: int

class adminEditRent(adminRent):
    timeStart: str = Field(example='gggg-mm-dd h:m:s')
    timeEnd : str = Field(example='gggg-mm-dd h:m:s')
    priceOfUnit: int
    priceTupe: str
    finalPrice: int
    rentId: int