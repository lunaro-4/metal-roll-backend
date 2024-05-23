from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sql_app.schemas import CoilModel
from sql_app.models import CoilBase
from sql_app.database import create_db_and_tables, get_async_session


DATE_FORMAT = "%d-%m-%Y"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root_2():
    return {"Hello" : "World"}

@app.get("/coil")
async def get_coil_2(session : AsyncSession = Depends(get_async_session)):
    coils = await session.execute(select(CoilBase))
    return [CoilModel(id = coil.id, length = coil.length, weight = coil.weight, add_date = str(coil.add_date), del_date=str(coil.del_date)) for coil in coils.scalars()]

# @app.get("/coil")
# async def get_coil(skip: int = 0, limit: int = 10):
#     return fake_coils_db[skip : skip + limit]



@app.post("/coil")
async def create_coil(coil : CoilModel, session : AsyncSession = Depends(get_async_session)):
    add_date = datetime.strptime(coil.add_date, DATE_FORMAT)
    del_date = None
    if coil.del_date != None and coil.del_date != '':
        del_date = datetime.strptime(coil.del_date, DATE_FORMAT)

    session.add(CoilBase(id = coil.id, length = coil.length, weight = coil.weight, add_date = add_date, del_date=del_date))
    await session.commit()
    return coil



# def translate_to_datetime(input_date: str) -> datetime:
#     input_params_list = input_date.split(sep='-')
#     input_day, input_month, input_year = input_params_list[0], input_params_list[1], input_params_list[2]
#     return datetime(int(input_day), int(input_month), int(input_year))


