from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from fastapi import FastAPI
from database import engine, SessionLocal, Base
from config import settings, validate_settings

# Importar as rotas
from api.routes import include_routes

# Validar configurações antes de iniciar
try:
    validate_settings()
except ValueError as e:
    print(f"Erro de configuração: {e}")

# Atualizar a URL do banco de dados com base nas configurações
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

app = FastAPI(title="Video_UGC_Pipeline")

# Create tables
Base.metadata.create_all(bind=engine)

# Incluir rotas
include_routes(app)

@app.get("/")
def read_root():
    return {"message": "Welcome to Video UGC Pipeline API"}