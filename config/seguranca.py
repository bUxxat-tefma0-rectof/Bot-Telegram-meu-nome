from .geral import Config

class SegurancaConfig:
    """Configurações de segurança"""
    
    # Rate limiting
    MAX_REQUISICOES_POR_MINUTO = 30
    BLOQUEIO_TEMPORARIO_MINUTOS = 5
    
    # Autenticação
    JWT_SECRET = Config.JWT_SECRET
    JWT_EXPIRACAO_HORAS = 24
    
    # Senhas
    MIN_CARACTERES_SENHA = 6
    EXIGIR_NUMEROS = False
    EXIGIR_MAIUSCULAS = False
    EXIGIR_ESPECIAIS = False
    
    # Anti-fraude
    MAX_COMPRAS_DIA = 50
    MAX_COMPRAS_HORA = 10
    MAX_VALOR_COMPRA = 5000.00
    
    # 2FA
    DOIS_FATORES_ATIVO = False
    
    @classmethod
    def get_jwt_secret(cls):
        return cls.JWT_SECRET
