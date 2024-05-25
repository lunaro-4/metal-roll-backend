from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy import Result, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import MultipleResultsFound, NoResultFound, OperationalError, ResourceClosedError

from sql_app.schemas import CoilInputModel, CoilModel
from sql_app.models import CoilBase
from sql_app.database import get_db 


DATE_FORMAT = "%Y-%m-%d"

def printerr(err):
    print('---\n',err,'\n---')


async def get_all_coil(session : AsyncSession):
    try:
        coils = await session.execute(select(CoilBase))
    except OperationalError as oe:
        printerr(oe)
        raise HTTPException(status_code=503, detail="Database unavailable")
    except Exception as e:
         printerr(e)
         raise HTTPException(status_code=503, detail="Unexpected error occured")
    return [CoilModel(id = coil.id,
                      length = coil.length, weight = coil.weight,
                      add_date = str(coil.add_date), del_date=str(coil.del_date)) for coil in coils.scalars()]


async def handle_add_coil(coil : CoilInputModel, session : AsyncSession):
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
    except Exception as e:
         printerr(e)
         raise HTTPException(status_code=503, detail="Unexpected error occured")

    new_coil = CoilBase(length = coil.length, weight = coil.weight, add_date = add_date, del_date=del_date)
    session.add(new_coil)
    await session.commit()
    await session.refresh(new_coil)
    return CoilModel(id = new_coil.id,
                     length = new_coil.length, weight = new_coil.weight,
                     add_date = str(new_coil.add_date), del_date=str(new_coil.del_date))


async def handle_delete_coil(coil_id : int, session : AsyncSession):
    coil_to_remove = await session.execute(select(CoilBase).filter_by(id = coil_id))
    try:
        coil_to_remove = coil_to_remove.scalar_one()
        await session.execute(delete(CoilBase).filter_by(id = coil_id))
        await session.commit()
        coil_to_remove = CoilModel(id = coil_to_remove.id, 
                             length = coil_to_remove.length, weight = coil_to_remove.weight,
                             add_date = str(coil_to_remove.add_date), del_date=str(coil_to_remove.del_date))
        # await session.refresh(coil_to_remove)
    except NoResultFound as nrf:
         printerr(nrf)
         raise HTTPException(status_code=400, detail="Metall roll with this ID not found")
    # except Exception as e:
    #      printerr(e)
    #      raise HTTPException(status_code=503, detail="Unexpected error occured")

    return coil_to_remove
    # return {"result" : "123"}


async def get_all_coil_stats(session : AsyncSession):
    return []






