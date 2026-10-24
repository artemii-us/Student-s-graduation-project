from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3


app = FastAPI(title="Автосервис API")

DATABASE = "autoservice.db"



def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables():
    connection = get_connection()

    connection.executescript("""
        CREATE TABLE IF NOT EXISTS owners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT
        );

        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER,
            plate_number TEXT,
            owner_id INTEGER NOT NULL,

            FOREIGN KEY (owner_id)
                REFERENCES owners(id)
        );

        CREATE TABLE IF NOT EXISTS masters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            specialization TEXT
        );

        CREATE TABLE IF NOT EXISTS repairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER NOT NULL,
            master_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            repair_date TEXT,
            price REAL,

            FOREIGN KEY (car_id)
                REFERENCES cars(id),

            FOREIGN KEY (master_id)
                REFERENCES masters(id)
        );
    """)

    connection.commit()
    connection.close()


create_tables()

class OwnerCreate(BaseModel):
    name: str
    phone: str | None = None
    address: str | None = None


class CarCreate(BaseModel):
    brand: str
    model: str
    year: int | None = None
    plate_number: str | None = None
    owner_id: int


class MasterCreate(BaseModel):
    name: str
    phone: str | None = None
    specialization: str | None = None


class RepairCreate(BaseModel):
    car_id: int
    master_id: int
    description: str
    repair_date: str | None = None
    price: float | None = None


@app.get("/owners")
def get_owners():
    connection = get_connection()

    owners = connection.execute(
        "SELECT * FROM owners"
    ).fetchall()

    connection.close()

    return [dict(owner) for owner in owners]


@app.post("/owners")
def create_owner(owner: OwnerCreate):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO owners (name, phone, address)
        VALUES (?, ?, ?)
        """,
        (owner.name, owner.phone, owner.address)
    )

    connection.commit()

    owner_id = cursor.lastrowid

    connection.close()

    return {
        "id": owner_id,
        "message": "Владелец добавлен"
    }


@app.get("/owners/{owner_id}")
def get_owner(owner_id: int):
    connection = get_connection()

    owner = connection.execute(
        "SELECT * FROM owners WHERE id = ?",
        (owner_id,)
    ).fetchone()

    connection.close()

    if owner is None:
        raise HTTPException(
            status_code=404,
            detail="Владелец не найден"
        )

    return dict(owner)


@app.get("/cars")
def get_cars():
    connection = get_connection()

    cars = connection.execute(
        "SELECT * FROM cars"
    ).fetchall()

    connection.close()

    return [dict(car) for car in cars]


@app.post("/cars")
def create_car(car: CarCreate):
    connection = get_connection()

    owner = connection.execute(
        "SELECT id FROM owners WHERE id = ?",
        (car.owner_id,)
    ).fetchone()

    if owner is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Владелец не найден"
        )

    cursor = connection.execute(
        """
        INSERT INTO cars
        (brand, model, year, plate_number, owner_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            car.brand,
            car.model,
            car.year,
            car.plate_number,
            car.owner_id
        )
    )

    connection.commit()

    car_id = cursor.lastrowid

    connection.close()

    return {
        "id": car_id,
        "message": "Машина добавлена"
    }


@app.get("/cars/{car_id}")
def get_car(car_id: int):
    connection = get_connection()

    car = connection.execute(
        "SELECT * FROM cars WHERE id = ?",
        (car_id,)
    ).fetchone()

    connection.close()

    if car is None:
        raise HTTPException(
            status_code=404,
            detail="Машина не найдена"
        )

    return dict(car)


@app.get("/masters")
def get_masters():
    connection = get_connection()

    masters = connection.execute(
        "SELECT * FROM masters"
    ).fetchall()

    connection.close()

    return [dict(master) for master in masters]


@app.post("/masters")
def create_master(master: MasterCreate):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO masters
        (name, phone, specialization)
        VALUES (?, ?, ?)
        """,
        (
            master.name,
            master.phone,
            master.specialization
        )
    )

    connection.commit()

    master_id = cursor.lastrowid

    connection.close()

    return {
        "id": master_id,
        "message": "Мастер добавлен"
    }


@app.get("/masters/{master_id}")
def get_master(master_id: int):
    connection = get_connection()

    master = connection.execute(
        "SELECT * FROM masters WHERE id = ?",
        (master_id,)
    ).fetchone()

    connection.close()

    if master is None:
        raise HTTPException(
            status_code=404,
            detail="Мастер не найден"
        )

    return dict(master)

@app.get("/repairs")
def get_repairs():
    connection = get_connection()

    repairs = connection.execute(
        "SELECT * FROM repairs"
    ).fetchall()

    connection.close()

    return [dict(repair) for repair in repairs]


@app.post("/repairs")
def create_repair(repair: RepairCreate):
    connection = get_connection()

    car = connection.execute(
        "SELECT id FROM cars WHERE id = ?",
        (repair.car_id,)
    ).fetchone()

    if car is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Машина не найдена"
        )

    master = connection.execute(
        "SELECT id FROM masters WHERE id = ?",
        (repair.master_id,)
    ).fetchone()

    if master is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Мастер не найден"
        )

    cursor = connection.execute(
        """
        INSERT INTO repairs
        (car_id, master_id, description, repair_date, price)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            repair.car_id,
            repair.master_id,
            repair.description,
            repair.repair_date,
            repair.price
        )
    )

    connection.commit()

    repair_id = cursor.lastrowid

    connection.close()

    return {
        "id": repair_id,
        "message": "Ремонт добавлен"
    }


@app.get("/repairs/{repair_id}")
def get_repair(repair_id: int):
    connection = get_connection()

    repair = connection.execute(
        "SELECT * FROM repairs WHERE id = ?",
        (repair_id,)
    ).fetchone()

    connection.close()

    if repair is None:
        raise HTTPException(
            status_code=404,
            detail="Ремонт не найден"
        )

    return dict(repair)
