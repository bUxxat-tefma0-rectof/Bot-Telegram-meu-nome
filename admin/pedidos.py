from database.connection import get_db
from utils.helpers import formatar_moeda, formatar_data
from services.notificacoes import NotificacaoService

class PedidosAdmin:
    
    @staticmethod
    def listar(filtro: str = 'todos', pagina: int = 1, limite: int = 20) -> dict:
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
            f'''SELECT p.*, c.nome as cliente_nome, c.telefone
                FROM pedidos p JOIN clientes c ON p.cliente_id = c.id
                {where} ORDER BY p.data_pedido DESC LIMIT ? OFFSET ?''',
            (limite, offset)
        ).fetchall()]
        
        return {'pedidos': pedidos, 'total': total, 'pagina': pagina}
    
    @staticmethod
    def get_detalhes(pedido_id: int) -> dict:
        db = get_db()
        pedido = db.execute('''
            SELECT p.*, c.nome, c.telefone, c.email, c.cpf,
                   e.logradouro, e.numero, e.bairro, e.cidade, e.estado, e.cep
            FROM pedidos p
            JOIN clientes c ON p.cliente_id = c.id
            LEFT JOIN enderecos e ON p.endereco_id = e.id
            WHERE p.id = ?
        ''', (pedido_id,)).fetchone()
        
        if not pedido: return None
        
        itens = [dict(r) for r in db.execute(
            'SELECT * FROM itens_pedido WHERE pedido_id = ?', (pedido_id,)
        ).fetchall()]
        
        result = dict(pedido)
        result['itens'] = itens
        return result
    
    @staticmethod
    def alterar_status(pedido_id: int, novo_status: str) -> dict:
        db = get_db()
        status_validos = ['recebido','confirmado','separando','embalando','entrega','entregue','cancelado','reembolsado']
        
        if novo_status not in status_validos:
            return {'sucesso': False, 'mensagem': 'Status inválido'}
        
        if novo_status == 'entregue':
            db.execute('UPDATE pedidos SET status = ?, data_entrega = datetime("now") WHERE id = ?',
                       (novo_status, pedido_id))
        else:
            db.execute('UPDATE pedidos SET status = ? WHERE id = ?', (novo_status, pedido_id))
        
        db.commit()
        
        # Notificar cliente
        pedido = db.execute('SELECT * FROM pedidos WHERE id = ?', (pedido_id,)).fetchone()
        if pedido:
            NotificacaoService.notificar_pedido_entregue(pedido['cliente_id'], dict(pedido))
        
        return {'sucesso': True, 'mensagem': f'Status: {novo_status}'}
    
    @staticmethod
    def cancelar_pedido(pedido_id: int) -> dict:
        db = get_db()
        pedido = db.execute('SELECT * FROM pedidos WHERE id = ?', (pedido_id,)).fetchone()
        if not pedido:
            return {'sucesso': False, 'mensagem': 'Pedido não encontrado'}
        
        # Devolve estoque
        itens = db.execute('SELECT * FROM itens_pedido WHERE pedido_id = ?', (pedido_id,)).fetchall()
        for item in itens:
            db.execute('UPDATE produtos SET estoque = estoque + ? WHERE nome = ?',
                       (item['quantidade'], item['produto_nome']))
        
        db.execute("UPDATE pedidos SET status = 'cancelado' WHERE id = ?", (pedido_id,))
        db.commit()
        
        return {'sucesso': True, 'mensagem': 'Pedido cancelado e estoque devolvido'}
