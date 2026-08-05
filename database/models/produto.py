from database.connection import get_db
from typing import Optional, List, Dict
from utils.helpers import formatar_moeda

class ProdutoModel:
    
    @staticmethod
    def get_by_id(produto_id: int) -> Optional[Dict]:
        db = get_db()
        row = db.execute('''
            SELECT p.*, c.nome as categoria_nome, c.emoji as categoria_emoji
            FROM produtos p LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.id = ?
        ''', (produto_id,)).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def criar(dados: Dict) -> int:
        db = get_db()
        cursor = db.execute('''
            INSERT INTO produtos (categoria_id, nome, descricao, marca, preco, preco_promocional,
                preco_clube, estoque, unidade, peso, codigo_barras, sku, foto, destaque, ordem)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dados.get('categoria_id'), dados['nome'], dados.get('descricao', ''),
            dados.get('marca', ''), dados['preco'], dados.get('preco_promocional'),
            dados.get('preco_clube'), dados.get('estoque', 0), dados.get('unidade', 'un'),
            dados.get('peso', ''), dados.get('codigo_barras', ''), dados.get('sku', ''),
            dados.get('foto', ''), dados.get('destaque', 0), dados.get('ordem', 0)
        ))
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def atualizar(produto_id: int, dados: Dict) -> bool:
        db = get_db()
        campos = []
        valores = []
        permitidos = ['categoria_id', 'nome', 'descricao', 'marca', 'preco', 'preco_promocional',
                     'preco_clube', 'estoque', 'unidade', 'peso', 'codigo_barras', 'sku', 'foto',
                     'galeria', 'destaque', 'disponivel', 'oculto', 'ordem', 'info_nutricional',
                     'validade', 'limite_por_cliente', 'data_inicio_promocao', 'data_fim_promocao']
        
        for campo in permitidos:
            if campo in dados:
                campos.append(f'{campo} = ?')
                valores.append(dados[campo])
        
        if not campos:
            return False
        
        valores.append(produto_id)
        db.execute(f'UPDATE produtos SET {", ".join(campos)} WHERE id = ?', valores)
        db.commit()
        return True
    
    @staticmethod
    def excluir(produto_id: int) -> bool:
        db = get_db()
        db.execute('DELETE FROM favoritos WHERE produto_id = ?', (produto_id,))
        db.execute('DELETE FROM carrinhos WHERE produto_id = ?', (produto_id,))
        db.execute('DELETE FROM alertas_estoque WHERE produto_id = ?', (produto_id,))
        db.execute('DELETE FROM produtos WHERE id = ?', (produto_id,))
        db.commit()
        return True
    
    @staticmethod
    def duplicar(produto_id: int) -> Optional[int]:
        produto = ProdutoModel.get_by_id(produto_id)
        if not produto:
            return None
        
        dados = dict(produto)
        dados['nome'] = f'{dados["nome"]} (Cópia)'
        del dados['id']
        del dados['categoria_nome']
        del dados['categoria_emoji']
        
        return ProdutoModel.criar(dados)
    
    @staticmethod
    def toggle_status(produto_id: int) -> bool:
        db = get_db()
        p = db.execute('SELECT disponivel FROM produtos WHERE id = ?', (produto_id,)).fetchone()
        if not p:
            return False
        novo = 0 if p['disponivel'] else 1
        db.execute('UPDATE produtos SET disponivel = ? WHERE id = ?', (novo, produto_id))
        db.commit()
        return True
    
    @staticmethod
    def adicionar_estoque(produto_id: int, quantidade: int) -> bool:
        db = get_db()
        db.execute('UPDATE produtos SET estoque = estoque + ?, disponivel = 1 WHERE id = ?',
                   (quantidade, produto_id))
        db.commit()
        return True
    
    @staticmethod
    def reduzir_estoque(produto_id: int, quantidade: int) -> bool:
        db = get_db()
        produto = db.execute('SELECT estoque FROM produtos WHERE id = ?', (produto_id,)).fetchone()
        if not produto or produto['estoque'] < quantidade:
            return False
        db.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', (quantidade, produto_id))
        if produto['estoque'] - quantidade <= 0:
            db.execute('UPDATE produtos SET disponivel = 0 WHERE id = ?', (produto_id,))
        db.commit()
        return True
    
    @staticmethod
    def listar_por_categoria(categoria_id: int, limite: int = 20) -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM produtos WHERE categoria_id = ? AND disponivel = 1 AND estoque > 0 AND oculto = 0 ORDER BY destaque DESC, ordem LIMIT ?',
            (categoria_id, limite)
        ).fetchall()]
    
    @staticmethod
    def pesquisar(termo: str, limite: int = 30) -> List[Dict]:
        db = get_db()
        busca = f'%{termo}%'
        return [dict(r) for r in db.execute(
            '''SELECT * FROM produtos WHERE disponivel = 1 AND estoque > 0 AND oculto = 0
               AND (nome LIKE ? OR marca LIKE ? OR descricao LIKE ? OR codigo_barras LIKE ?)
               ORDER BY destaque DESC LIMIT ?''',
            (busca, busca, busca, busca, limite)
        ).fetchall()]
    
    @staticmethod
    def get_destaques(limite: int = 10) -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM produtos WHERE disponivel = 1 AND estoque > 0 AND (destaque = 1 OR preco_promocional IS NOT NULL) ORDER BY RANDOM() LIMIT ?',
            (limite,)
        ).fetchall()]
    
    @staticmethod
    def get_ofertas(limite: int = 15) -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM produtos WHERE disponivel = 1 AND estoque > 0 AND preco_promocional IS NOT NULL ORDER BY ((preco - preco_promocional) / preco * 100) DESC LIMIT ?',
            (limite,)
        ).fetchall()]
    
    @staticmethod
    def get_mais_vendidos(limite: int = 10) -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            '''SELECT p.*, COUNT(ip.id) as total_vendas FROM produtos p
               LEFT JOIN itens_pedido ip ON ip.produto_nome = p.nome
               WHERE p.disponivel = 1 GROUP BY p.id
               ORDER BY total_vendas DESC LIMIT ?''',
            (limite,)
        ).fetchall()]
    
    @staticmethod
    def get_estoque_baixo(limite: int = 20) -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM produtos WHERE estoque <= 10 AND disponivel = 1 ORDER BY estoque ASC LIMIT ?',
            (limite,)
        ).fetchall()]
