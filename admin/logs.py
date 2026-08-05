from database.connection import get_db
from utils.helpers import formatar_data

class LogsAdmin:
    
    @staticmethod
    def listar(limite: int = 100, modulo: str = None, usuario_id: int = None) -> list:
        db = get_db()
        query = 'SELECT * FROM logs_sistema WHERE 1=1'
        params = []
        
        if modulo:
            query += ' AND modulo = ?'
            params.append(modulo)
        if usuario_id:
            query += ' AND usuario_id = ?'
            params.append(usuario_id)
        
        query += ' ORDER BY data DESC LIMIT ?'
        params.append(limite)
        
        return [dict(r) for r in db.execute(query, params).fetchall()]
    
    @staticmethod
    def get_modulos() -> list:
        db = get_db()
        return [r['modulo'] for r in db.execute(
            'SELECT DISTINCT modulo FROM logs_sistema WHERE modulo IS NOT NULL ORDER BY modulo'
        ).fetchall()]
    
    @staticmethod
    def limpar(dias: int = 90) -> dict:
        db = get_db()
        db.execute(f"DELETE FROM logs_sistema WHERE data < datetime('now', '-{dias} days')")
        db.commit()
        return {'sucesso': True, 'mensagem': f'Logs com mais de {dias} dias removidos!'}
    
    @staticmethod
    def get_estatisticas() -> dict:
        db = get_db()
        return {
            'total': db.execute('SELECT COUNT(*) as t FROM logs_sistema').fetchone()['t'],
            'hoje': db.execute("SELECT COUNT(*) as t FROM logs_sistema WHERE date(data) = date('now')").fetchone()['t'],
            'acoes_hoje': [dict(r) for r in db.execute(
                "SELECT acao, COUNT(*) as total FROM logs_sistema WHERE date(data) = date('now') GROUP BY acao ORDER BY total DESC LIMIT 10"
            ).fetchall()]
        }
