from fastapi import FastAPI
from database import Base, engine

from models import Categoria        
from producto import Producto       
from cliente import Cliente         
from compra import Compra           
from usuario import Usuario         

app = FastAPI(title="Papelería API")


Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"ok": True, "msg": "API lista"}
