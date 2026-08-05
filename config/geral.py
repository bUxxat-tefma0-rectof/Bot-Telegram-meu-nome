import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot
    BOT_TOKEN_CLIENTE = os.getenv('BOT_TOKEN_CLIENTE', '')
    BOT_TOKEN_ADMIN = os.getenv('BOT_TOKEN_ADMIN', '')
    ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', './loja.db')
    
    # Pagamento
    MERCADO_PAGO_ACCESS_TOKEN = os.getenv('MERCADO_PAGO_ACCESS_TOKEN', '')
    TEMPO_EXPIRACAO_PIX = int(os.getenv('TEMPO_EXPIRACAO_PIX', '30'))
    
    # Loja
    NOME_LOJA = os.getenv('NOME_LOJA', 'Loja Digital')
    PEDIDO_MINIMO = float(os.getenv('PEDIDO_MINIMO', '10'))
    TAXA_ENTREGA = float(os.getenv('TAXA_ENTREGA_PADRAO', '5'))
    
    # Afiliados
    COMISSAO_AFILIADO = float(os.getenv('COMISSAO_AFILIADO', '5'))
    
    # URLs
    RENDER_EXTERNAL_URL = os.getenv('RENDER_EXTERNAL_URL', '')
    
    # Segurança
    JWT_SECRET = os.getenv('JWT_SECRET', 'chave_secreta_padrao')
    MAX_TENTATIVAS = int(os.getenv('MAX_TENTATIVAS', '5'))
