from database.connection import get_db
from typing import List, Optional

class LojaService:
    
    @staticmethod
    def get_categorias() -> List[dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM categorias WHERE ativo = 1 ORDER BY ordem'
        ).fetchall()]
    
    @staticmethod
    def get_categoria(cat_id: int) -> Optional[dict]:
        db = get_db()
        r = db.execute('SELECT * FROM categorias WHERE id = ?', (cat_id,)).fetchone()
        return dict(r) if r else None
    
    @staticmethod
    def get_produtos_por_categoria(cat_id: int, limite: int = 20) -> List[dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM produtos WHERE categoria_id = ? AND disponivel = 1 AND estoque > 0 AND oculto = 0 ORDER BY destaque DESC, ordem LIMIT ?',
            (cat_id, limite)
        ).fetchall()]
    
    @staticmethod
    def get_produto(prod_id: int) -> Optional[dict]:
        db = get_db()
        r = db.execute('SELECT * FROM produtos WHERE id = ?', (prod_id,)).fetchone()
        return dict(r) if r else None
    
    @staticmethod
    def get_destaques(limite: int = 10) -> List[dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM produtos WHERE disponivel = 1 AND estoque > 0 AND (destaque = 1 OR preco_promocional IS NOT NULL) ORDER BY RANDOM() LIMIT ?',
            (limite,)
        ).fetchall()]
    
    @staticmethod
    def get_ofertas(limite: int = 15) -> List[dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM produtos WHERE disponivel = 1 AND estoque > 0 AND preco_promocional IS NOT NULL ORDER BY ((preco - preco_promocional) / preco * 100) DESC LIMIT ?',
            (limite,)
        ).fetchall()]
    
    @staticmethod
    def get_mais_vendidos(limite: int = 10) -> List[dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            '''SELECT p.*, COUNT(ip.id) as total_vendas FROM produtos p
               LEFT JOIN itens_pedido ip ON ip.produto_nome = p.nome
               WHERE p.disponivel = 1 GROUP BY p.id
               ORDER BY total_vendas DESC LIMIT ?''',
            (limite,)
        ).fetchall()]
