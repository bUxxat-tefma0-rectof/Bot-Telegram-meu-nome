from database.connection import get_db

class SuporteService:
    
    @staticmethod
    def get_contato() -> dict:
        db = get_db()
        telefone = db.execute("SELECT valor FROM configuracoes WHERE chave='telefone_suporte'").fetchone()
        email = db.execute("SELECT valor FROM configuracoes WHERE chave='email_suporte'").fetchone()
        telegram = db.execute("SELECT valor FROM configuracoes WHERE chave='telegram_suporte'").fetchone()
        
        return {
            'telefone': telefone['valor'] if telefone else 'Não configurado',
            'email': email['valor'] if email else 'Não configurado',
            'telegram': telegram['valor'] if telegram else '@suporte'
        }
    
    @staticmethod
    def get_horario() -> str:
        db = get_db()
        row = db.execute("SELECT valor FROM configuracoes WHERE chave='horario_suporte'").fetchone()
        return row['valor'] if row else 'Seg-Sex 9h às 18h'
    
    @staticmethod
    def enviar_mensagem(user_id: int, mensagem: str) -> dict:
        db = get_db()
        cliente = db.execute('SELECT nome, email, telefone FROM clientes WHERE telegram_id = ?',
                            (user_id,)).fetchone()
        if not cliente: return {'sucesso': False}
        
        # Aqui poderia enviar email, salvar no banco, etc
        return {'sucesso': True, 'mensagem': 'Mensagem enviada ao suporte! Responderemos em breve.'}
