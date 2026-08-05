from database.connection import get_db

class FavoritosService:
    
    @staticmethod
    def toggle(user_id: int, produto_id: int):
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return
        
        existe = db.execute('SELECT * FROM favoritos WHERE cliente_id = ? AND produto_id = ?',
                           (cliente['id'], produto_id)).fetchone()
        
        if existe:
            db.execute('DELETE FROM favoritos WHERE id = ?', (existe['id'],))
        else:
            db.execute('INSERT INTO favoritos (cliente_id, produto_id) VALUES (?, ?)',
                       (cliente['id'], produto_id))
        db.commit()
    
    @staticmethod
    def is_favorito(user_id: int, produto_id: int) -> bool:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return False
        
        return db.execute('SELECT * FROM favoritos WHERE cliente_id = ? AND produto_id = ?',
                         (cliente['id'], produto_id)).fetchone() is not None
    
    @staticmethod
    def listar(user_id: int) -> list:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return []
        
        return [dict(r) for r in db.execute(
            '''SELECT f.*, p.nome, p.preco, p.preco_promocional, p.foto
               FROM favoritos f JOIN produtos p ON f.produto_id = p.id
               WHERE f.cliente_id = ? AND p.disponivel = 1
               ORDER BY f.data DESC''',
            (cliente['id'],)
        ).fetchall()]
    
    @staticmethod
    def remover(user_id: int, produto_id: int):
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return
        db.execute('DELETE FROM favoritos WHERE cliente_id = ? AND produto_id = ?',
                   (cliente['id'], produto_id))
        db.commit()
