from database.connection import get_db
from utils.helpers import formatar_moeda

class FinanceiroAdmin:
    
    @staticmethod
    def get_resumo() -> dict:
        db = get_db()
        
        return {
            'faturamento_total': db.execute("SELECT COALESCE(SUM(total), 0) as t FROM pedidos WHERE pagamento_status = 'approved'").fetchone()['t'],
            'faturamento_mes': db.execute("SELECT COALESCE(SUM(total), 0) as t FROM pedidos WHERE pagamento_status = 'approved' AND strftime('%Y-%m', data_pedido) = strftime('%Y-%m', 'now')").fetchone()['t'],
            'faturamento_hoje': db.execute("SELECT COALESCE(SUM(total), 0) as t FROM pedidos WHERE pagamento_status = 'approved' AND date(data_pedido) = date('now')").fetchone()['t'],
            'total_pix': db.execute("SELECT COALESCE(SUM(total), 0) as t FROM pedidos WHERE pagamento_metodo = 'pix' AND pagamento_status = 'approved'").fetchone()['t'],
            'total_dinheiro': db.execute("SELECT COALESCE(SUM(total), 0) as t FROM pedidos WHERE pagamento_metodo = 'dinheiro' AND pagamento_status = 'approved'").fetchone()['t'],
            'total_taxas': db.execute("SELECT COALESCE(SUM(taxa_entrega), 0) as t FROM pedidos WHERE pagamento_status = 'approved'").fetchone()['t'],
            'total_descontos': db.execute("SELECT COALESCE(SUM(desconto), 0) as t FROM pedidos WHERE pagamento_status = 'approved'").fetchone()['t'],
            'total_reembolsos': db.execute("SELECT COALESCE(SUM(total), 0) as t FROM pedidos WHERE status = 'reembolsado'").fetchone()['t']
        }
    
    @staticmethod
    def get_extrato(limite: int = 50) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT * FROM pedidos WHERE pagamento_status = 'approved' ORDER BY data_pedido DESC LIMIT ?",
            (limite,)
        ).fetchall()]
    
    @staticmethod
    def get_recargas(limite: int = 50) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT r.*, c.nome FROM recargas r JOIN clientes c ON r.cliente_id = c.id ORDER BY r.data DESC LIMIT ?',
            (limite,)
        ).fetchall()]
