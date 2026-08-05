from database.connection import get_db
from utils.helpers import formatar_moeda, formatar_data
from services.exportacao import ExportacaoService
from services.pdf import PDFService

class RelatoriosAdmin:
    
    @staticmethod
    def vendas_por_periodo(inicio: str, fim: str) -> dict:
        db = get_db()
        
        pedidos = [dict(r) for r in db.execute(
            "SELECT * FROM pedidos WHERE date(data_pedido) BETWEEN ? AND ? ORDER BY data_pedido",
            (inicio, fim)
        ).fetchall()]
        
        total_vendas = sum(p['total'] for p in pedidos if p['pagamento_status'] == 'approved')
        total_pedidos = len(pedidos)
        ticket_medio = total_vendas / total_pedidos if total_pedidos > 0 else 0
        
        return {
            'periodo': {'inicio': inicio, 'fim': fim},
            'total_pedidos': total_pedidos,
            'total_vendas': formatar_moeda(total_vendas),
            'ticket_medio': formatar_moeda(ticket_medio),
            'pedidos': pedidos[:50]
        }
    
    @staticmethod
    def produtos_mais_vendidos(limite: int = 20) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            '''SELECT ip.produto_nome, COUNT(*) as vendas, SUM(ip.quantidade) as unidades,
                      SUM(ip.preco_unitario * ip.quantidade) as receita
               FROM itens_pedido ip
               JOIN pedidos p ON ip.pedido_id = p.id
               WHERE p.pagamento_status = 'approved'
               GROUP BY ip.produto_nome ORDER BY vendas DESC LIMIT ?''',
            (limite,)
        ).fetchall()]
    
    @staticmethod
    def clientes_top(limite: int = 20) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            '''SELECT nome, telefone, total_gasto, pontos_fidelidade,
                      (SELECT COUNT(*) FROM pedidos WHERE cliente_id = c.id) as total_pedidos
               FROM clientes c ORDER BY total_gasto DESC LIMIT ?''',
            (limite,)
        ).fetchall()]
    
    @staticmethod
    def resumo_mensal() -> dict:
        db = get_db()
        return {
            'vendas': [dict(r) for r in db.execute(
                "SELECT strftime('%Y-%m', data_pedido) as mes, COUNT(*) as pedidos, COALESCE(SUM(total), 0) as faturamento FROM pedidos WHERE pagamento_status = 'approved' GROUP BY strftime('%Y-%m', data_pedido) ORDER BY mes DESC LIMIT 12"
            ).fetchall()],
            'clientes': [dict(r) for r in db.execute(
                "SELECT strftime('%Y-%m', data_cadastro) as mes, COUNT(*) as novos FROM clientes GROUP BY strftime('%Y-%m', data_cadastro) ORDER BY mes DESC LIMIT 12"
            ).fetchall()]
        }
    
    @staticmethod
    def gerar_pdf(tipo: str = 'vendas') -> bytes:
        db = get_db()
        
        if tipo == 'vendas':
            pedidos = [dict(r) for r in db.execute(
                "SELECT p.*, c.nome FROM pedidos p JOIN clientes c ON p.cliente_id = c.id WHERE strftime('%Y-%m', p.data_pedido) = strftime('%Y-%m', 'now') ORDER BY p.data_pedido DESC"
            ).fetchall()]
            itens = [dict(r) for r in db.execute(
                "SELECT i.* FROM itens_pedido i JOIN pedidos p ON i.pedido_id = p.id WHERE strftime('%Y-%m', p.data_pedido) = strftime('%Y-%m', 'now')"
            ).fetchall()]
            return PDFService.gerar_relatorio(pedidos, itens)
        
        return None
