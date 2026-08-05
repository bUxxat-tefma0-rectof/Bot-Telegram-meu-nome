from database.connection import get_db
from services.pix import PixService
from utils.helpers import formatar_moeda

class PixAdmin:
    
    def __init__(self):
        self.pix_service = PixService()
    
    def verificar_pagamento_manual(self, pedido_id: int) -> dict:
        return self.pix_service.verificar_manualmente(pedido_id)
    
    @staticmethod
    def get_pix_pendentes() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT p.*, c.nome FROM pedidos p JOIN clientes c ON p.cliente_id = c.id WHERE p.pagamento_metodo = 'pix' AND p.pagamento_status = 'pendente' ORDER BY p.data_pedido"
        ).fetchall()]
    
    @staticmethod
    def get_pix_aprovados(limite: int = 50) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT p.*, c.nome FROM pedidos p JOIN clientes c ON p.cliente_id = c.id WHERE p.pagamento_status = 'approved' ORDER BY p.data_pedido DESC LIMIT ?",
            (limite,)
        ).fetchall()]
    
    @staticmethod
    def aprovar_manualmente(pedido_id: int) -> dict:
        db = get_db()
        db.execute("UPDATE pedidos SET pagamento_status = 'approved', status = 'confirmado' WHERE id = ?", (pedido_id,))
        db.commit()
        return {'sucesso': True, 'mensagem': 'Pagamento aprovado manualmente!'}
