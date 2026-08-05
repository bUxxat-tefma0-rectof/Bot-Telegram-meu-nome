import hashlib
import hmac
from database.connection import get_db
from services.pix import PixService
from services.logs import LogService
import logging

logger = logging.getLogger(__name__)

class WebhookService:
    
    def __init__(self):
        self.pix_service = PixService()
    
    def processar_webhook_mercadopago(self, data: dict) -> dict:
        try:
            action = data.get('action', '')
            payment_id = data.get('data', {}).get('id', '')
            
            if not payment_id:
                return {'sucesso': False, 'mensagem': 'ID de pagamento não encontrado'}
            
            db = get_db()
            
            # Verifica se é de um pedido
            pedido = db.execute('SELECT * FROM pedidos WHERE pagamento_id = ?', (payment_id,)).fetchone()
            
            if pedido:
                if action == 'payment.updated':
                    result = self.pix_service.verificar_manualmente(pedido['id'])
                    LogService.registrar(
                        pedido['cliente_id'], 'webhook_pagamento', 'webhooks',
                        f'Webhook processado para pedido {pedido["numero"]}: {result.get("status", "N/A")}'
                    )
                    return {'sucesso': True, 'tipo': 'pedido', 'pedido_id': pedido['id']}
            
            # Verifica se é de uma recarga
            recarga = db.execute('SELECT * FROM recargas WHERE payment_id = ?', (payment_id,)).fetchone()
            
            if recarga:
                if action == 'payment.updated':
                    db.execute("UPDATE recargas SET status = 'aprovado' WHERE payment_id = ?", (payment_id,))
                    db.execute('UPDATE clientes SET saldo = saldo + ? WHERE id = ?',
                              (recarga['valor'], recarga['cliente_id']))
                    db.commit()
                    
                    LogService.registrar(
                        recarga['cliente_id'], 'webhook_recarga', 'webhooks',
                        f'Recarga de R$ {recarga["valor"]:.2f} aprovada via webhook'
                    )
                    return {'sucesso': True, 'tipo': 'recarga'}
            
            return {'sucesso': True, 'mensagem': 'Webhook processado (nenhuma ação necessária)'}
            
        except Exception as e:
            logger.error(f'Erro ao processar webhook: {e}')
            LogService.registrar(None, 'webhook_erro', 'webhooks', str(e))
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def verificar_assinatura(data: str, signature: str, secret: str) -> bool:
        if not secret:
            return True
        expected = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
