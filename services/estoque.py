from database.connection import get_db
from services.notificacoes import NotificacaoService
import logging

logger = logging.getLogger(__name__)

class EstoqueService:
    
    @staticmethod
    def verificar_estoque_baixo():
        db = get_db()
        produtos = db.execute('''
            SELECT * FROM produtos 
            WHERE disponivel = 1 AND estoque <= estoque_minimo AND estoque > 0
        ''').fetchall()
        
        for p in produtos:
            NotificacaoService.notificar_estoque_baixo(dict(p))
            logger.info(f'⚠️ Estoque baixo: {p["nome"]} - {p["estoque"]} un')
        
        # Produtos sem estoque
        sem_estoque = db.execute('''
            SELECT * FROM produtos WHERE disponivel = 1 AND estoque <= 0
        ''').fetchall()
        
        for p in sem_estoque:
            db.execute('UPDATE produtos SET disponivel = 0 WHERE id = ?', (p['id'],))
            logger.info(f'❌ Produto desativado (sem estoque): {p["nome"]}')
        
        db.commit()
    
    @staticmethod
    def adicionar_estoque(produto_id: int, quantidade: int) -> dict:
        db = get_db()
        produto = db.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,)).fetchone()
        
        if not produto:
            return {'sucesso': False, 'mensagem': 'Produto não encontrado'}
        
        db.execute('UPDATE produtos SET estoque = estoque + ?, disponivel = 1 WHERE id = ?',
                   (quantidade, produto_id))
        db.commit()
        
        # Notificar clientes que aguardavam
        alertas = db.execute('SELECT * FROM alertas_estoque WHERE produto_id = ?', (produto_id,)).fetchall()
        for alerta in alertas:
            NotificacaoService.enviar(
                alerta['cliente_id'], 'estoque',
                '📦 Produto Disponível!',
                f'O produto *{produto["nome"]}* voltou ao estoque!\n\nCorra para garantir!'
            )
        
        db.execute('DELETE FROM alertas_estoque WHERE produto_id = ?', (produto_id,))
        db.commit()
        
        return {'sucesso': True, 'mensagem': f'{quantidade} unidades adicionadas'}
    
    @staticmethod
    def remover_estoque(produto_id: int, quantidade: int) -> dict:
        db = get_db()
        produto = db.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,)).fetchone()
        
        if not produto:
            return {'sucesso': False, 'mensagem': 'Produto não encontrado'}
        
        novo_estoque = produto['estoque'] - quantidade
        if novo_estoque < 0:
            return {'sucesso': False, 'mensagem': 'Estoque insuficiente'}
        
        db.execute('UPDATE produtos SET estoque = ? WHERE id = ?', (novo_estoque, produto_id))
        
        if novo_estoque == 0:
            db.execute('UPDATE produtos SET disponivel = 0 WHERE id = ?', (produto_id,))
        
        db.commit()
        return {'sucesso': True, 'mensagem': f'{quantidade} unidades removidas'}
    
    @staticmethod
    def alertar_quando_disponivel(cliente_id: int, produto_id: int) -> dict:
        db = get_db()
        
        existe = db.execute('SELECT * FROM alertas_estoque WHERE cliente_id = ? AND produto_id = ?',
                            (cliente_id, produto_id)).fetchone()
        
        if existe:
            db.execute('DELETE FROM alertas_estoque WHERE id = ?', (existe['id'],))
            db.commit()
            return {'sucesso': True, 'mensagem': 'Alerta removido'}
        
        db.execute('INSERT INTO alertas_estoque (cliente_id, produto_id) VALUES (?, ?)',
                   (cliente_id, produto_id))
        db.commit()
        return {'sucesso': True, 'mensagem': 'Você será notificado quando o produto voltar!'}
