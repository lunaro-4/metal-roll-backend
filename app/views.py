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
async def get_coil_2(session : AsyncSession = Depends(get_db)):
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
async def get_coil_stats(session : AsyncSession = Depends(get_db)):
    coil_stats = await get_all_coil_stats(session)
    return coil_stats


