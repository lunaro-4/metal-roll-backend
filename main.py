from fastapi import FastAPI
from sql_app.schemas import Coil

app = FastAPI()


fake_coils_db = [{"id" : 1224, "length" : 12, "weight" : 13, "add_date" : "12-04-2020"},
                 {"id" : 1228, "length" : 33, "weight" : 58, "add_date" : "13-04-2020"},
                 {"id" : 3244, "length" : 34, "weight" : 5, "add_date" : "12-02-2020"},
                 {"id" : 4455, "length" : 3, "weight" : 15, "add_date" : "12-03-2020"}]

@app.get("/")
async def root_2():
    return {"Hello" : "World"}

@app.get("/coil")
async def get_coil(skip: int = 0, limit: int = 10):
    return fake_coils_db[skip : skip + limit]

@app.post("/coil")
async def create_coil(coil : Coil):
    return coil






