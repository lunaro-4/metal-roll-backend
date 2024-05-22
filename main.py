from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root_2():
    return {"Hello" : "World"}




