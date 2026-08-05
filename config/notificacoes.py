class NotificacaoConfig:
    """Configurações de notificações"""
    
    # Canais
    TELEGRAM_ATIVO = True
    EMAIL_ATIVO = False
    
    # Eventos que geram notificações
    EVENTOS = {
        'pedido_recebido': True,
        'pagamento_aprovado': True,
        'pagamento_recusado': True,
        'pix_expirado': True,
        'pedido_entregue': True,
        'estoque_baixo': True,
        'novo_cliente': False,
        'nova_avaliacao': False,
        'saque_solicitado': True,
        'promocao_nova': True
    }
    
    # Intervalos
    INTERVALO_VERIFICACAO_PIX = 10  # segundos
    MAX_VERIFICACOES_PIX = 30  # máximo de tentativas
    
    @classmethod
    def is_ativo(cls, evento: str) -> bool:
        return cls.EVENTOS.get(evento, False)
