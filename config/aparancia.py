from database.connection import get_db

class AparenciaConfig:
    """Configurações de aparência (editáveis pelo painel)"""
    
    @classmethod
    def get_config(cls, chave: str, default: str = '') -> str:
        try:
            db = get_db()
            row = db.execute('SELECT valor FROM configuracoes WHERE chave = ?', (chave,)).fetchone()
            return row['valor'] if row else default
        except:
            return default
    
    @classmethod
    def get_cor_primaria(cls) -> str:
        return cls.get_config('cor_primaria', '#6366f1')
    
    @classmethod
    def get_cor_secundaria(cls) -> str:
        return cls.get_config('cor_secundaria', '#ec4899')
    
    @classmethod
    def get_cor_fundo(cls) -> str:
        return cls.get_config('cor_fundo', '#f8fafc')
    
    @classmethod
    def get_tema(cls) -> str:
        return cls.get_config('tema', 'light')
    
    @classmethod
    def get_nome_loja(cls) -> str:
        return cls.get_config('nome_loja', 'Loja Digital')
    
    @classmethod
    def get_logo(cls) -> str:
        return cls.get_config('logo', '')
    
    @classmethod
    def get_banner(cls) -> str:
        return cls.get_config('banner', '')
    
    @classmethod
    def get_emoji_loja(cls) -> str:
        return cls.get_config('emoji_loja', '🛒')
    
    @classmethod
    def get_todas_cores(cls) -> dict:
        return {
            'primaria': cls.get_cor_primaria(),
            'secundaria': cls.get_cor_secundaria(),
            'fundo': cls.get_cor_fundo(),
            'texto': cls.get_config('cor_texto', '#1e293b'),
            'texto_claro': cls.get_config('cor_texto_claro', '#64748b'),
            'borda': cls.get_config('cor_borda', '#e2e8f0'),
            'sucesso': cls.get_config('cor_sucesso', '#10b981'),
            'erro': cls.get_config('cor_erro', '#ef4444'),
            'aviso': cls.get_config('cor_aviso', '#f59e0b')
        }
