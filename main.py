from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sql_app.schemas import CoilModel
from sql_app.models import CoilBase
from sql_app.database import create_db_and_tables, get_async_session


DATE_FORMAT = "%Y-%m-%d"

def printerr(err):
    print('---\n',err,'\n---')

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



@app.post("/coil")
async def create_coil(coil : CoilModel, session : AsyncSession = Depends(get_async_session)):
    try:
        add_date = None
        if coil.add_date != None and coil.add_date != '':
            add_date = datetime.strptime(coil.add_date, DATE_FORMAT)
        del_date = None
        if coil.del_date != None and coil.del_date != '':
            del_date = datetime.strptime(coil.del_date, DATE_FORMAT)
    except ValueError as ve:
         # print(f"""Date format is not correct!
         #       expected : "yyyy-MM-dd"
         #       got: {coil.add_date} and {coil.del_date}""", '\n',str(ve))
         printerr(ve)
         raise HTTPException(status_code=400, detail="Incorrect date format")

    session.add(CoilBase(length = coil.length, weight = coil.weight, add_date = add_date, del_date=del_date))
    await session.commit()
    return coil


