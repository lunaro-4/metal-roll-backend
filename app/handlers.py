from contextlib import asynccontextmanager
from datetime import datetime, timedelta
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

        if add_date == None:
            raise AssertionError

        if del_date != None and add_date > del_date:
            raise AssertionError
    except ValueError as ve:
         printerr(ve)
         raise HTTPException(status_code=400, detail="Incorrect date format")
    except AssertionError as ae:
        printerr(ae)
        raise HTTPException(status_code=400, detail="Item was deleted before added")
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


async def handle_get_coil_stats(start_date : datetime, end_date : datetime, session : AsyncSession):
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    coils_by_add_date = await session.execute(select(CoilBase).filter(CoilBase.add_date >= start_date).filter(CoilBase.add_date <= end_date))
    coils_by_del_date = await session.execute(select(CoilBase).filter(CoilBase.add_date >= start_date).filter(CoilBase.add_date <= end_date))
    result = coils_by_add_date.merge(coils_by_del_date)

    return result


def separate_stats_data(coil_stats : Result):
    coil_length_list = []
    coil_weight_list = []
    coil_add_del_dict = {}
    for coil in coil_stats.scalars():
        coil_length_list.append(float(coil.length))
        coil_weight_list.append(float(coil.weight))
        coil_add_del_dict[coil.add_date] = coil.del_date
    return (coil_length_list, coil_weight_list, coil_add_del_dict)
        
def calculate_stats_from_list(stat_list : list):
    stat_max = 0
    stat_min = None
    stat_sum = 0
    for stat in stat_list:
        stat_sum += stat
        if stat > stat_max:
            stat_max = stat
        if stat_min == None or stat < stat_min:
            stat_min = stat

    stat_avg = stat_sum / len(stat_list)

    return (stat_max, stat_min, stat_avg, stat_sum)



def find_gaps(coil_add_del_dict: dict):

    max_gap = 0
    min_gap = None

    for coil in coil_add_del_dict.keys():
        delta = coil_add_del_dict[coil] - coil
        if max_gap < delta.days:
            max_gap = delta.days
        if min_gap == None or min_gap > delta.days:
            min_gap = delta.days
        
        
    return (max_gap, min_gap)



