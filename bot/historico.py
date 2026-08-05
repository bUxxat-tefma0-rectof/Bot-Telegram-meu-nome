from database.connection import get_db
from utils.helpers import formatar_moeda, formatar_data

class HistoricoService:
    
    @staticmethod
    def get_compras(user_id: int, limite: int = 50) -> list:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return []
        
        return [dict(r) for r in db.execute(
            '''SELECT p.numero, p.total, p.status, p.pagamento_metodo, p.data_pedido,
                      COUNT(ip.id) as total_itens
               FROM pedidos p
               LEFT JOIN itens_pedido ip ON p.id = ip.pedido_id
               WHERE p.cliente_id = ?
               GROUP BY p.id
               ORDER BY p.data_pedido DESC LIMIT ?''',
            (cliente['id'], limite)
        ).fetchall()]
    
    @staticmethod
    def get_gastos_por_mes(user_id: int) -> list:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return []
        
        return [dict(r) for r in db.execute(
            """SELECT strftime('%Y-%m', data_pedido) as mes, COUNT(*) as pedidos, SUM(total) as total
               FROM pedidos WHERE cliente_id = ? AND pagamento_status = 'approved'
               GROUP BY strftime('%Y-%m', data_pedido) ORDER BY mes DESC LIMIT 12""",
            (cliente['id'],)
        ).fetchall()]
    
    @staticmethod
    def get_produtos_mais_comprados(user_id: int, limite: int = 10) -> list:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return []
        
        return [dict(r) for r in db.execute(
            '''SELECT ip.produto_nome, COUNT(*) as vezes, SUM(ip.quantidade) as total_qtd,
                      SUM(ip.preco_unitario * ip.quantidade) as total_gasto
               FROM itens_pedido ip
               JOIN pedidos p ON ip.pedido_id = p.id
               WHERE p.cliente_id = ?
               GROUP BY ip.produto_nome ORDER BY vezes DESC LIMIT ?''',
            (cliente['id'], limite)
        ).fetchall()]
