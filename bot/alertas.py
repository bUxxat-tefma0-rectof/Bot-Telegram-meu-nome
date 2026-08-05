from database.connection import get_db

class AlertasService:
    
    @staticmethod
    def criar_alerta_estoque(user_id: int, produto_id: int) -> dict:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return {'sucesso': False}
        
        existe = db.execute('SELECT * FROM alertas_estoque WHERE cliente_id = ? AND produto_id = ?',
                           (cliente['id'], produto_id)).fetchone()
        
        if existe:
            db.execute('DELETE FROM alertas_estoque WHERE id = ?', (existe['id'],))
            db.commit()
            return {'sucesso': True, 'mensagem': 'Alerta removido'}
        
        db.execute('INSERT INTO alertas_estoque (cliente_id, produto_id) VALUES (?, ?)',
                   (cliente['id'], produto_id))
        db.commit()
        return {'sucesso': True, 'mensagem': 'Você será notificado quando o produto voltar ao estoque!'}
    
    @staticmethod
    def get_alertas_ativos(user_id: int) -> list:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return []
        
        return [dict(r) for r in db.execute(
            '''SELECT a.*, p.nome, p.foto FROM alertas_estoque a
               JOIN produtos p ON a.produto_id = p.id
               WHERE a.cliente_id = ?''',
            (cliente['id'],)
        ).fetchall()]
