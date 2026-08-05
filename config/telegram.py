from .geral import Config

class TelegramConfig:
    """Configurações específicas do Telegram"""
    
    # Comportamento do bot
    EDITAR_MENSAGENS = True  # Editar mensagens em vez de enviar novas
    USAR_REPLY = True  # Usar ForceReply para respostas
    TEMPO_EDICAO = 48  # Horas máximas para editar mensagem
    
    # Polling
    POLLING_INTERVAL = 0.5  # segundos
    POLLING_TIMEOUT = 10  # segundos
    
    # Limites
    MAX_BOTOES_POR_LINHA = 2
    MAX_PRODUTOS_POR_PAGINA = 12
    MAX_CATEGORIAS_POR_PAGINA = 20
    
    # Parse mode padrão
    PARSE_MODE = 'Markdown'
    
    @classmethod
    def get_bot_token_cliente(cls):
        return Config.BOT_TOKEN_CLIENTE
    
    @classmethod
    def get_bot_token_admin(cls):
        return Config.BOT_TOKEN_ADMIN
    
    @classmethod
    def get_admin_ids(cls):
        return Config.ADMIN_IDS
