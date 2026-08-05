from database.connection import get_db

class PesquisaService:
    
    @staticmethod
    def pesquisar(termo: str, limite: int = 20) -> list:
        db = get_db()
        busca = f'%{termo}%'
        return [dict(r) for r in db.execute(
            '''SELECT * FROM produtos 
               WHERE disponivel = 1 AND estoque > 0 AND oculto = 0
               AND (nome LIKE ? OR marca LIKE ? OR descricao LIKE ? OR codigo_barras LIKE ?)
               ORDER BY destaque DESC LIMIT ?''',
            (busca, busca, busca, busca, limite)
        ).fetchall()]
    
    @staticmethod
    def pesquisar_com_filtros(termo: str, categoria_id: int = None, preco_min: float = None, 
                             preco_max: float = None, ordenar: str = 'relevancia') -> list:
        db = get_db()
        busca = f'%{termo}%'
        
        query = '''SELECT * FROM produtos WHERE disponivel = 1 AND estoque > 0 AND oculto = 0
                   AND (nome LIKE ? OR marca LIKE ? OR descricao LIKE ?)'''
        params = [busca, busca, busca]
        
        if categoria_id:
            query += ' AND categoria_id = ?'
            params.append(categoria_id)
        if preco_min is not None:
            query += ' AND COALESCE(preco_promocional, preco) >= ?'
            params.append(preco_min)
        if preco_max is not None:
            query += ' AND COALESCE(preco_promocional, preco) <= ?'
            params.append(preco_max)
        
        if ordenar == 'menor_preco':
            query += ' ORDER BY COALESCE(preco_promocional, preco) ASC'
        elif ordenar == 'maior_preco':
            query += ' ORDER BY COALESCE(preco_promocional, preco) DESC'
        elif ordenar == 'nome':
            query += ' ORDER BY nome ASC'
        else:
            query += ' ORDER BY destaque DESC'
        
        query += ' LIMIT 30'
        
        return [dict(r) for r in db.execute(query, params).fetchall()]
