from database.connection import get_db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LogService:
    
    @staticmethod
    def registrar(usuario_id: int, acao: str, modulo: str, detalhes: str = None,
                  valor_antigo: str = None, valor_novo: str = None, ip: str = None):
        try:
            db = get_db()
            db.execute('''
                INSERT INTO logs_sistema (usuario_id, acao, modulo, detalhes, valor_antigo, valor_novo, ip, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', (usuario_id, acao, modulo, detalhes, valor_antigo, valor_novo, ip))
            db.commit()
        except Exception as e:
            logger.error(f'Erro ao registrar log: {e}')
    
    @staticmethod
    def get_logs_recentes(limite: int = 100, modulo: str = None) -> list:
        db = get_db()
        if modulo:
            return [dict(r) for r in db.execute(
                'SELECT * FROM logs_sistema WHERE modulo = ? ORDER BY data DESC LIMIT ?',
                (modulo, limite)
            ).fetchall()]
        return [dict(r) for r in db.execute(
            'SELECT * FROM logs_sistema ORDER BY data DESC LIMIT ?', (limite,)
        ).fetchall()]
    
    @staticmethod
    def get_acoes_usuario(usuario_id: int, limite: int = 50) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM logs_sistema WHERE usuario_id = ? ORDER BY data DESC LIMIT ?',
            (usuario_id, limite)
        ).fetchall()]
    
    @staticmethod
    def limpar_logs_antigos(dias: int = 90):
        db = get_db()
        db.execute(f"DELETE FROM logs_sistema WHERE data < datetime('now', '-{dias} days')")
        db.commit()
        logger.info(f'🗑 Logs com mais de {dias} dias removidos')
