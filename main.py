from fastapi import FastAPI
from database import engine, SessionLocal, Base
from config import settings, validate_settings

# Importar os modelos para registrar as tabelas no Base
from models.entities import Campaign, PipelineJob

# Importar as rotas
from api.routes import include_routes

# Validar configurações antes de iniciar
try:
    validate_settings()
except ValueError as e:
    print(f"Erro de configuração: {e}")

app = FastAPI(title="Video_UGC_Pipeline")

# Create tables
Base.metadata.create_all(bind=engine)

# Incluir rotas
include_routes(app)

@app.get("/")
def read_root():
    return {"message": "Welcome to Video UGC Pipeline API"}