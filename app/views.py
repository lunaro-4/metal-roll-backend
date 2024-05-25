from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from sql_app.schemas import CoilModel
from sql_app.models import CoilBase
from sql_app.database import get_db 
from .handlers import *



# router =  APIRouter(prefix="/coil")
router =  APIRouter()


@router.get("/")
async def root():
    return []

@router.get("/coil")
async def get_coil(session : AsyncSession = Depends(get_db)):
    coil_response = await get_all_coil(session)
    return coil_response


@router.post("/coil")
async def create_coil(coil : CoilModel, session : AsyncSession = Depends(get_db)):
    response = await handle_add_coil(coil, session)
    return response 


@router.delete("/coil")
async def delete_coil(coil_id: int, session : AsyncSession = Depends(get_db)):
    result = await handle_delete_coil(coil_id, session)
    return result

    # return CoilModel(id = coil_to_remove.id, length = coil_to_remove.length, weight = coil_to_remove.weight, add_date = str(coil_to_remove.add_date), del_date=str(coil_to_remove.del_date))

    
@router.get("/coil/stats")
async def get_coil_stats(start_date : str, end_date : str ,session : AsyncSession = Depends(get_db)):
    try:
        datetime_start = datetime.now()
        if start_date != None and start_date != '':
            datetime_start = datetime.strptime(start_date, DATE_FORMAT)
        datetime_end = datetime.now()
        if end_date != None and end_date != '':
            datetime_end = datetime.strptime(end_date, DATE_FORMAT)
    except ValueError as ve:
         printerr(ve)
         raise HTTPException(status_code=400, detail="Incorrect date format")


    coil_stats = await handle_get_coil_stats(datetime_start, datetime_end, session)

    (coil_length_list, coil_weight_list, coil_add_del_dict) = separate_stats_data(coil_stats)

    (coil_len_max, coil_len_min, coil_len_avg, coil_len_sum) = calculate_stats_from_list(coil_length_list)
    (coil_weight_max, coil_weight_min, coil_weight_avg, coil_weight_sum) = calculate_stats_from_list(coil_weight_list)

    (max_add_del_gap, min_add_del_gap) = find_gaps(coil_add_del_dict)

    result = {
            # TODO
            "roll_add_amount" : 0,
            # TODO
            "roll_del_amount" : 0,
            "avg_len" : coil_len_avg,
            "max_len" : coil_len_max,
            "min_len" : coil_len_min,
            # TODO
            "sum_len" : coil_len_sum,
            "avg_weight" : coil_weight_avg,
            "max_weight" : coil_weight_max,
            "min_weight" : coil_weight_min,
            "max_add_del_gap" : max_add_del_gap,
            "min_add_del_gap" : min_add_del_gap
    }


    return result
    # return [CoilModel(id = coil.id,
    #                   length = coil.length, weight = coil.weight,
    #                   add_date = str(coil.add_date), del_date=str(coil.del_date)) for coil in coil_stats.scalars()]

