from database.connection import get_db
from utils.helpers import formatar_moeda, formatar_data
from datetime import datetime

class DashboardAdmin:
    
    @staticmethod
    def get_estatisticas() -> dict:
        db = get_db()
        
        hoje = datetime.now().strftime('%Y-%m-%d')
        mes = datetime.now().strftime('%Y-%m')
        
        return {
            'clientes': {
                'total': db.execute('SELECT COUNT(*) as t FROM clientes').fetchone()['t'],
                'novos_hoje': db.execute("SELECT COUNT(*) as t FROM clientes WHERE date(data_cadastro) = date('now')").fetchone()['t'],
                'novos_mes': db.execute("SELECT COUNT(*) as t FROM clientes WHERE strftime('%Y-%m', data_cadastro) = ?", (mes,)).fetchone()['t'],
                'bloqueados': db.execute('SELECT COUNT(*) as t FROM clientes WHERE bloqueado = 1').fetchone()['t']
            },
            'pedidos': {
                'total': db.execute('SELECT COUNT(*) as t FROM pedidos').fetchone()['t'],
                'hoje': db.execute("SELECT COUNT(*) as t FROM pedidos WHERE date(data_pedido) = date('now')").fetchone()['t'],
                'mes': db.execute("SELECT COUNT(*) as t FROM pedidos WHERE strftime('%Y-%m', data_pedido) = ?", (mes,)).fetchone()['t'],
                'pendentes': db.execute("SELECT COUNT(*) as t FROM pedidos WHERE status IN ('recebido','confirmado','separando','embalando')").fetchone()['t'],
                'em_entrega': db.execute("SELECT COUNT(*) as t FROM pedidos WHERE status = 'entrega'").fetchone()['t'],
                'entregues': db.execute("SELECT COUNT(*) as t FROM pedidos WHERE status = 'entregue'").fetchone()['t'],
                'cancelados': db.execute("SELECT COUNT(*) as t FROM pedidos WHERE status = 'cancelado'").fetchone()['t']
            },
            'faturamento': {
                'total': db.execute("SELECT COALESCE(SUM(total), 0) as t FROM pedidos WHERE pagamento_status = 'approved'").fetchone()['t'],
                'hoje': db.execute("SELECT COALESCE(SUM(total), 0) as t FROM pedidos WHERE pagamento_status = 'approved' AND date(data_pedido) = date('now')").fetchone()['t'],
                'mes': db.execute("SELECT COALESCE(SUM(total), 0) as t FROM pedidos WHERE pagamento_status = 'approved' AND strftime('%Y-%m', data_pedido) = ?", (mes,)).fetchone()['t']
            },
            'produtos': {
                'total': db.execute('SELECT COUNT(*) as t FROM produtos').fetchone()['t'],
                'ativos': db.execute('SELECT COUNT(*) as t FROM produtos WHERE disponivel = 1').fetchone()['t'],
                'estoque_baixo': db.execute('SELECT COUNT(*) as t FROM produtos WHERE estoque <= 10 AND disponivel = 1').fetchone()['t'],
                'sem_estoque': db.execute('SELECT COUNT(*) as t FROM produtos WHERE estoque <= 0 AND disponivel = 1').fetchone()['t']
            },
            'afiliados': {
                'total': db.execute('SELECT COUNT(*) as t FROM afiliados WHERE ativo = 1').fetchone()['t'],
                'comissoes': db.execute('SELECT COALESCE(SUM(total_comissoes), 0) as t FROM afiliados').fetchone()['t']
            }
        }
    
    @staticmethod
    def get_grafico_vendas(dias: int = 7) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            f"SELECT date(data_pedido) as dia, COUNT(*) as pedidos, COALESCE(SUM(total), 0) as faturamento FROM pedidos WHERE data_pedido >= date('now', '-{dias} days') AND pagamento_status = 'approved' GROUP BY date(data_pedido) ORDER BY dia"
        ).fetchall()]
    
    @staticmethod
    def get_top_produtos(limite: int = 10) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            '''SELECT produto_nome, COUNT(*) as vendas, SUM(quantidade) as unidades, SUM(preco_unitario * quantidade) as receita
               FROM itens_pedido GROUP BY produto_nome ORDER BY vendas DESC LIMIT ?''',
            (limite,)
        ).fetchall()]
