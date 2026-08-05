from database.connection import get_db
from utils.helpers import formatar_data

class AuditoriaAdmin:
    
    @staticmethod
    def get_alteracoes_produto(produto_id: int) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT * FROM logs_sistema WHERE modulo = 'produtos' AND detalhes LIKE ? ORDER BY data DESC",
            (f'%ID {produto_id}%',)
        ).fetchall()]
    
    @staticmethod
    def get_alteracoes_config() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT * FROM logs_sistema WHERE modulo = 'configuracoes' ORDER BY data DESC LIMIT 100"
        ).fetchall()]
    
    @staticmethod
    def get_alteracoes_precos() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT * FROM logs_sistema WHERE modulo = 'produtos' AND acao IN ('preco_alterado', 'promocao_alterada') ORDER BY data DESC LIMIT 100"
        ).fetchall()]
    
    @staticmethod
    def get_alteracoes_usuarios(usuario_id: int) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM logs_sistema WHERE usuario_id = ? ORDER BY data DESC LIMIT 100',
            (usuario_id,)
        ).fetchall()]
    
    @staticmethod
    def get_resumo_alteracoes(limite: int = 50) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            '''SELECT ls.*, c.nome as usuario_nome
               FROM logs_sistema ls
               LEFT JOIN clientes c ON ls.usuario_id = c.id
               ORDER BY ls.data DESC LIMIT ?''',
            (limite,)
        ).fetchall()]
