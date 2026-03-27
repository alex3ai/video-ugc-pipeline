import os
import sqlite3
from config import settings
from database import engine, Base
from models.entities import Campaign, PipelineJob

def reset_database():
    # Extrai o nome do arquivo do DATABASE_URL
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
    else:
        print("Este script só funciona com bancos de dados SQLite")
        return

    # Fecha qualquer conexão pendente e remove o arquivo do banco de dados
    engine.dispose()  # Fecha todas as conexões
    
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Banco de dados {db_path} removido.")
        except PermissionError:
            print(f"Não foi possível remover o banco de dados {db_path}, está em uso por outro processo.")
            return
    else:
        print(f"Banco de dados {db_path} não encontrado, criando novo banco de dados...")

    # Recreate all tables
    Base.metadata.create_all(bind=engine)
    print("Novo banco de dados criado com tabelas vazias.")

if __name__ == "__main__":
    reset_database()
    print("Banco de dados resetado com sucesso!")