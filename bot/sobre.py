from database.connection import get_db
from config.geral import Config
from utils.helpers import formatar_moeda
from datetime import datetime

class SobreService:
    
    @staticmethod
    def get_info_loja() -> dict:
        db = get_db()
        
        info = {
            'nome': Config.NOME_LOJA,
            'versao': '2.0.0',
            'descricao': 'Loja Digital Telegram - Sistema completo de e-commerce',
            'desenvolvedor': 'Loja Digital',
            'site': Config.RENDER_EXTERNAL_URL or '',
            'ano': datetime.now().year
        }
        
        sobre = db.execute("SELECT valor FROM configuracoes WHERE chave = 'sobre_loja'").fetchone()
        if sobre:
            info['descricao'] = sobre['valor']
        
        logo = db.execute("SELECT valor FROM configuracoes WHERE chave = 'logo'").fetchone()
        if logo:
            info['logo'] = logo['valor']
        
        return info
    
    @staticmethod
    def get_status() -> dict:
        db = get_db()
        
        return {
            'online': True,
            'clientes': db.execute('SELECT COUNT(*) as t FROM clientes').fetchone()['t'],
            'produtos': db.execute('SELECT COUNT(*) as t FROM produtos WHERE disponivel = 1').fetchone()['t'],
            'categorias': db.execute('SELECT COUNT(*) as t FROM categorias WHERE ativo = 1').fetchone()['t'],
            'pedidos_hoje': db.execute("SELECT COUNT(*) as t FROM pedidos WHERE date(data_pedido) = date('now')").fetchone()['t'],
            'faturamento_mes': db.execute("SELECT COALESCE(SUM(total), 0) as t FROM pedidos WHERE pagamento_status = 'approved' AND strftime('%Y-%m', data_pedido) = strftime('%Y-%m', 'now')").fetchone()['t'],
            'hora_servidor': datetime.now().strftime('%H:%M:%S'),
            'data_servidor': datetime.now().strftime('%d/%m/%Y')
        }
    
    @staticmethod
    def get_termos() -> str:
        db = get_db()
        row = db.execute("SELECT valor FROM configuracoes WHERE chave = 'termos_uso'").fetchone()
        if row and row['valor']:
            return row['valor']
        
        return (
            '📋 *Termos de Uso*\n\n'
            '1. Ao usar este bot, você concorda com estes termos.\n'
            '2. Os preços podem ser alterados sem aviso prévio.\n'
            '3. O prazo de entrega varia conforme a região.\n'
            '4. Reembolsos são analisados em até 7 dias úteis.\n'
            '5. Seus dados são protegidos e não são compartilhados.\n\n'
            f'{Config.NOME_LOJA} - {datetime.now().year}'
        )
    
    @staticmethod
    def get_politica_privacidade() -> str:
        db = get_db()
        row = db.execute("SELECT valor FROM configuracoes WHERE chave = 'politica_privacidade'").fetchone()
        if row and row['valor']:
            return row['valor']
        
        return (
            '🔒 *Política de Privacidade*\n\n'
            '1. Coletamos apenas dados necessários para os pedidos.\n'
            '2. Não compartilhamos seus dados com terceiros.\n'
            '3. Você pode solicitar a exclusão dos seus dados.\n'
            '4. Utilizamos criptografia para proteger suas informações.\n'
            '5. Dados de pagamento são processados pelo Mercado Pago.\n\n'
            f'{Config.NOME_LOJA} - {datetime.now().year}'
        )
    
    @staticmethod
    def get_versao() -> str:
        return '2.0.0'
    
    @staticmethod
    def get_changelog() -> str:
        return (
            '📝 *Registro de Alterações*\n\n'
            '*v2.0.0*\n'
            '• Sistema de afiliados\n'
            '• Cashback em compras\n'
            '• Cupons de desconto\n'
            '• Painel admin web\n'
            '• Múltiplos temas\n'
            '• WebApp integrado\n\n'
            '*v1.0.0*\n'
            '• Lançamento inicial\n'
            '• Catálogo de produtos\n'
            '• Carrinho de compras\n'
            '• Pagamento PIX\n'
            '• Perfil do cliente'
        )
