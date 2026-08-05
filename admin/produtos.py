from database.connection import get_db
from utils.helpers import formatar_moeda
from services.upload import UploadService
from services.logs import LogService
import json

class ProdutosAdmin:
    
    @staticmethod
    def listar(pagina: int = 1, limite: int = 20, filtro: dict = None) -> dict:
        db = get_db()
        offset = (pagina - 1) * limite
        
        where = 'WHERE 1=1'
        params = []
        
        if filtro:
            if filtro.get('categoria_id'):
                where += ' AND p.categoria_id = ?'
                params.append(filtro['categoria_id'])
            if filtro.get('disponivel') is not None:
                where += ' AND p.disponivel = ?'
                params.append(filtro['disponivel'])
            if filtro.get('busca'):
                where += ' AND p.nome LIKE ?'
                params.append(f'%{filtro["busca"]}%')
        
        total = db.execute(f'SELECT COUNT(*) as t FROM produtos p {where}', params).fetchone()['t']
        
        produtos = [dict(r) for r in db.execute(
            f'''SELECT p.*, c.nome as categoria_nome, c.emoji as categoria_emoji
                FROM produtos p LEFT JOIN categorias c ON p.categoria_id = c.id
                {where} ORDER BY p.id DESC LIMIT ? OFFSET ?''',
            params + [limite, offset]
        ).fetchall()]
        
        return {'produtos': produtos, 'total': total, 'pagina': pagina, 'total_paginas': (total + limite - 1) // limite}
    
    @staticmethod
    def criar(dados: dict) -> dict:
        db = get_db()
        try:
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
            return {'sucesso': True, 'id': cursor.lastrowid, 'mensagem': 'Produto criado!'}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def editar(produto_id: int, dados: dict) -> dict:
        db = get_db()
        campos = []
        valores = []
        permitidos = ['categoria_id', 'nome', 'descricao', 'marca', 'preco', 'preco_promocional',
                     'preco_clube', 'estoque', 'unidade', 'peso', 'codigo_barras', 'sku', 'foto',
                     'destaque', 'disponivel', 'oculto', 'ordem', 'galeria', 'info_nutricional',
                     'validade', 'limite_por_cliente', 'data_inicio_promocao', 'data_fim_promocao']
        
        for campo in permitidos:
            if campo in dados:
                campos.append(f'{campo} = ?')
                valores.append(dados[campo])
        
        if not campos:
            return {'sucesso': False, 'mensagem': 'Nenhum dado para atualizar'}
        
        valores.append(produto_id)
        db.execute(f'UPDATE produtos SET {", ".join(campos)} WHERE id = ?', valores)
        db.commit()
        return {'sucesso': True, 'mensagem': 'Produto atualizado!'}
    
    @staticmethod
    def excluir(produto_id: int) -> dict:
        db = get_db()
        db.execute('DELETE FROM favoritos WHERE produto_id = ?', (produto_id,))
        db.execute('DELETE FROM carrinhos WHERE produto_id = ?', (produto_id,))
        db.execute('DELETE FROM produtos WHERE id = ?', (produto_id,))
        db.commit()
        return {'sucesso': True, 'mensagem': 'Produto excluído!'}
    
    @staticmethod
    def duplicar(produto_id: int) -> dict:
        db = get_db()
        produto = db.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,)).fetchone()
        if not produto:
            return {'sucesso': False, 'mensagem': 'Produto não encontrado'}
        
        dados = dict(produto)
        dados['nome'] = f'{dados["nome"]} (Cópia)'
        del dados['id']
        
        return ProdutosAdmin.criar(dados)
    
    @staticmethod
    def toggle_status(produto_id: int) -> dict:
        db = get_db()
        p = db.execute('SELECT disponivel FROM produtos WHERE id = ?', (produto_id,)).fetchone()
        if not p:
            return {'sucesso': False}
        novo = 0 if p['disponivel'] else 1
        db.execute('UPDATE produtos SET disponivel = ? WHERE id = ?', (novo, produto_id))
        db.commit()
        return {'sucesso': True, 'disponivel': novo}
