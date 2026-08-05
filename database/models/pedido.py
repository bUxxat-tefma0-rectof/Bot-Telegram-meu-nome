from database.connection import get_db
from typing import List, Optional, Dict
from utils.helpers import formatar_moeda, formatar_data

class PedidoModel:
    
    STATUS_FLUXO = ['recebido', 'confirmado', 'separando', 'embalando', 'entrega', 'entregue']
    
    @staticmethod
    def get_by_id(pedido_id: int) -> Optional[Dict]:
        db = get_db()
        row = db.execute('''
            SELECT p.*, c.nome as cliente_nome, c.telefone, c.email,
                   e.logradouro, e.numero, e.bairro, e.cidade, e.estado
            FROM pedidos p
            JOIN clientes c ON p.cliente_id = c.id
            LEFT JOIN enderecos e ON p.endereco_id = e.id
            WHERE p.id = ?
        ''', (pedido_id,)).fetchone()
        
        if not row:
            return None
        
        pedido = dict(row)
        pedido['itens'] = [dict(r) for r in db.execute(
            'SELECT * FROM itens_pedido WHERE pedido_id = ?', (pedido_id,)
        ).fetchall()]
        pedido['total_formatado'] = formatar_moeda(pedido['total'])
        pedido['data_formatada'] = formatar_data(pedido['data_pedido'])
        
        return pedido
    
    @staticmethod
    def criar(cliente_id: int, dados: Dict) -> int:
        db = get_db()
        cursor = db.execute('''
            INSERT INTO pedidos (numero, cliente_id, endereco_id, tipo_entrega, status,
                subtotal, taxa_entrega, desconto, total, cupom, comentario, pagamento_metodo)
            VALUES (?, ?, ?, ?, 'recebido', ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dados['numero'], cliente_id, dados.get('endereco_id'),
            dados.get('tipo_entrega', 'entrega'),
            dados.get('subtotal', 0), dados.get('taxa_entrega', 0),
            dados.get('desconto', 0), dados.get('total', 0),
            dados.get('cupom'), dados.get('comentario'),
            dados.get('pagamento_metodo', 'pix')
        ))
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def adicionar_item(pedido_id: int, produto_id: int, nome: str, quantidade: int, preco: float, comentario: str = None):
        db = get_db()
        db.execute('''
            INSERT INTO itens_pedido (pedido_id, produto_id, produto_nome, quantidade, preco_unitario, comentario)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (pedido_id, produto_id, nome, quantidade, preco, comentario))
        db.commit()
    
    @staticmethod
    def atualizar_status(pedido_id: int, status: str) -> bool:
        if status not in PedidoModel.STATUS_FLUXO + ['cancelado', 'reembolsado']:
            return False
        
        db = get_db()
        if status == 'entregue':
            db.execute('UPDATE pedidos SET status = ?, data_entrega = datetime("now") WHERE id = ?',
                       (status, pedido_id))
        else:
            db.execute('UPDATE pedidos SET status = ? WHERE id = ?', (status, pedido_id))
        db.commit()
        return True
    
    @staticmethod
    def atualizar_pagamento(pedido_id: int, payment_id: str, qrcode: str = None, status: str = 'pendente') -> bool:
        db = get_db()
        db.execute('''
            UPDATE pedidos SET pagamento_id = ?, pagamento_qrcode = ?, pagamento_status = ?
            WHERE id = ?
        ''', (payment_id, qrcode, status, pedido_id))
        db.commit()
        return True
    
    @staticmethod
    def confirmar_pagamento(pedido_id: int) -> bool:
        db = get_db()
        db.execute('''
            UPDATE pedidos SET pagamento_status = 'approved', status = 'confirmado', data_pagamento = datetime('now')
            WHERE id = ?
        ''', (pedido_id,))
        db.commit()
        return True
    
    @staticmethod
    def cancelar(pedido_id: int) -> bool:
        db = get_db()
        pedido = db.execute('SELECT * FROM pedidos WHERE id = ?', (pedido_id,)).fetchone()
        if not pedido or pedido['status'] in ['entregue', 'cancelado']:
            return False
        
        # Devolve estoque
        itens = db.execute('SELECT * FROM itens_pedido WHERE pedido_id = ?', (pedido_id,)).fetchall()
        for item in itens:
            db.execute('UPDATE produtos SET estoque = estoque + ? WHERE nome = ?',
                       (item['quantidade'], item['produto_nome']))
        
        db.execute("UPDATE pedidos SET status = 'cancelado' WHERE id = ?", (pedido_id,))
        db.commit()
        return True
    
    @staticmethod
    def listar_por_cliente(cliente_id: int, limite: int = 20) -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM pedidos WHERE cliente_id = ? ORDER BY data_pedido DESC LIMIT ?',
            (cliente_id, limite)
        ).fetchall()]
    
    @staticmethod
    def listar_todos(filtro: str = 'todos', pagina: int = 1, limite: int = 20) -> Dict:
        db = get_db()
        where = ''
        
        if filtro == 'pendentes':
            where = "WHERE status IN ('recebido','confirmado','separando','embalando')"
        elif filtro == 'entrega':
            where = "WHERE status = 'entrega'"
        elif filtro == 'entregues':
            where = "WHERE status = 'entregue'"
        elif filtro == 'cancelados':
            where = "WHERE status = 'cancelado'"
        elif filtro == 'hoje':
            where = "WHERE date(data_pedido) = date('now')"
        
        total = db.execute(f'SELECT COUNT(*) as t FROM pedidos {where}').fetchone()['t']
        offset = (pagina - 1) * limite
        
        pedidos = [dict(r) for r in db.execute(
            f'''SELECT p.*, c.nome as cliente_nome
                FROM pedidos p JOIN clientes c ON p.cliente_id = c.id
                {where} ORDER BY p.data_pedido DESC LIMIT ? OFFSET ?''',
            (limite, offset)
        ).fetchall()]
        
        return {'pedidos': pedidos, 'total': total, 'pagina': pagina}
