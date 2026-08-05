from services.pagamento import PagamentoService
from config.pagamentos import PagamentoConfig
from database.connection import get_db
import logging

logger = logging.getLogger(__name__)

class GatewayService:
    def __init__(self):
        self.gateways = {
            'mercadopago': PagamentoService(),
            'pix_manual': None
        }
        self.gateway_ativo = 'mercadopago'
    
    def get_gateway_ativo(self):
        db = get_db()
        config = db.execute("SELECT valor FROM configuracoes WHERE chave = 'gateway_ativo'").fetchone()
        if config:
            self.gateway_ativo = config['valor']
        return self.gateway_ativo
    
    def gerar_pix(self, valor: float, descricao: str, pedido_numero: str) -> dict:
        gateway = self.get_gateway_ativo()
        
        if gateway == 'mercadopago':
            return self.gateways['mercadopago'].gerar_pix(valor, descricao, pedido_numero)
        elif gateway == 'pix_manual':
            return self.gerar_pix_manual(valor, descricao, pedido_numero)
        
        return {'sucesso': False, 'mensagem': 'Gateway não configurado'}
    
    def gerar_pix_manual(self, valor: float, descricao: str, pedido_numero: str) -> dict:
        chave_pix = PagamentoConfig.CHAVE_PIX
        nome = PagamentoConfig.NOME_RECEBEDOR
        cidade = PagamentoConfig.CIDADE_RECEBEDOR
        
        pix_code = f"00020126580014br.gov.bcb.pix0136{chave_pix}5204000053039865405{valor:.2f}5802BR5913{nome}6008{cidade}62070503***6304"
        
        import qrcode
        from io import BytesIO
        
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(pix_code)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')
        
        return {
            'sucesso': True,
            'payment_id': f'manual_{pedido_numero}',
            'copia_cola': pix_code,
            'qr_buffer': buf.getvalue(),
            'status': 'pending'
        }
    
    def verificar_pagamento(self, payment_id: str) -> dict:
        if payment_id.startswith('manual_'):
            return {'status': 'pending', 'aprovado': False, 'pendente': True}
        
        return self.gateways['mercadopago'].verificar_pagamento(payment_id)
