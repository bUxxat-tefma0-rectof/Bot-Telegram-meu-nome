from database.connection import get_db
from typing import List, Dict, Optional
from datetime import datetime

class LogModel:
    
    @staticmethod
    def registrar(usuario_id: Optional[int], acao: str, modulo: str, 
                  detalhes: str = None, valor_antigo: str = None, 
                  valor_novo: str = None, ip: str = None) -> int:
        db = get_db()
        cursor = db.execute('''
            INSERT INTO logs_sistema (usuario_id, acao, modulo, detalhes, valor_antigo, valor_novo, ip, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (usuario_id, acao, modulo, detalhes, valor_antigo, valor_novo, ip))
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_recentes(limite: int = 100, modulo: str = None) -> List[Dict]:
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
    def get_por_usuario(usuario_id: int, limite: int = 50) -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM logs_sistema WHERE usuario_id = ? ORDER BY data DESC LIMIT ?',
            (usuario_id, limite)
        ).fetchall()]
    
    @staticmethod
    def get_por_acao(acao: str, limite: int = 50) -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM logs_sistema WHERE acao = ? ORDER BY data DESC LIMIT ?',
            (acao, limite)
        ).fetchall()]
    
    @staticmethod
    def get_estatisticas() -> Dict:
        db = get_db()
        return {
            'total': db.execute('SELECT COUNT(*) as t FROM logs_sistema').fetchone()['t'],
            'hoje': db.execute("SELECT COUNT(*) as t FROM logs_sistema WHERE date(data) = date('now')").fetchone()['t'],
            'acoes': [dict(r) for r in db.execute(
                "SELECT acao, COUNT(*) as total FROM logs_sistema WHERE date(data) = date('now') GROUP BY acao ORDER BY total DESC LIMIT 10"
            ).fetchall()],
            'modulos': [dict(r) for r in db.execute(
                "SELECT modulo, COUNT(*) as total FROM logs_sistema GROUP BY modulo ORDER BY total DESC"
            ).fetchall()]
        }
    
    @staticmethod
    def limpar_antigos(dias: int = 90) -> int:
        db = get_db()
        result = db.execute(f"DELETE FROM logs_sistema WHERE data < datetime('now', '-{dias} days')")
        db.commit()
        return result.rowcount
    
    @staticmethod
    def buscar(detalhes: str, limite: int = 50) -> List[Dict]:
        db = get_db()
        busca = f'%{detalhes}%'
        return [dict(r) for r in db.execute(
            'SELECT * FROM logs_sistema WHERE detalhes LIKE ? ORDER BY data DESC LIMIT ?',
            (busca, limite)
        ).fetchall()]
    
    @staticmethod
    def get_alteracoes_produto(produto_id: int) -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT * FROM logs_sistema WHERE modulo = 'produtos' AND (detalhes LIKE ? OR detalhes LIKE ?) ORDER BY data DESC",
            (f'%ID {produto_id}%', f'%produto {produto_id}%')
        ).fetchall()]
    
    @staticmethod
    def get_alteracoes_config() -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT * FROM logs_sistema WHERE modulo = 'configuracoes' ORDER BY data DESC LIMIT 100"
        ).fetchall()]
