from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.locations import Base

DATABASE_URL = "postgresql://postgres:password@localhost:5432/urban_utilization"

app = FastAPI()

#Connect tp PostGIS database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind = engine)

#Create tables if they don't exist 
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message":"FastAPI + PostGIS API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port = 8000, reload = True)
