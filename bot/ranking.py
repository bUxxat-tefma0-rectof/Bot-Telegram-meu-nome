from database.connection import get_db
from utils.helpers import formatar_moeda

class RankingService:
    
    @staticmethod
    def get_ranking(limite: int = 20) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            '''SELECT nome, total_gasto, pontos_fidelidade,
                      (SELECT COUNT(*) FROM pedidos WHERE cliente_id = c.id) as total_pedidos
               FROM clientes c
               WHERE bloqueado = 0 AND total_gasto > 0
               ORDER BY total_gasto DESC LIMIT ?''',
            (limite,)
        ).fetchall()]
    
    @staticmethod
    def get_ranking_afiliados(limite: int = 20) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            '''SELECT a.*, c.nome FROM afiliados a
               JOIN clientes c ON a.cliente_id = c.id
               WHERE a.ativo = 1
               ORDER BY a.total_comissoes DESC LIMIT ?''',
            (limite,)
        ).fetchall()]
    
    @staticmethod
    def get_ranking_semanal() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            """SELECT c.nome, COUNT(p.id) as pedidos, COALESCE(SUM(p.total), 0) as total
               FROM clientes c
               JOIN pedidos p ON c.id = p.cliente_id
               WHERE p.data_pedido >= datetime('now', '-7 days')
               AND p.pagamento_status = 'approved'
               GROUP BY c.id ORDER BY total DESC LIMIT 10"""
        ).fetchall()]
