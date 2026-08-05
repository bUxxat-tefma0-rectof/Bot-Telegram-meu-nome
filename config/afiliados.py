from .geral import Config

class AfiliadoConfig:
    """Configurações do sistema de afiliados"""
    
    COMISSAO_PADRAO = Config.COMISSAO_AFILIADO  # percentual
    NIVEL_MINIMO_SAQUE = 50.00  # valor mínimo para saque
    PRAZO_SAQUE = 7  # dias para processar saque
    
    # Níveis de afiliado
    NIVEIS = {
        1: {'nome': 'Bronze', 'comissao': 5, 'min_vendas': 0},
        2: {'nome': 'Prata', 'comissao': 7, 'min_vendas': 1000},
        3: {'nome': 'Ouro', 'comissao': 10, 'min_vendas': 5000},
        4: {'nome': 'Diamante', 'comissao': 15, 'min_vendas': 20000}
    }
    
    @classmethod
    def get_comissao_padrao(cls):
        return cls.COMISSAO_PADRAO
    
    @classmethod
    def get_nivel(cls, total_vendas: float) -> int:
        for nivel_id in sorted(cls.NIVEIS.keys(), reverse=True):
            if total_vendas >= cls.NIVEIS[nivel_id]['min_vendas']:
                return nivel_id
        return 1
