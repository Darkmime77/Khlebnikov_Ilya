from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models, schemas, datetime, math
from database import get_db, engine
from fastapi import Depends, FastAPI, HTTPException
from auth import AuthHandler

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

auth_handler = AuthHandler()

# # AccountController
# авторизация и выдача JWT токена
@app.post("/api/Account/login")
async def user_login(user_input: schemas.Credentials, db: Session = Depends(get_db)):
    user_db = (
        db.query(models.Users).filter(models.Users.login == user_input.username).first()
    )
    if not user_db:
        raise HTTPException(404, "Не верный логин")
    if auth_handler.verify_password(user_input.password, user_db.password):
        # token = auth_handler.encode_token(user_db.username)
        userId = (
        db.query(models.Users.userId).filter(models.Users.login == user_input.username).scalar()
        )
        token = auth_handler.encode_token(userId)
        db.query(models.Users).filter(
            models.Users.username == user_input.username
        ).update(
            {
                "is_auth": True,
            }
        )
        db.commit()
        return {"token": token}
    else:
        raise HTTPException(403, "Не верный пароль")


@app.get("/api/Account/Me")
async def me_user(
    userId=Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)
):
    User = db.query(models.Users).filter(models.Users.userId == userId).first()
    return User


@app.post("/api/Account/SignIn")
async def new_jwt(userId=Depends(auth_handler.auth_wrapper)):
    token = auth_handler.encode_token(userId)
    return {"token": token}


@app.post("/api/Account/SignUp")
async def register_user(user_input: schemas.UserCreate, db: Session = Depends(get_db)):
    user_db = (
        db.query(models.Users).filter(models.Users.login == user_input.login).first()
    )
    if user_db:
        raise HTTPException(400, "Такой логин уже существует")
    hash_pass = auth_handler.get_password_hash(user_input.password)
    admin = db.query(models.Users).all()
    if not admin:
        isAdmin = True
    else:
        isAdmin = False
    user_db = models.Users(
        username=user_input.username,
        password=hash_pass,
        isAdmin=isAdmin,
        balance=0,
        login=user_input.login,
    )
    db.add(user_db)
    db.commit()
    return "Успешно"


