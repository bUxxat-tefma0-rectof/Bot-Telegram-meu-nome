from database.connection import get_db
from config.geral import Config

class SobreService:
    
    @staticmethod
    def get_info() -> dict:
        db = get_db()
        info = {
            'nome': Config.NOME_LOJA,
            'versao': '1.0.0',
            'descricao': 'Loja Digital Telegram - Sistema completo de e-commerce',
            'desenvolvedor': 'Sua Empresa'
        }
        
        sobre = db.execute("SELECT valor FROM configuracoes WHERE chave='sobre_loja'").fetchone()
        if sobre:
            info['descricao'] = sobre['valor']
        
        return info
    
    @staticmethod
    def get_status() -> dict:
        db = get_db()
        return {
            'clientes': db.execute('SELECT COUNT(*) as t FROM clientes').fetchone()['t'],
            'produtos': db.execute('SELECT COUNT(*) as t FROM produtos WHERE disponivel = 1').fetchone()['t'],
            'pedidos_hoje': db.execute("SELECT COUNT(*) as t FROM pedidos WHERE date(data_pedido) = date('now')").fetchone()['t'],
            'online': True
        }
