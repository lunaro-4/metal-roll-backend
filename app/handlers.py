from datetime import datetime
from fastapi import HTTPException

from sqlalchemy import Result, delete, or_, select
from sqlalchemy.exc import  NoResultFound, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from sql_app.schemas import CoilInputModel, CoilModel
from sql_app.models import CoilBase


def printerr(err):
    print('---\n',err,'\n---')

def incorrect_data_format(param):
    raise HTTPException(status_code=400, detail=f"{param} must be non-negative")

async def get_all_coil(session : AsyncSession,
                       id_start : int | None = None, id_end : int | None = None,
                       length_start : float | None = None, length_end : float | None = None,
                       weight_start : float | None = None, weight_end : float | None = None,
                       add_date_start : datetime | None = None, add_date_end : datetime | None = None,
                       del_date_start : datetime | None = None, del_date_end : datetime | None = None,):

    query = select(CoilBase)

    if id_start:
        if id_start < 0:
            incorrect_data_format('id')
            query = query.filter(CoilBase.id >= id_start)
    if id_end:
        if id_end < 0:
            incorrect_data_format('id')
        query = query.filter(CoilBase.id <= id_end)
    if length_start:
        if length_start < 0:
            incorrect_data_format('id')
        query = query.filter(CoilBase.length >= length_start)
    if length_end:
        if length_end < 0:
            incorrect_data_format('id')
        query = query.filter(CoilBase.length <= length_end)
    if weight_start:
        if weight_start < 0:
            incorrect_data_format('id')
        query = query.filter(CoilBase.weight >= weight_start)
    if weight_end:
        if weight_end < 0:
            incorrect_data_format('id')
        query = query.filter(CoilBase.weight <= weight_end)
    if add_date_start:
        query = query.filter(CoilBase.add_date >= add_date_start)
    if add_date_end:
        query = query.filter(CoilBase.add_date <= add_date_end)
    if del_date_start:
        query = query.filter(CoilBase.del_date >= del_date_start)
    if del_date_end:
        query = query.filter(CoilBase.del_date <= del_date_end)

    try:
        coils = await session.execute(query)
    except OperationalError as oe:
        await session.rollback()
        printerr(oe)
        raise HTTPException(status_code=503, detail="Database unavailable")
    except Exception as e:
         printerr(e)
         raise HTTPException(status_code=503, detail="Unexpected error occured")

    return [CoilModel(id = coil.id,
                      length = coil.length, weight = coil.weight,
                      add_date = str(coil.add_date), del_date=str(coil.del_date)) for coil in coils.scalars()]


async def handle_add_coil(coil : CoilInputModel, session : AsyncSession, add_date : datetime | None = None, del_date : datetime | None = None):
    new_coil = CoilBase(length = coil.length, weight = coil.weight, add_date = add_date, del_date=del_date)
    try:
        session.add(new_coil)
        await session.commit()
        await session.refresh(new_coil)
    except OperationalError as oe:
        await session.rollback()
        printerr(oe)
        raise HTTPException(status_code=503, detail="Database unavailable")
    return CoilModel(id = new_coil.id,
                     length = new_coil.length, weight = new_coil.weight,
                     add_date = str(new_coil.add_date), del_date=str(new_coil.del_date))


async def handle_delete_coil(coil_id : int, session : AsyncSession):

    # проверка на неотрицательность id не требуется, 
    # поскольку запрос все равно ничего не найдет по отрицательному id

    try:
        coil_to_remove = await session.execute(select(CoilBase).filter_by(id = coil_id))
        coil_to_remove = coil_to_remove.scalar_one()
        await session.execute(delete(CoilBase).filter_by(id = coil_id))
        await session.commit()
        coil_to_remove = CoilModel(id = coil_to_remove.id, 
                             length = coil_to_remove.length, weight = coil_to_remove.weight,
                             add_date = str(coil_to_remove.add_date), del_date=str(coil_to_remove.del_date))
    except NoResultFound as nrf:
         printerr(nrf)
         raise HTTPException(status_code=400, detail="Metall roll with this ID not found")
    except OperationalError as oe:
        await session.rollback()
        printerr(oe)
        raise HTTPException(status_code=503, detail="Database unavailable")

    return coil_to_remove


async def handle_get_coil_stats(start_date : datetime, end_date : datetime, session : AsyncSession):

    try:
        coils_by_add_date = await session.execute(select(CoilBase).filter(CoilBase.add_date >= start_date).filter(CoilBase.add_date <= end_date))
        coils_by_del_date = await session.execute(select(CoilBase).filter(CoilBase.del_date >= start_date).filter(CoilBase.del_date <= end_date))
    except OperationalError as oe:
        await session.rollback()
        printerr(oe)
        raise HTTPException(status_code=503, detail="Database unavailable")

    result = coils_by_add_date.merge(coils_by_del_date)

    return result

async def count_by_param(session : AsyncSession, param, start_date : datetime | None = None, end_date : datetime | None = None):
    querry = select(CoilBase)
    if start_date:
       querry = querry.filter(param >= start_date) 
    if end_date:
        querry = querry.filter(param <= end_date)
    amount = await session.execute(querry)
    return len(amount.all())



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
        if coil == None or coil_add_del_dict[coil] == None:
            continue
        delta = coil_add_del_dict[coil] - coil
        if max_gap < delta.days:
            max_gap = delta.days
        if min_gap == None or min_gap > delta.days:
            min_gap = delta.days
        
        
    return (max_gap, min_gap)



async def calculate_sum_coil_weight(start_date : datetime, end_date : datetime, session : AsyncSession):
    # насколько я понял из задания, требуется отфильтровать рулоны, 
    # которые были добавлены после начала периода, но не были удалены до конца
    coils = await session.execute(select(CoilBase).filter(or_(CoilBase.del_date >= end_date, CoilBase.del_date == None)).filter(CoilBase.add_date != None))
    sum_weight = 0
    for coil in coils.scalars():
        sum_weight += coil.weight
    return sum_weight


