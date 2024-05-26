from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from sql_app.schemas import CoilModel
from sql_app.models import CoilBase
from sql_app.database import get_db 

from .handlers import *

from . import settings

DATE_FORMAT = settings.date_format

router =  APIRouter()

def incorrect_date_format(error):
    printerr(error)
    raise HTTPException(status_code=400, detail="Incorrect date format")

@router.get("/")
async def root():
    return []

@router.get("/coil")
async def get_coil(id_start : int | None = None, id_end : int | None = None,
                   length_start : float | None = None, length_end : float | None = None,
                   weight_start : float | None = None, weight_end : float | None = None,
                   add_date_start : str | None = None, add_date_end : str | None = None,
                   del_date_start : str | None = None, del_date_end : str | None = None,
                   session : AsyncSession = Depends(get_db)):

    # меняем значения местами, в случае если случайно передали обратный порядок

    if id_start and id_end and id_start > id_end:
        id_start, id_end = id_end, id_start
    if length_start and length_end and length_start > length_end:
        length_start, length_end = length_end, length_start
    if weight_start and weight_end and weight_start > weight_end:
        weight_start, weight_end = weight_end, weight_start

    
    # Проверяем на соответствие формату
    if add_date_start:
        try:
            add_date_start = datetime.strptime(add_date_start, DATE_FORMAT)
        except Exception as e:
            incorrect_date_format(e)
    if add_date_end:
        try:
            add_date_end = datetime.strptime(add_date_end, DATE_FORMAT)
        except Exception as e:
            incorrect_date_format(e)
    if del_date_start:
        try:
            del_date_start = datetime.strptime(del_date_start, DATE_FORMAT)
        except Exception as e:
            incorrect_date_format(e)
    if del_date_end:
        try:
            del_date_end = datetime.strptime(del_date_end, DATE_FORMAT)
        except Exception as e:
            incorrect_date_format(e)

    coil_response = await get_all_coil(session=session,
                                       id_start=id_start, id_end=id_end,
                                       length_start=length_start, length_end=length_end, 
                                       weight_start=weight_start, weight_end=weight_end, 
                                       add_date_start=add_date_start, add_date_end=add_date_end,
                                       del_date_start=del_date_start, del_date_end=del_date_end)
    return coil_response


@router.post("/coil")
async def create_coil(coil : CoilModel, session : AsyncSession = Depends(get_db)):
    add_date = None
    del_date = None
    if coil.weight < 0 or coil.length < 0 :
        raise HTTPException(status_code=400, detail="Weight and length must be non-negative")
    try:
        if coil.add_date != None and coil.add_date != '':
            add_date = datetime.strptime(coil.add_date, DATE_FORMAT)
        if coil.del_date != None and coil.del_date != '':
            del_date = datetime.strptime(coil.del_date, DATE_FORMAT)
        if del_date != None and add_date != None and add_date > del_date:
            raise AssertionError
        
    except ValueError as ve:
        incorrect_date_format(ve)
    except AssertionError as ae:
        printerr(ae)
        raise HTTPException(status_code=400, detail="Item was deleted before added")
    except Exception as e:
        printerr(e)
        raise HTTPException(status_code=503, detail="Unexpected error occured")

    response = await handle_add_coil(coil=coil, session=session, add_date=add_date)
    return response 


@router.delete("/coil")
async def delete_coil(coil_id: int, session : AsyncSession = Depends(get_db)):
    result = await handle_delete_coil(coil_id, session)
    return result


    
@router.get("/coil/stats")
async def get_coil_stats(session : AsyncSession = Depends(get_db), start_date : str | None = None, end_date : str | None = None ):
    datetime_start = None
    datetime_end = None
    try:
        if start_date:
            datetime_start = datetime.strptime(start_date, DATE_FORMAT)
        if end_date:
            datetime_end = datetime.strptime(end_date, DATE_FORMAT)
    except ValueError as ve:
        incorrect_date_format(ve)

    if datetime_start and datetime_end and datetime_start > datetime_end:
        datetime_start, datetime_end = datetime_end, datetime_start

    coil_stats = await handle_get_coil_stats(datetime_start, datetime_end, session)

    (coil_length_list, coil_weight_list, coil_add_del_dict) = separate_stats_data(coil_stats)

    add_amount = await count_by_param(start_date=datetime_start, end_date=datetime_end, session=session, param=CoilBase.add_date)
    del_amount = await count_by_param(start_date=datetime_start, end_date=datetime_end, session=session, param=CoilBase.del_date)

    (coil_len_max, coil_len_min, coil_len_avg, coil_len_sum) = calculate_stats_from_list(coil_length_list)
    (coil_weight_max, coil_weight_min, coil_weight_avg, coil_weight_sum) = calculate_stats_from_list(coil_weight_list)

    coil_weight_sum_fixed = await calculate_sum_coil_weight(start_date=datetime_start, end_date=datetime_end, session=session)

    (max_add_del_gap, min_add_del_gap) = find_gaps(coil_add_del_dict)


    result = {
            "roll_add_amount" : add_amount,
            "roll_del_amount" : del_amount,
            "avg_len" : coil_len_avg,
            "max_len" : coil_len_max,
            "min_len" : coil_len_min,
            "avg_weight" : coil_weight_avg,
            "max_weight" : coil_weight_max,
            "min_weight" : coil_weight_min,
            "sum_weight_in_range" : coil_weight_sum_fixed,
            "max_add_del_gap" : max_add_del_gap,
            "min_add_del_gap" : min_add_del_gap
    }


    return result
    # return {}
