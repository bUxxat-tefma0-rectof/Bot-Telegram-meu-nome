from database.connection import get_db
from typing import List

class PermissionHandler:
    
    PERMISSOES = [
        'dashboard', 'produtos', 'categorias', 'estoque', 'pedidos',
        'clientes', 'financeiro', 'pix', 'gateway', 'cupons', 'promocoes',
        'afiliados', 'mensagens', 'botoes', 'menus', 'banners', 'temas',
        'aparencia', 'webhooks', 'relatorios', 'notificacoes', 'logs',
        'auditoria', 'backup', 'config'
    ]
    
    CARGOS = {
        'admin': 'all',
        'moderador': 'dashboard,pedidos,clientes,notificacoes',
        'suporte': 'clientes,notificacoes',
        'financeiro': 'dashboard,financeiro,pix,relatorios',
        'estoquista': 'dashboard,produtos,estoque'
    }
    
    @classmethod
    def tem_permissao(cls, user_id: int, permissao: str) -> bool:
        db = get_db()
        admin = db.execute('SELECT * FROM administradores WHERE telegram_id = ? AND ativo = 1',
                          (user_id,)).fetchone()
        if not admin:
            return False
        
        if admin['permissoes'] == 'all':
            return True
        
        permissoes = admin['permissoes'].split(',') if admin['permissoes'] else []
        return permissao in permissoes
    
    @classmethod
    def get_permissoes_usuario(cls, user_id: int) -> List[str]:
        db = get_db()
        admin = db.execute('SELECT * FROM administradores WHERE telegram_id = ? AND ativo = 1',
                          (user_id,)).fetchone()
        if not admin:
            return []
        
        if admin['permissoes'] == 'all':
            return cls.PERMISSOES
        
        return admin['permissoes'].split(',') if admin['permissoes'] else []
    
    @classmethod
    def get_permissoes_cargo(cls, cargo: str) -> List[str]:
        permissoes_str = cls.CARGOS.get(cargo, '')
        if permissoes_str == 'all':
            return cls.PERMISSOES
        return permissoes_str.split(',') if permissoes_str else []
