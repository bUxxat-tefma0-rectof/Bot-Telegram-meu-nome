from database.connection import get_db
from database.models.produto import ProdutoModel
from services.notificacoes import NotificacaoService
from utils.helpers import formatar_moeda

class EstoqueAdmin:
    
    @staticmethod
    def adicionar(produto_id: int, quantidade: int) -> dict:
        db = get_db()
        produto = ProdutoModel.get_by_id(produto_id)
        
        if not produto:
            return {'sucesso': False, 'mensagem': 'Produto não encontrado'}
        
        db.execute('UPDATE produtos SET estoque = estoque + ?, disponivel = 1 WHERE id = ?',
                   (quantidade, produto_id))
        db.commit()
        
        # Notificar clientes com alerta
        alertas = db.execute('SELECT * FROM alertas_estoque WHERE produto_id = ?', (produto_id,)).fetchall()
        for alerta in alertas:
            NotificacaoService.enviar(
                alerta['cliente_id'], 'estoque', '📦 Produto Disponível!',
                f'O produto *{produto["nome"]}* voltou ao estoque!\n\nCorra para garantir o seu! 🛒'
            )
        
        db.execute('DELETE FROM alertas_estoque WHERE produto_id = ?', (produto_id,))
        db.commit()
        
        return {'sucesso': True, 'mensagem': f'{quantidade} unidades adicionadas ao estoque de {produto["nome"]}'}
    
    @staticmethod
    def remover(produto_id: int, quantidade: int) -> dict:
        db = get_db()
        produto = ProdutoModel.get_by_id(produto_id)
        
        if not produto:
            return {'sucesso': False, 'mensagem': 'Produto não encontrado'}
        
        if produto['estoque'] < quantidade:
            return {'sucesso': False, 'mensagem': f'Estoque insuficiente. Disponível: {produto["estoque"]}'}
        
        novo_estoque = produto['estoque'] - quantidade
        db.execute('UPDATE produtos SET estoque = ? WHERE id = ?', (novo_estoque, produto_id))
        
        if novo_estoque <= 0:
            db.execute('UPDATE produtos SET disponivel = 0 WHERE id = ?', (produto_id,))
        
        db.commit()
        return {'sucesso': True, 'mensagem': f'{quantidade} unidades removidas do estoque de {produto["nome"]}'}
    
    @staticmethod
    def get_estoque_baixo(limite: int = 20) -> list:
        return ProdutoModel.get_estoque_baixo(limite)
    
    @staticmethod
    def get_sem_estoque() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM produtos WHERE estoque <= 0 AND disponivel = 1'
        ).fetchall()]
    
    @staticmethod
    def verificar_todos() -> dict:
        db = get_db()
        baixo = ProdutoModel.get_estoque_baixo(30)
        sem = EstoqueAdmin.get_sem_estoque()
        
        # Desativa produtos sem estoque
        for p in sem:
            db.execute('UPDATE produtos SET disponivel = 0 WHERE id = ?', (p['id'],))
        db.commit()
        
        return {
            'estoque_baixo': baixo,
            'sem_estoque': sem,
            'total_baixo': len(baixo),
            'total_sem': len(sem)
        }
