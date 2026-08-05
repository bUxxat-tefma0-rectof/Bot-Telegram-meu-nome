from database.connection import get_db

class TermosService:
    
    @staticmethod
    def get_termos() -> str:
        db = get_db()
        row = db.execute("SELECT valor FROM configuracoes WHERE chave='termos_uso'").fetchone()
        return row['valor'] if row else 'Termos de uso não configurados.'
    
    @staticmethod
    def get_politica() -> str:
        db = get_db()
        row = db.execute("SELECT valor FROM configuracoes WHERE chave='politica_privacidade'").fetchone()
        return row['valor'] if row else 'Política de privacidade não configurada.'
    
    @staticmethod
    def get_sobre() -> str:
        db = get_db()
        row = db.execute("SELECT valor FROM configuracoes WHERE chave='sobre_loja'").fetchone()
        return row['valor'] if row else 'Loja Digital - Sua melhor experiência de compras no Telegram!'
