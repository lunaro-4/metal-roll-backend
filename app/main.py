from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sql_app.schemas import CoilModel
from sql_app.models import CoilBase
from sql_app.database import get_db 

# router =  APIRouter(prefix="/coil")
router =  APIRouter()

DATE_FORMAT = "%Y-%m-%d"

def printerr(err):
    print('---\n',err,'\n---')


@router.get("/")
async def root_2():
    return {"Hello" : "World"}

@router.get("/coil")
async def get_coil_2(session : AsyncSession = Depends(get_db)):
    coils = await session.execute(select(CoilBase))
    return [CoilModel(id = coil.id,
                      length = coil.length, weight = coil.weight,
                      add_date = str(coil.add_date), del_date=str(coil.del_date)) for coil in coils.scalars()]



@router.post("/coil")
async def create_coil(coil : CoilModel, session : AsyncSession = Depends(get_db)):
    try:
        add_date = None
        if coil.add_date != None and coil.add_date != '':
            add_date = datetime.strptime(coil.add_date, DATE_FORMAT)
        del_date = None
        if coil.del_date != None and coil.del_date != '':
            del_date = datetime.strptime(coil.del_date, DATE_FORMAT)
    except ValueError as ve:
         printerr(ve)
         raise HTTPException(status_code=400, detail="Incorrect date format")

    new_coil = CoilBase(length = coil.length, weight = coil.weight, add_date = add_date, del_date=del_date)
    session.add(new_coil)
    await session.commit()
    await session.refresh(new_coil)
    return CoilModel(id = new_coil.id, length = new_coil.length, weight = new_coil.weight, add_date = str(new_coil.add_date), del_date=str(new_coil.del_date))

@router.delete("/coil")
async def delete_coil(coil_id: int, session : AsyncSession = Depends(get_db)):
    coil_to_remove = await session.execute(select(CoilBase).filter_by(id = coil_id))
    if coil_to_remove:
        coil_to_remove = coil_to_remove.first()
        await session.delete(coil_to_remove)
        await session.commit()

    return CoilModel(id = coil_to_remove.id, length = coil_to_remove.length, weight = coil_to_remove.weight, add_date = str(coil_to_remove.add_date), del_date=str(coil_to_remove.del_date))

    
    pass


