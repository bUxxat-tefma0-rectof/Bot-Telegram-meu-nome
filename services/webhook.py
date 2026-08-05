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
            pedido = db.execute('SELECT * FROM pedidos WHERE pagamento_id = ?', (payment_id,)).fetchone()
            
            if not pedido:
                recarga = db.execute('SELECT * FROM recargas WHERE payment_id = ?', (payment_id,)).fetchone()
                if recarga:
                    if action == 'payment.updated':
                        db.execute("UPDATE recargas SET status = 'aprovado' WHERE payment_id = ?", (payment_id,))
                        db.execute('UPDATE clientes SET saldo = saldo + ? WHERE id = ?', (recarga['valor'], recarga['cliente_id']))
                        db.commit()
                        return {'sucesso': True, 'tipo': 'recarga'}
                
                return {'sucesso': False, 'mensagem': 'Pedido/Recarga não encontrado'}
            
            if action == 'payment.updated':
                self.pix_service.verificar_manualmente(pedido['id'])
                return {'sucesso': True, 'tipo': 'pedido'}
            
            return {'sucesso': True, 'mensagem': 'Webhook processado'}
            
        except Exception as e:
            logger.error(f'Erro webhook: {e}')
            return {'sucesso': False, 'mensagem': str(e)}
    
    def verificar_assinatura(self, data: str, signature: str, secret: str) -> bool:
        expected = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
