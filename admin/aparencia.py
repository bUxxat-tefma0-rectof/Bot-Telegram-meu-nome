from database.connection import get_db

class AparenciaAdmin:
    
    @staticmethod
    def get_config() -> dict:
        db = get_db()
        configs = db.execute("SELECT * FROM configuracoes WHERE categoria IN ('aparencia', 'geral')").fetchall()
        return {c['chave']: c['valor'] for c in configs}
    
    @staticmethod
    def salvar_config(dados: dict) -> dict:
        db = get_db()
        for chave, valor in dados.items():
            existe = db.execute('SELECT * FROM configuracoes WHERE chave = ?', (chave,)).fetchone()
            if existe:
                db.execute('UPDATE configuracoes SET valor = ? WHERE chave = ?', (str(valor), chave))
            else:
                db.execute("INSERT INTO configuracoes (chave, valor, categoria) VALUES (?, ?, 'aparencia')",
                          (chave, str(valor)))
        db.commit()
        return {'sucesso': True, 'mensagem': 'Aparência atualizada!'}
    
    @staticmethod
    def get_logo() -> str:
        db = get_db()
        row = db.execute("SELECT valor FROM configuracoes WHERE chave = 'logo'").fetchone()
        return row['valor'] if row else ''
    
    @staticmethod
    def get_banner() -> str:
        db = get_db()
        row = db.execute("SELECT valor FROM configuracoes WHERE chave = 'banner'").fetchone()
        return row['valor'] if row else ''
    
    @staticmethod
    def get_nome_loja() -> str:
        db = get_db()
        row = db.execute("SELECT valor FROM configuracoes WHERE chave = 'nome_loja'").fetchone()
        return row['valor'] if row else 'Loja Digital'
    
    @staticmethod
    def get_emoji_loja() -> str:
        db = get_db()
        row = db.execute("SELECT valor FROM configuracoes WHERE chave = 'emoji_loja'").fetchone()
        return row['valor'] if row else '🛒'
