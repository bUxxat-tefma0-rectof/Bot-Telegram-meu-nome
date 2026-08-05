from database.connection import get_db
from utils.helpers import formatar_data

class NotificacoesBot:
    
    @staticmethod
    def get_notificacoes(user_id: int, limite: int = 20) -> list:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return []
        
        return [dict(r) for r in db.execute(
            'SELECT * FROM notificacoes WHERE cliente_id = ? ORDER BY data DESC LIMIT ?',
            (cliente['id'], limite)
        ).fetchall()]
    
    @staticmethod
    def get_nao_lidas(user_id: int) -> list:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return []
        
        return [dict(r) for r in db.execute(
            'SELECT * FROM notificacoes WHERE cliente_id = ? AND lida = 0 ORDER BY data DESC',
            (cliente['id'],)
        ).fetchall()]
    
    @staticmethod
    def marcar_como_lida(user_id: int, notificacao_id: int):
        db = get_db()
        db.execute('UPDATE notificacoes SET lida = 1 WHERE id = ?', (notificacao_id,))
        db.commit()
    
    @staticmethod
    def contar_nao_lidas(user_id: int) -> int:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return 0
        
        return db.execute('SELECT COUNT(*) as t FROM notificacoes WHERE cliente_id = ? AND lida = 0',
                         (cliente['id'],)).fetchone()['t']
