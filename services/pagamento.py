import mercadopago
from config.pagamentos import PagamentoConfig
from config.geral import Config
from utils.helpers import formatar_moeda, gerar_numero_pedido
from database.connection import get_db
import qrcode
from io import BytesIO
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PagamentoService:
    def __init__(self):
        self.sdk = mercadopago.SDK(PagamentoConfig.ACCESS_TOKEN)
    
    def gerar_pix(self, valor: float, descricao: str, pedido_numero: str) -> dict:
        try:
            payment_data = {
                "transaction_amount": float(valor),
                "description": descricao[:100] if descricao else f"Pedido {pedido_numero}",
                "payment_method_id": "pix",
                "payer": {
                    "email": f"pedido{pedido_numero}@lojadigital.com",
                    "first_name": "Cliente"
                }
            }
            
            result = self.sdk.payment().create(payment_data)
            
            if result.get('status') in [200, 201]:
                response = result['response']
                pix_data = response['point_of_interaction']['transaction_data']
                
                qr = qrcode.QRCode(version=1, box_size=6, border=2)
                qr.add_data(pix_data['qr_code'])
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buf = BytesIO()
                img.save(buf, format='PNG')
                
                logger.info(f'PIX gerado: {response["id"]} - R$ {valor}')
                
                return {
                    'sucesso': True,
                    'payment_id': response['id'],
                    'qr_code_base64': pix_data.get('qr_code_base64', ''),
                    'copia_cola': pix_data['qr_code'],
                    'qr_buffer': buf.getvalue(),
                    'status': response['status'],
                    'data_expiracao': response.get('date_of_expiration', '')
                }
            
            logger.error(f'Erro Mercado Pago: {result}')
            return {'sucesso': False, 'mensagem': 'Erro ao gerar PIX. Tente novamente.'}
            
        except Exception as e:
            logger.error(f'Exceção PIX: {e}')
            return {'sucesso': False, 'mensagem': f'Erro: {str(e)}'}
    
    def verificar_pagamento(self, payment_id: str) -> dict:
        try:
            result = self.sdk.payment().get(payment_id)
            
            if result.get('status') == 200:
                response = result['response']
                status = response['status']
                
                return {
                    'status': status,
                    'aprovado': status == 'approved',
                    'recusado': status == 'rejected',
                    'pendente': status == 'pending',
                    'detalhe': response.get('status_detail', ''),
                    'valor': response.get('transaction_amount', 0),
                    'data_aprovacao': response.get('date_approved', '')
                }
            
            return {'status': 'error', 'aprovado': False}
        except Exception as e:
            logger.error(f'Erro ao verificar: {e}')
            return {'status': 'error', 'aprovado': False}
    
    def cancelar_pagamento(self, payment_id: str) -> dict:
        try:
            result = self.sdk.payment().cancel(payment_id)
            if result.get('status') == 200:
                return {'sucesso': True, 'status': result['response']['status']}
            return {'sucesso': False, 'mensagem': 'Erro ao cancelar'}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    def reembolsar(self, payment_id: str, valor: float = None) -> dict:
        try:
            if valor:
                result = self.sdk.payment().refund(payment_id, {"amount": float(valor)})
            else:
                result = self.sdk.payment().refund(payment_id)
            
            if result.get('status') == 200:
                return {'sucesso': True, 'mensagem': 'Reembolso realizado!'}
            return {'sucesso': False, 'mensagem': 'Erro ao reembolsar'}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    def processar_recarga(self, cliente_id: int, valor: float) -> dict:
        db = get_db()
        numero = f"REC{int(datetime.now().timestamp())}"
        
        result = self.gerar_pix(valor, f"Recarga de {formatar_moeda(valor)}", numero)
        
        if result['sucesso']:
            db.execute('''
                INSERT INTO recargas (cliente_id, valor, payment_id, status, data)
                VALUES (?, ?, ?, 'pendente', datetime('now'))
            ''', (cliente_id, valor, result['payment_id']))
            db.commit()
        
        return result
