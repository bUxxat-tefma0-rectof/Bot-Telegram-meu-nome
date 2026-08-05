from database.connection import get_db
from services.pagamento import PagamentoService

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
            db.execute('UPDATE configuracoes SET valor = ? WHERE chave = ?', (str(valor), chave))
        else:
            db.execute("INSERT INTO configuracoes (chave, valor, categoria) VALUES (?, ?, 'pagamentos')",
                       (chave, str(valor)))
        db.commit()
        return {'sucesso': True}
    
    @staticmethod
    def get_gateway_ativo() -> str:
        db = get_db()
        row = db.execute("SELECT valor FROM configuracoes WHERE chave = 'gateway_ativo'").fetchone()
        return row['valor'] if row else 'mercadopago'
    
    @staticmethod
    def set_gateway_ativo(gateway: str) -> dict:
        return GatewayAdmin.salvar_config('gateway_ativo', gateway)
    
    @staticmethod
    def get_gateways_disponiveis() -> list:
        return [
            {'id': 'mercadopago', 'nome': 'Mercado Pago', 'descricao': 'Gateway oficial com PIX e Cartão', 'ativo': True},
            {'id': 'pix_manual', 'nome': 'PIX Manual', 'descricao': 'Chave PIX copia e cola', 'ativo': False},
            {'id': 'picpay', 'nome': 'PicPay', 'descricao': 'Gateway PicPay', 'ativo': False},
            {'id': 'paypal', 'nome': 'PayPal', 'descricao': 'Gateway internacional', 'ativo': False}
        ]
    
    @staticmethod
    def testar_conexao() -> dict:
        try:
            pg = PagamentoService()
            result = pg.verificar_pagamento('test_123')
            if result.get('status') != 'error':
                return {'sucesso': True, 'mensagem': 'Conexão com Mercado Pago OK!'}
            return {'sucesso': False, 'mensagem': 'Erro na conexão com Mercado Pago'}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
