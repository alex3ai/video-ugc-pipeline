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

# Using lifespan instead of deprecated startup event
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    # Startup
    import threading
    from worker import run_pipeline_worker
    worker_thread = threading.Thread(target=run_pipeline_worker, daemon=True)
    worker_thread.start()
    print("Worker de processamento iniciado em thread separada.")
    yield
    # Shutdown code would go here if needed

app = FastAPI(title="Video_UGC_Pipeline", lifespan=lifespan)

# Create tables
Base.metadata.create_all(bind=engine)

# Incluir rotas
include_routes(app)

@app.get("/")
def read_root():
    return {"message": "Welcome to Video UGC Pipeline API"}

# Endpoint para testar manualmente o funcionamento do pipeline
@app.get("/debug/start-worker")
def start_worker_manually():
    # Iniciar o worker em uma thread separada
    import threading
    from worker import run_pipeline_worker
    worker_thread = threading.Thread(target=run_pipeline_worker, daemon=True)
    worker_thread.start()
    return {"message": "Worker iniciado manualmente em thread separada."}