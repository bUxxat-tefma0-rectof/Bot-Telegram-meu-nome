from database.connection import get_db
from datetime import datetime

class CarrinhoService:
    
    @staticmethod
    def adicionar(user_id: int, produto_id: int, quantidade: int = 1, comentario: str = None):
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return {'sucesso': False}
        
        produto = db.execute('SELECT estoque, limite_por_cliente FROM produtos WHERE id = ?', (produto_id,)).fetchone()
        if not produto or produto['estoque'] < quantidade:
            return {'sucesso': False, 'mensagem': 'Estoque insuficiente'}
        
        existe = db.execute('SELECT * FROM carrinhos WHERE cliente_id = ? AND produto_id = ?',
                            (cliente['id'], produto_id)).fetchone()
        
        if existe:
            nova_qtd = existe['quantidade'] + quantidade
            if produto['limite_por_cliente'] and nova_qtd > produto['limite_por_cliente']:
                return {'sucesso': False, 'mensagem': f'Limite de {produto["limite_por_cliente"]} por cliente'}
            db.execute('UPDATE carrinhos SET quantidade = ?, comentario = ? WHERE id = ?',
                       (nova_qtd, comentario, existe['id']))
        else:
            db.execute('INSERT INTO carrinhos (cliente_id, produto_id, quantidade, comentario, data_adicao) VALUES (?,?,?,?,?)',
                       (cliente['id'], produto_id, quantidade, comentario, datetime.now()))
        
        db.commit()
        return {'sucesso': True, 'mensagem': 'Adicionado ao carrinho!'}
    
    @staticmethod
    def remover(user_id: int, carrinho_id: int):
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return
        db.execute('DELETE FROM carrinhos WHERE id = ? AND cliente_id = ?', (carrinho_id, cliente['id']))
        db.commit()
    
    @staticmethod
    def atualizar_quantidade(user_id: int, carrinho_id: int, quantidade: int):
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return
        
        if quantidade <= 0:
            db.execute('DELETE FROM carrinhos WHERE id = ? AND cliente_id = ?', (carrinho_id, cliente['id']))
        else:
            db.execute('UPDATE carrinhos SET quantidade = ? WHERE id = ? AND cliente_id = ?',
                       (quantidade, carrinho_id, cliente['id']))
        db.commit()
    
    @staticmethod
    def limpar(user_id: int):
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return
        db.execute('DELETE FROM carrinhos WHERE cliente_id = ?', (cliente['id'],))
        db.commit()
    
    @staticmethod
    def listar(user_id: int) -> dict:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return {'itens': [], 'total': 0, 'quantidade': 0}
        
        itens = [dict(r) for r in db.execute(
            '''SELECT c.*, p.nome, p.preco, p.preco_promocional, p.foto, p.marca, p.estoque, p.limite_por_cliente
               FROM carrinhos c JOIN produtos p ON c.produto_id = p.id
               WHERE c.cliente_id = ?''', (cliente['id'],)
        ).fetchall()]
        
        total = sum((i.get('preco_promocional') or i.get('preco', 0)) * i['quantidade'] for i in itens)
        qtd = sum(i['quantidade'] for i in itens)
        
        return {'itens': itens, 'total': total, 'quantidade': qtd}