@app.post("/api/Account/SignOut")
async def black_list_JWT(
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    db.query(models.Users).filter(models.Users.userId == userId).update(
        {
            "is_auth": False,
        }
    )
    db.commit()
    return {"Вы вышли из аккаунта"}


@app.put("/api/Account/Update")
async def User_Edit(
    user_input: schemas.UserEdit,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = (
        db.query(models.Users).filter(models.Users.userId == userId).first()
    )
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    if user_db:
        if user_db.userId != userId:
            raise HTTPException(400, "Такой логин уже существует")
    db.query(models.Users).filter(models.Users.userId == userId).update(
        {
            "login": user_input.login,
            "password": auth_handler.get_password_hash(user_input.password),
            "username": user_input.username,
            "is_auth": False,
        }
    )
    db.commit()
    return "Успешно"


# TransportController
@app.get("/api/Transport/{id}")
async def get_Car(transportId: int, db: Session = Depends(get_db)):
    Car = db.query(models.Transport).get(transportId)
    if not Car:
        raise HTTPException(400, "Не верный аунтификатор")
    return Car


@app.post("/api/Transport")
async def register_car(
    car_input: schemas.Cars,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    car_db = models.Transport(
        canBeRanted=car_input.canBeRanted,
        model=car_input.model,
        color=car_input.color,
        identifier=car_input.identifier,
        description=car_input.description,
        latitube=car_input.latitube,
        longitube=car_input.longitube,
        minutePrice=car_input.minutePrice,
        dayPrice=car_input.dayPrice,
        userId=userId,
        transportType=car_input.transportType,
    )
    db.add(car_db)
    db.commit()
    return "Успешно"


@app.put("/api/Transport/{id}")
async def transport_edit(
    Transport_input: schemas.TransportEdit,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    Car_db = (
        db.query(models.Transport)
        .filter(models.Transport.transportId == Transport_input.transportId)
        .first()
    )
    if not Car_db:
        raise HTTPException(404, "Не верный идентификатор")
    if Car_db.userId == userId:
        db.query(models.Transport).filter(
            models.Transport.transportId == Car_db.transportId
        ).update(
            {
                "canBeRanted": Transport_input.canBeRanted,
                "model": Transport_input.model,
                "color": Transport_input.color,
                "identifier": Transport_input.identifier,
                "description": Transport_input.description,
                "latitube": Transport_input.latitube,
                "longitube": Transport_input.longitube,
                "minutePrice": Transport_input.minutePrice,
                "dayPrice": Transport_input.dayPrice,
            }
        )
        db.commit()
        return "Успешно"
    else:
        return HTTPException(403, "Авто вам не принадлежит")


@app.delete("/api/Transport/{id}")
async def transport_delete(
    Transport_input: schemas.TransportDelete,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    Car_db = (
        db.query(models.Transport)
        .filter(models.Transport.transportId == Transport_input.transportId)
        .first()
    )
    if not Car_db:
        raise HTTPException(404, "Не верный идентификатор")
    if Car_db.userId == userId:
        db.delete(Car_db)
        db.commit()
        return "Успешно"
    else:
        return HTTPException(403, "Авто вам не принадлежит")


# RentController
@app.get("/api/Rent/Transport")
async def get_rent_all(
    lat: int,
    long: int,
    radius: int,
    type: str,
    db: Session = Depends(get_db),
):
    Rent_db = db.query(models.Transport).all()
    list_car = []
    for i in Rent_db:
        if math.sqrt((i.latitube - lat)**2 + (i.longitube - long)**2) <= radius and i.canBeRanted == True and i.transportType == type:
            list_car.append(i)
    return list_car

@app.get("/api/Rent/{rentId}")
async def get_rent(rentId: int,
userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    Rent_db = db.get(models.Rent, rentId)
    if not Rent_db:
        raise HTTPException(404, "Не верный идентификатор")
    Transport_db = db.get(models.Transport, Rent_db.transportId)
    if Rent_db.userId == user_db.userId:
        return Rent_db
    elif Transport_db.userId == user_db.userId:
        return Rent_db
    else:
        return "Вы не арендатор и не владелец машины!"


@app.get("/api/Rent./Myhistory")
async def history_rent(
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    rent = db.query(models.Rent).filter(models.Rent.userId == userId).all()
    return rent


@app.get("/api/Rent/TransportHistory/{transportId}")
async def history_rent_car(
    trasportId: int,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    transport_db = (
        db.query(models.Transport)
        .filter(models.Transport.transportId == trasportId)
        .first()
    )
    if not transport_db:
        raise HTTPException(400, "Не верно указан идентификатор")
    if transport_db.userId == user_db.userId:
        rent = (
            db.query(models.Rent)
            .filter(models.Rent.transportId == trasportId)
            .all()
        )
        return rent
    else:
        return "Вы не владелец транспорта!"


@app.post("/api/Rent/New/{transportId}")
async def new_rent(
    rent_input: schemas.Rent,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    transport_db = db.get(models.Transport, rent_input.trasportId)
    if transport_db.canBeRanted == False:
        raise HTTPException(400,"Транспорт не доступен для аренды!")
    if transport_db.userId == user_db.userId:
        raise HTTPException(400,"Нельзя арендовывать свой собственный автомобиль!")
    if rent_input.rentType == "minutes":
        rentUnit = transport_db.minutePrice
    elif rent_input.rentType == "day":
        rentUnit = transport_db.dayPrice
    else:
        raise HTTPException(400,"Не верно выбран тип аренды, впишите 1 из следующих вариантов minutes | day")
    car_db = models.Rent(
        userId=user_db.userId,
        timeStart=datetime.datetime.now(),
        priceOfUnit=rentUnit,
        priceType=rent_input.rentType,
        transportId=rent_input.trasportId,
    )
    db.add(car_db)
    db.query(models.Transport).filter(
        models.Transport.transportId == rent_input.trasportId
    ).update({"canBeRanted": False})
    db.commit()
    return "Аренда оформлена"


@app.post("/api/Rent/End/{rentId}")
async def end_rent(
    rent_input: schemas.EndRent,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    rent_db = db.get(models.Rent, rent_input.rentId)
    if rent_db.userId != user_db.userId:
        raise HTTPException(400,"Вы не арендуете данный транспорт!")
    data = datetime.datetime.now() - rent_db.timeStart
    if rent_db.priceType == "minutes":
        price = data.total_seconds() / 60
    elif rent_db.priceType == "day":
        price = data.days

    db.query(models.Rent).filter(models.Rent.rentId == rent_input.rentId).update(
        {"timeEnd": datetime.datetime.now(), "finalPrice": round(price * rent_db.priceOfUnit,2)+rent_db.priceOfUnit}
    )
    db.query(models.Transport).filter(
        models.Transport.transportId == rent_db.transportId
    ).update(
        {
            "latitube": rent_input.lat,
            "longitube": rent_input.long,
            "canBeRanted": True
        }
    )
    db.commit()
    return "Аренда закончена"


# PaymentController
@app.post("/api/Payment/Hesoyam/{accountId}")
async def Payment_Controller(
    Payment_input: schemas.PaymentController,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    user_db = db.get(models.Users, Payment_input.userId)
    if not user_db:
        raise HTTPException(404, "Не верный идентификатор")
    if user_db.userId == userId:
        db.query(models.Users).filter(models.Users.userId == user_db.userId).update(
            {"balance": user_db.balance + 250000}
        )
        db.commit()
        return "Успешно"
    else:
        isadmin = db.get(models.Users, userId)
        if isadmin.isAdmin == True:
            db.query(models.Users).filter(models.Users.userId == user_db.userId).update(
                {"balance": user_db.balance + 250000}
            )
            db.commit()
            return "Успешно"
        else:
            return "Вы не администратор!"


# AdminAccountController
@app.get("/api/Admin/Account")
def admin_get_Users(
    userId=Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    isadmin = db.get(models.Users, userId)
    if isadmin.isAdmin == True:
        return db.query(models.Users).all()
    else:
        return "Вы не администратор!"


@app.get("/api/Admin/Account/{id}")
def admin_get_User(
    userId: int,
    userId_ad=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId_ad).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    isadmin = db.get(models.Users, userId_ad)
    if isadmin.isAdmin == True:
        return db.get(models.Users, userId)
    else:
        return "Вы не администратор!"


@app.post("/api/Admin/Account")
def adm_register_user(
    user_input: schemas.UserCreate,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    isadmin = db.get(models.Users, userId)
    if isadmin.isAdmin == True:
        user_db = (
            db.query(models.Users)
            .filter(models.Users.login == user_input.login)
            .first()
        )
        if user_db:
            raise HTTPException(400, "Такой логин уже существует")
        hash_pass = auth_handler.get_password_hash(user_input.password)
        user_db = models.Users(
            username=user_input.username,
            password=hash_pass,
            isAdmin=user_input.isAdmin,
            balance=0,
            login=user_input.login,
        )
        db.add(user_db)
        db.commit()
        return user_db
    else:
        return "Вы не администратор!"


@app.put("/api/Admin/Account/{id}")
async def Admin_User_Edit(
    user_input: schemas.AdminUserEdit,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    isadmin = db.get(models.Users, userId)
    if isadmin.isAdmin == True:
        user_db = (
            db.query(models.Users)
            .filter(models.Users.login == user_input.login)
            .first()
        )
        if user_db:
            if user_db.userId != user_input.userId:
                raise HTTPException(400, "Такой логин уже существует")
        db.query(models.Users).filter(models.Users.userId == user_input.userId).update(
            {
                "isAdmin": user_input.isAdmin,
                "login": user_input.login,
                "username": user_input.username,
                "password": auth_handler.get_password_hash(user_input.password),
                "balance": user_input.balance,
                "is_auth": False,
            }
        )
        db.commit()
        return "Успешно"
    else:
        return "Вы не администратор!"


@app.delete("/api/Admin/Account/{id}")
async def Admin_User_delete(
    User_input: schemas.DeleteUser,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    isadmin = db.get(models.Users, userId)
    if isadmin.isAdmin == True:
        User_db = (
            db.query(models.Users)
            .filter(models.Users.userId == User_input.userId)
            .first()
        )
        if not User_db:
            raise HTTPException(404, "Не верный идентификатор")
        db.delete(User_db)
        db.commit()
        return "Успешно"
    else:
        return "Вы не администратор!"


# AdminTranstorController
@app.get("/api/Admin/Transport")
async def Admin_get_Cars(
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    isadmin = db.get(models.Users, userId)
    if isadmin.isAdmin == True:
        Cars = db.query(models.Transport).all()
        return Cars
    else:
        return "Вы не администратор!"


@app.get("/api/Admin/Transport/{id}")
async def Admin_get_Car(
    transportId: int,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    isadmin = db.get(models.Users, userId)
    if isadmin.isAdmin == True:
        Car = db.query(models.Transport).get(transportId)
        return Car
    else:
        return "Вы не администратор!"


@app.post("/api/Admin/Transport")
async def Admin_Creat_Transport(
    car_input: schemas.AdminTransport,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    isadmin = db.get(models.Users, userId)
    if isadmin.isAdmin == True:
        User_db = db.query(models.Users).get(car_input.userId)
        if not User_db:
            raise HTTPException(404, "Не верный идентификатор пользователя")
        car_db = models.Transport(
            canBeRanted=car_input.canBeRanted,
            model=car_input.model,
            color=car_input.color,
            identifier=car_input.identifier,
            description=car_input.description,
            latitube=car_input.latitube,
            longitube=car_input.longitube,
            minutePrice=car_input.minutePrice,
            dayPrice=car_input.dayPrice,
            userId=car_input.userId,
            transportType=car_input.transportType,
        )
        db.add(car_db)
        db.commit()
        return "Успешно"
    else:
        return "Вы не администратор!"


@app.put("/api/Admin/Transport/{id}")
async def Admin_Transport_Edit(
    car_input: schemas.EditAdminTransport,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    isadmin = db.get(models.Users, userId)
    if isadmin.isAdmin == True:
        Car_db = (
            db.query(models.Transport)
            .filter(models.Transport.transportId == car_input.transportId)
            .first()
        )
        if not Car_db:
            raise HTTPException(404, "Не верный идентификатор машины")
        User_db = db.query(models.Users).get(car_input.userId)
        if not User_db:
            raise HTTPException(404, "Не верный идентификатор пользователя")
        db.query(models.Transport).filter(
            models.Transport.transportId == car_input.transportId
        ).update(
            {
                "userId": car_input.userId,
                "canBeRanted": car_input.canBeRanted,
                "model": car_input.model,
                "color": car_input.color,
                "identifier": car_input.identifier,
                "description": car_input.description,
                "latitube": car_input.latitube,
                "longitube": car_input.longitube,
                "minutePrice": car_input.minutePrice,
                "dayPrice": car_input.dayPrice,
            }
        )
        db.commit()
        return "Успешно"
    else:
        return "Вы не администратор!"


@app.delete("/api/Admin/Transport/{id}")
async def Admin_Transport_delete(
    Transport_input: schemas.DeleteTransport,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    isadmin = db.get(models.Users, userId)
    if isadmin.isAdmin == True:
        Car_db = (
            db.query(models.Transport)
            .filter(models.Transport.transportId == Transport_input.trasportId)
            .first()
        )
        if not Car_db:
            raise HTTPException(404, "Не верный идентификатор машины")
        db.delete(Car_db)
        db.commit()
        return "Успешно"
    else:
        return "Вы не администратор!"


# AdminRentControlle
@app.get("/api/Admin/Rent/{rentId}")
async def admin_get_rent(
    rentId: int,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    isadmin = db.get(models.Users, userId)
    if isadmin.isAdmin == True:
        rent_db = db.get(models.Rent, rentId)
        return rent_db
    else:
        return "Вы не администратор!"

@app.get("/api/Admin/UserHistory/{userId}")
async def admin_history_rent(userId: int,
    userId_ad=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId_ad).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    isadmin = db.get(models.Users, userId_ad)
    if isadmin.isAdmin == True:
        rent = db.query(models.Rent).filter(models.Rent.userId == userId).all()
        return rent
    else:
        return "Вы не администратор!"


@app.get("/api/Admin/TransportHistory/{transportId}")
async def admin_history_rent_car(
    transportId : int,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    isadmin = db.get(models.Users, userId)
    if isadmin.isAdmin == True:
        rent = db.query(models.Rent).filter(models.Rent.transportId == transportId).all()
        return rent
    else:
        return "Вы не администратор!"


@app.post("/api/Admin/Rent")
async def admin_new_rent(
    rent_input: schemas.adminRent,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    transport_db = db.get(models.Transport, rent_input.trasportId)
    user_db_test = db.get(models.Users,rent_input.userId)
    if not user_db_test:
        raise HTTPException(400,"Не верный идентификатор пользователя!")
    if transport_db.canBeRanted == False:
        raise HTTPException(400,"Транспорт не доступен для аренды!")
    isadmin = db.get(models.Users, userId)
    if isadmin.isAdmin == True:
        if rent_input.rentType == "minutes":
            rentUnit = transport_db.minutePrice
        elif rent_input.rentType == "day":
            rentUnit = transport_db.dayPrice
        else:
            raise HTTPException(400,"Не верно выбран тип аренды, впишите 1 из следующих вариантов minutes | day")
        car_db = models.Rent(
            userId=rent_input.userId,
            timeStart=datetime.datetime.now(),
            priceOfUnit=rentUnit,
            priceType=rent_input.rentType,
            transportId=rent_input.trasportId,
        )
        db.add(car_db)
        db.query(models.Transport).filter(
            models.Transport.transportId == rent_input.trasportId
        ).update({"canBeRanted": False})
        db.commit()
        return "Аренда оформлена"
    else:
        return "Вы не администратор!"


@app.post("/api/Admin/Rent/{id}")
async def admin_rent_edit(rent_input: schemas.adminEditRent,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    isadmin = db.get(models.Users, userId)
    if isadmin.isAdmin == True:
        Car_db = (
            db.query(models.Transport)
            .filter(models.Transport.transportId == rent_input.trasportId)
            .first()
        )
        if not Car_db:
            raise HTTPException(404, "Не верный идентификатор машины")
        User_db = db.query(models.Users).get(rent_input.userId)
        if not User_db:
            raise HTTPException(404, "Не верный идентификатор пользователя")
        db.query(models.Transport).filter(models.Rent.rentId == rent_input.rentId).update(
            {
                "transportId": rent_input.trasportId,
                "userId": rent_input.userId,
                "timeStart": rent_input.timeStart,
                "timeEnd": rent_input.timeEnd,
                "priceOfUnit": rent_input.priceOfUnit,
                "priceType": rent_input.rentType,
                "finalPrice": rent_input.finalPrice
            }
        )
        db.commit()
        return "Успешно"
    else:
        return "Вы не администратор!"


@app.delete("/api/Admin/Rent/{rentId}")
async def admin_history_rent_car(
    rentId : int,
    userId=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    user_db = db.query(models.Users).filter(models.Users.userId == userId).first()
    if user_db.is_auth == False:
        raise HTTPException(400, "Not authenticated")
    isadmin = db.get(models.Users, userId)
    if isadmin.isAdmin == True:
        rent = db.delete(models.Rent, rentId)
        db.commit()
        return "Успешно"
    else:
        return "Вы не администратор!"
