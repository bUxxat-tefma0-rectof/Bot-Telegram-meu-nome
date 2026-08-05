from database.connection import get_db

class GatewayAdmin:
    
    @staticmethod
    def get_config() -> dict:
        db = get_db()
        configs = db.execute("SELECT * FROM configuracoes WHERE categoria = 'pagamentos'").fetchall()
        return {c['chave']: c['valor'] for c in configs}
    
    @staticmethod
    def salvar_config(chave: str, valor: str) -> dict:
        db = get_db()
        existe = db.execute('SELECT * FROM configuracoes WHERE chave = ?', (chave,)).fetchone()
        if existe:
            db.execute('UPDATE configuracoes SET valor = ? WHERE chave = ?', (valor, chave))
        else:
            db.execute("INSERT INTO configuracoes (chave, valor, categoria) VALUES (?, ?, 'pagamentos')", (chave, valor))
        db.commit()
        return {'sucesso': True}
    
    @staticmethod
    def get_gateways_disponiveis() -> list:
        return [
            {'id': 'mercadopago', 'nome': 'Mercado Pago', 'ativo': True},
            {'id': 'pix_manual', 'nome': 'PIX Manual', 'ativo': False},
            {'id': 'picpay', 'nome': 'PicPay', 'ativo': False},
            {'id': 'paypal', 'nome': 'PayPal', 'ativo': False}
        ]
