from database.connection import get_db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AuditoriaService:
    
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
            logger.error(f'Erro ao registrar auditoria: {e}')
    
    @staticmethod
    def get_logs(limite: int = 100, modulo: str = None) -> list:
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
    def get_alteracoes_produto(produto_id: int) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT * FROM logs_sistema WHERE modulo = 'produtos' AND detalhes LIKE ? ORDER BY data DESC",
            (f'%ID {produto_id}%',)
        ).fetchall()]
    
    @staticmethod
    def get_alteracoes_config() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT * FROM logs_sistema WHERE modulo = 'configuracoes' ORDER BY data DESC LIMIT 100"
        ).fetchall()]
