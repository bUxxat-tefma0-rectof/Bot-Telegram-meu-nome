from database.connection import get_db

class ConfiguracoesService:
    
    @staticmethod
    def get_config(chave: str, default: str = '') -> str:
        db = get_db()
        row = db.execute('SELECT valor FROM configuracoes WHERE chave = ?', (chave,)).fetchone()
        return row['valor'] if row else default
    
    @staticmethod
    def get_todas_configuracoes() -> dict:
        db = get_db()
        rows = db.execute('SELECT * FROM configuracoes').fetchall()
        return {r['chave']: r['valor'] for r in rows}
    
    @staticmethod
    def get_tema() -> dict:
        configs = ConfiguracoesService.get_todas_configuracoes()
        return {
            'cor_primaria': configs.get('cor_primaria', '#6366f1'),
            'cor_secundaria': configs.get('cor_secundaria', '#ec4899'),
            'cor_fundo': configs.get('cor_fundo', '#f8fafc'),
            'cor_texto': configs.get('cor_texto', '#1e293b'),
            'tema': configs.get('tema', 'light'),
            'nome_loja': configs.get('nome_loja', 'Loja Digital'),
            'emoji_loja': configs.get('emoji_loja', '🛒')
        }
