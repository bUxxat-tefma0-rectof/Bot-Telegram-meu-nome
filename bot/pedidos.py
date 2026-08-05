from database.connection import get_db
from utils.helpers import formatar_moeda, formatar_data

class PedidosService:
    
    @staticmethod
    def listar(user_id: int, limite: int = 20) -> list:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return []
        
        return [dict(r) for r in db.execute(
            'SELECT * FROM pedidos WHERE cliente_id = ? ORDER BY data_pedido DESC LIMIT ?',
            (cliente['id'], limite)
        ).fetchall()]
    
    @staticmethod
    def get_detalhes(pedido_id: int, user_id: int = None) -> dict:
        db = get_db()
        
        if user_id:
            cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
            if not cliente: return None
            pedido = db.execute('SELECT * FROM pedidos WHERE id = ? AND cliente_id = ?',
                               (pedido_id, cliente['id'])).fetchone()
        else:
            pedido = db.execute('SELECT * FROM pedidos WHERE id = ?', (pedido_id,)).fetchone()
        
        if not pedido: return None
        
        itens = [dict(r) for r in db.execute(
            'SELECT * FROM itens_pedido WHERE pedido_id = ?', (pedido_id,)
        ).fetchall()]
        
        resultado = dict(pedido)
        resultado['itens'] = itens
        resultado['total_formatado'] = formatar_moeda(resultado['total'])
        resultado['data_formatada'] = formatar_data(resultado['data_pedido'])
        
        return resultado
    
    @staticmethod
    def get_status_fluxo(status: str) -> list:
        fluxo = [
            {'status': 'recebido', 'label': 'Recebido', 'emoji': '📥'},
            {'status': 'confirmado', 'label': 'Confirmado', 'emoji': '✅'},
            {'status': 'separando', 'label': 'Separando', 'emoji': '📦'},
            {'status': 'embalando', 'label': 'Embalando', 'emoji': '🎁'},
            {'status': 'entrega', 'label': 'Em Entrega', 'emoji': '🛵'},
            {'status': 'entregue', 'label': 'Entregue', 'emoji': '🏠'}
        ]
        
        status_index = next((i for i, s in enumerate(fluxo) if s['status'] == status), 0)
        
        for i, s in enumerate(fluxo):
            s['concluido'] = i <= status_index
            s['atual'] = i == status_index
        
        return fluxo
    
    @staticmethod
    def cancelar(user_id: int, pedido_id: int) -> dict:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return {'sucesso': False, 'mensagem': 'Cliente não encontrado'}
        
        pedido = db.execute('SELECT * FROM pedidos WHERE id = ? AND cliente_id = ?',
                           (pedido_id, cliente['id'])).fetchone()
        if not pedido: return {'sucesso': False, 'mensagem': 'Pedido não encontrado'}
        
        if pedido['status'] in ['entregue', 'cancelado', 'reembolsado']:
            return {'sucesso': False, 'mensagem': 'Pedido não pode ser cancelado'}
        
        # Devolve estoque
        itens = db.execute('SELECT * FROM itens_pedido WHERE pedido_id = ?', (pedido_id,)).fetchall()
        for item in itens:
            db.execute('UPDATE produtos SET estoque = estoque + ? WHERE nome = ?',
                       (item['quantidade'], item['produto_nome']))
        
        db.execute("UPDATE pedidos SET status = 'cancelado' WHERE id = ?", (pedido_id,))
        db.commit()
        
        return {'sucesso': True, 'mensagem': 'Pedido cancelado com sucesso'}
