from .geral import Config

class PagamentoConfig:
    """Configurações de pagamento"""
    
    # Mercado Pago
    ACCESS_TOKEN = Config.MERCADO_PAGO_ACCESS_TOKEN
    
    # PIX
    TEMPO_EXPIRACAO = Config.TEMPO_EXPIRACAO_PIX  # minutos
    CHAVE_PIX = ""
    NOME_RECEBEDOR = Config.NOME_LOJA
    CIDADE_RECEBEDOR = ""
    
    # Valores
    VALOR_MINIMO_RECARGA = 10.00
    VALOR_MAXIMO_RECARGA = 1000.00
    BONUS_RECARGA = 0  # percentual
    
    # Status
    APROVACAO_AUTOMATICA = True
    
    @classmethod
    def get_mercadopago_token(cls):
        return cls.ACCESS_TOKEN
