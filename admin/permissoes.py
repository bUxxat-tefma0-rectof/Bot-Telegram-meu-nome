from database.connection import get_db

class PermissoesAdmin:
    
    CARGOS = ['admin', 'moderador', 'suporte', 'financeiro', 'estoquista']
    
    PERMISSOES_DISPONIVEIS = [
        'dashboard', 'produtos', 'categorias', 'estoque', 'pedidos',
        'clientes', 'financeiro', 'pix', 'gateway', 'cupons', 'promocoes',
        'afiliados', 'mensagens', 'botoes', 'menus', 'banners', 'temas',
        'aparencia', 'webhooks', 'relatorios', 'notificacoes', 'logs',
        'auditoria', 'backup', 'config'
    ]
    
    @staticmethod
    def listar_admins() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM administradores ORDER BY cargo, nome'
        ).fetchall()]
    
    @staticmethod
    def adicionar_admin(telegram_id: int, nome: str, cargo: str = 'admin', permissoes: str = 'all') -> dict:
        db = get_db()
        try:
            db.execute('''
                INSERT INTO administradores (telegram_id, nome, cargo, permissoes)
                VALUES (?, ?, ?, ?)
            ''', (telegram_id, nome, cargo, permissoes))
            db.commit()
            return {'sucesso': True, 'mensagem': 'Administrador adicionado!'}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def editar_admin(admin_id: int, dados: dict) -> dict:
        db = get_db()
        campos = []
        valores = []
        permitidos = ['nome', 'cargo', 'permissoes', 'ativo']
        
        for campo in permitidos:
            if campo in dados:
                campos.append(f'{campo} = ?')
                valores.append(dados[campo])
        
        if not campos:
            return {'sucesso': False}
        
        valores.append(admin_id)
        db.execute(f'UPDATE administradores SET {", ".join(campos)} WHERE id = ?', valores)
        db.commit()
        return {'sucesso': True, 'mensagem': 'Administrador atualizado!'}
    
    @staticmethod
    def remover_admin(admin_id: int):
        db = get_db()
        db.execute('DELETE FROM administradores WHERE id = ?', (admin_id,))
        db.commit()
    
    @staticmethod
    def toggle_admin(admin_id: int) -> dict:
        db = get_db()
        a = db.execute('SELECT ativo FROM administradores WHERE id = ?', (admin_id,)).fetchone()
        if not a: return {'sucesso': False}
        novo = 0 if a['ativo'] else 1
        db.execute('UPDATE administradores SET ativo = ? WHERE id = ?', (novo, admin_id))
        db.commit()
        return {'sucesso': True, 'ativo': novo}
    
    @staticmethod
    def verificar_permissao(admin_id: int, permissao: str) -> bool:
        db = get_db()
        admin = db.execute('SELECT permissoes FROM administradores WHERE id = ? AND ativo = 1',
                          (admin_id,)).fetchone()
        if not admin: return False
        if admin['permissoes'] == 'all': return True
        
        permissoes = admin['permissoes'].split(',')
        return permissao in permissoes
