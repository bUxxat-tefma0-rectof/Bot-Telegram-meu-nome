import sqlite3
import os
from threading import Lock
from config.geral import Config

_lock = Lock()
_conn = None

def get_db() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        db_path = Config.DATABASE_PATH
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
        _conn = sqlite3.connect(db_path, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("PRAGMA foreign_keys=ON")
        _conn.execute("PRAGMA busy_timeout=5000")
    return _conn

def init_database():
    from .schema import criar_todas_tabelas
    from .seed import inserir_dados_padrao
    
    with _lock:
        criar_todas_tabelas()
        inserir_dados_padrao()
    
    print('✅ Banco de dados inicializado com sucesso')
