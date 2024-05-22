from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from . import models, schemas


def get_coil(db: Session, coil_id: int):
    return db.query(models.Coil).filter(models.Coil.id == coil_id).first()


def invert_date_params(input_range: list[str], max_range: list):
    if len(input_range) != 2 or max_range != 2:
        raise ValueError(f"""Ranges\' size is not correct! If you wish to invert one-sided range, put 0 on the other end. /n 
                         expected: input_range size = 2, max_range size = 2 /n
                         got: input_range size = {len(input_range)}, max_range size = {len(max_range)}""")
    input_start=0
    input_end=0
    max_start=0
    max_end=0
    try:
        if input_range[0] !=0:
            input_start_day, input_start_month, input_start_year = input_range[0].split('-')
            input_start = datetime(year=int(input_start_year), month=int(input_start_month), day=int(input_start_day))
        if input_range[1] !=0:
            input_end_day, input_end_month, input_end_year = input_range[1].split('-')
            input_end = datetime(year=int(input_end_year), month=int(input_end_month), day=int(input_end_day))
        if max_range[0] !=0:
            max_start_day, max_start_month, max_start_year = max_range[0].split('-')
            max_start = datetime(year=int(max_start_year), month=int(max_start_month), day=int(max_start_day))
        if max_range[1] !=0:
            max_end_day, max_end_month, max_end_year = max_range[1].split('-')
            max_end = datetime(year=int(max_end_year), month=int(max_end_month), day=int(max_end_day))
    except Exception as e:
        print(e)

    # swap values, if they are misplaced
    if input_start is datetime and input_end is datetime and input_start > input_end:
        input_start, input_end = input_end, input_start
    if max_start is datetime and max_end is datetime and max_start > max_end:
        max_start, max_end = max_end, max_start

    return_range = [0, 0]

    if input_start is datetime and input_end == 0:
        return_range = [max_start, input_start]
    elif input_end is datetime and input_start == 0:
        return_range = [input_end, max_end]
    else :
        return_range = [[max_start, input_start], [input_end, max_end]]

    return return_range


def get_coils_by_params(db: Session,
                        coil_add_date_start : str = '', coil_add_date_end: str = '',
                        coil_del_date_start : str = '', coil_del_date_end: str = '',
                        coil_length_start: float = 0, coil_length_end: float = 0,
                        coil_weight_start: float = 0, coil_weight_end: float = 0):
    
    # query = db.query(models.Coil)
    add_max_start, add_max_end = db.query(func.max(models.Coil.add_date)), db.query(func.min(models.Coil.add_date))
    del_max_start, del_max_end = db.query(func.max(models.Coil.del_date)), db.query(func.min(models.Coil.del_date))
    inverted_add = invert_date_params([coil_add_date_start, coil_add_date_end], [add_max_start, add_max_end])
    inverted_del = invert_date_params([coil_del_date_start, coil_del_date_end], [del_max_start, del_max_end])

    
        

def create_coil(db: Session, coil: schemas.Coil):
    db_coil = models.Coil(id = coil.id, length = coil.length, weight = coil.weight, add_date = coil.add_date, del_date = coil.del_date)
    db.add(db_coil)
    db.commit()
    db.refresh(db_coil)
    return db_coil


    # legacy
    #
    # # check if combination of variables is null
    # is_add_date_null = (coil_add_date_start + coil_add_date_end) == '' and coil_add_date_start == '' # true if add_date values are null 
    # is_del_date_null = (coil_del_date_start + coil_del_date_end) == '' and coil_del_date_start == '' # true if del_date values are null 
    # is_length_null = (coil_length_start + coil_length_end) == 0 and coil_length_start == 0 # true if length values are null
    # is_weight_null = (coil_weight_start + coil_weight_end) == 0 and coil_weight_start == 0 # true if weight values are null 
    # 
    # # since True converts to 1, if there is 2 False in a list, sum will be less than 3
    # if sum([is_add_date_null, is_del_date_null, is_length_null, is_weight_null]) < 3:
    #     raise ValueError('Too many parameters specified')
    #
    # if coil_add_date_start != '':
    #     db_query_result = 123
