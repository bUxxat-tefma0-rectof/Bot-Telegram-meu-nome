from database.connection import get_db
from services.notificacoes import NotificacaoService

class EstoqueAdmin:
    
    @staticmethod
    def adicionar(produto_id: int, quantidade: int) -> dict:
        db = get_db()
        db.execute('UPDATE produtos SET estoque = estoque + ?, disponivel = 1 WHERE id = ?',
                   (quantidade, produto_id))
        db.commit()
        
        # Notificar clientes que aguardavam
        alertas = db.execute('SELECT * FROM alertas_estoque WHERE produto_id = ?', (produto_id,)).fetchall()
        produto = db.execute('SELECT nome FROM produtos WHERE id = ?', (produto_id,)).fetchone()
        
        for alerta in alertas:
            NotificacaoService.enviar(
                alerta['cliente_id'], 'estoque', '📦 Produto Disponível!',
                f'O produto *{produto["nome"]}* voltou ao estoque!'
            )
        
        db.execute('DELETE FROM alertas_estoque WHERE produto_id = ?', (produto_id,))
        db.commit()
        
        return {'sucesso': True, 'mensagem': f'{quantidade} unidades adicionadas'}
    
    @staticmethod
    def remover(produto_id: int, quantidade: int) -> dict:
        db = get_db()
        produto = db.execute('SELECT estoque FROM produtos WHERE id = ?', (produto_id,)).fetchone()
        if not produto or produto['estoque'] < quantidade:
            return {'sucesso': False, 'mensagem': 'Estoque insuficiente'}
        
        db.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', (quantidade, produto_id))
        db.commit()
        return {'sucesso': True, 'mensagem': f'{quantidade} unidades removidas'}
    
    @staticmethod
    def get_estoque_baixo(limite: int = 20) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM produtos WHERE estoque <= 10 AND disponivel = 1 ORDER BY estoque ASC LIMIT ?',
            (limite,)
        ).fetchall()]
    
    @staticmethod
    def get_sem_estoque() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM produtos WHERE estoque <= 0 AND disponivel = 1'
        ).fetchall()]
