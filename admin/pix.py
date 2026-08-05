from database.connection import get_db
from services.pix import PixService
from services.logs import LogService
from utils.helpers import formatar_moeda

class PixAdmin:
    
    def __init__(self):
        self.pix_service = PixService()
    
    def verificar_pagamento(self, pedido_id: int) -> dict:
        return self.pix_service.verificar_manualmente(pedido_id)
    
    @staticmethod
    def get_pix_pendentes() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT p.*, c.nome as cliente_nome, c.telefone FROM pedidos p JOIN clientes c ON p.cliente_id = c.id WHERE p.pagamento_metodo = 'pix' AND p.pagamento_status = 'pendente' ORDER BY p.data_pedido"
        ).fetchall()]
    
    @staticmethod
    def get_pix_aprovados(limite: int = 50) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT p.*, c.nome as cliente_nome FROM pedidos p JOIN clientes c ON p.cliente_id = c.id WHERE p.pagamento_status = 'approved' ORDER BY p.data_pedido DESC LIMIT ?",
            (limite,)
        ).fetchall()]
    
    @staticmethod
    def get_pix_expirados() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT p.*, c.nome FROM pedidos p JOIN clientes c ON p.cliente_id = c.id WHERE p.pagamento_metodo = 'pix' AND p.pagamento_status = 'pendente' AND p.data_pedido < datetime('now', '-30 minutes') ORDER BY p.data_pedido"
        ).fetchall()]
    
    @staticmethod
    def aprovar_manualmente(pedido_id: int) -> dict:
        db = get_db()
        pedido = db.execute('SELECT * FROM pedidos WHERE id = ?', (pedido_id,)).fetchone()
        
        if not pedido:
            return {'sucesso': False, 'mensagem': 'Pedido não encontrado'}
        
        db.execute("UPDATE pedidos SET pagamento_status = 'approved', status = 'confirmado', data_pagamento = datetime('now') WHERE id = ?",
                   (pedido_id,))
        
        # Atualiza cliente
        db.execute('UPDATE clientes SET total_gasto = total_gasto + ? WHERE id = ?',
                   (pedido['total'], pedido['cliente_id']))
        
        # Cashback
        cashback = pedido['total'] * 0.02
        db.execute('UPDATE clientes SET cashback = cashback + ? WHERE id = ?',
                   (cashback, pedido['cliente_id']))
        
        # Pontos
        pontos = int(pedido['total'])
        db.execute('UPDATE clientes SET pontos_fidelidade = pontos_fidelidade + ? WHERE id = ?',
                   (pontos, pedido['cliente_id']))
        
        db.commit()
        
        LogService.registrar(pedido['cliente_id'], 'pagamento_aprovado_manual', 'pix',
                            f'Aprovação manual do pedido {pedido["numero"]}')
        
        return {'sucesso': True, 'mensagem': 'Pagamento aprovado manualmente!'}
    
    @staticmethod
    def reprovar_manualmente(pedido_id: int) -> dict:
        db = get_db()
        db.execute("UPDATE pedidos SET pagamento_status = 'rejected' WHERE id = ?", (pedido_id,))
        db.commit()
        return {'sucesso': True, 'mensagem': 'Pagamento reprovado!'}
    
    @staticmethod
    def verificar_todos_pendentes() -> dict:
        peds = PixAdmin.get_pix_pendentes()
        pix_service = PixService()
        
        aprovados = 0
        reprovados = 0
        expirados = 0
        
        for p in peds:
            result = pix_service.verificar_manualmente(p['id'])
            if result.get('aprovado'):
                aprovados += 1
            elif result.get('recusado'):
                reprovados += 1
            else:
                expirados += 1
        
        return {
            'sucesso': True,
            'total': len(peds),
            'aprovados': aprovados,
            'reprovados': reprovados,
            'expirados': expirados
        }
