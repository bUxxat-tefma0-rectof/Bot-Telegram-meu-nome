from database.connection import get_db
from typing import List, Dict, Optional
from datetime import datetime

class CarrinhoModel:
    
    @staticmethod
    def get_itens(cliente_id: int) -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            '''SELECT c.*, p.nome, p.preco, p.preco_promocional, p.foto, p.marca, p.estoque, p.limite_por_cliente
               FROM carrinhos c JOIN produtos p ON c.produto_id = p.id
               WHERE c.cliente_id = ? AND p.disponivel = 1 ORDER BY c.data_adicao DESC''',
            (cliente_id,)
        ).fetchall()]
    
    @staticmethod
    def get_total(cliente_id: int) -> Dict:
        itens = CarrinhoModel.get_itens(cliente_id)
        total = sum((i.get('preco_promocional') or i.get('preco', 0)) * i['quantidade'] for i in itens)
        quantidade = sum(i['quantidade'] for i in itens)
        return {'itens': itens, 'total': total, 'quantidade': quantidade}
    
    @staticmethod
    def adicionar(cliente_id: int, produto_id: int, quantidade: int = 1, comentario: str = None) -> Dict:
        db = get_db()
        
        produto = db.execute('SELECT estoque, limite_por_cliente, nome FROM produtos WHERE id = ? AND disponivel = 1',
                            (produto_id,)).fetchone()
        if not produto:
            return {'sucesso': False, 'mensagem': 'Produto indisponível'}
        if produto['estoque'] < quantidade:
            return {'sucesso': False, 'mensagem': f'Estoque insuficiente. Disponível: {produto["estoque"]}'}
        
        existe = db.execute('SELECT * FROM carrinhos WHERE cliente_id = ? AND produto_id = ?',
                           (cliente_id, produto_id)).fetchone()
        
        if existe:
            nova_qtd = existe['quantidade'] + quantidade
            if produto['limite_por_cliente'] and nova_qtd > produto['limite_por_cliente']:
                return {'sucesso': False, 'mensagem': f'Limite de {produto["limite_por_cliente"]} unidades por cliente'}
            db.execute('UPDATE carrinhos SET quantidade = ?, comentario = COALESCE(?, comentario) WHERE id = ?',
                       (nova_qtd, comentario, existe['id']))
        else:
            db.execute('''
                INSERT INTO carrinhos (cliente_id, produto_id, quantidade, comentario, data_adicao)
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (cliente_id, produto_id, quantidade, comentario))
        
        db.commit()
        return {'sucesso': True, 'mensagem': f'{produto["nome"]} adicionado ao carrinho!'}
    
    @staticmethod
    def remover(cliente_id: int, carrinho_id: int) -> bool:
        db = get_db()
        db.execute('DELETE FROM carrinhos WHERE id = ? AND cliente_id = ?', (carrinho_id, cliente_id))
        db.commit()
        return True
    
    @staticmethod
    def atualizar_quantidade(cliente_id: int, carrinho_id: int, quantidade: int) -> bool:
        db = get_db()
        if quantidade <= 0:
            return CarrinhoModel.remover(cliente_id, carrinho_id)
        db.execute('UPDATE carrinhos SET quantidade = ? WHERE id = ? AND cliente_id = ?',
                   (quantidade, carrinho_id, cliente_id))
        db.commit()
        return True
    
    @staticmethod
    def atualizar_comentario(cliente_id: int, carrinho_id: int, comentario: str) -> bool:
        db = get_db()
        db.execute('UPDATE carrinhos SET comentario = ? WHERE id = ? AND cliente_id = ?',
                   (comentario, carrinho_id, cliente_id))
        db.commit()
        return True
    
    @staticmethod
    def limpar(cliente_id: int) -> bool:
        db = get_db()
        db.execute('DELETE FROM carrinhos WHERE cliente_id = ?', (cliente_id,))
        db.commit()
        return True
    
    @staticmethod
    def get_quantidade_itens(cliente_id: int) -> int:
        db = get_db()
        result = db.execute('SELECT COALESCE(SUM(quantidade), 0) as t FROM carrinhos WHERE cliente_id = ?',
                           (cliente_id,)).fetchone()
        return result['t'] if result else 0
    
    @staticmethod
    def verificar_estoque(cliente_id: int) -> List[Dict]:
        itens = CarrinhoModel.get_itens(cliente_id)
        problemas = []
        for item in itens:
            if item['quantidade'] > item['estoque']:
                problemas.append({
                    'carrinho_id': item['id'],
                    'nome': item['nome'],
                    'quantidade': item['quantidade'],
                    'estoque': item['estoque']
                })
        return problemas
    
    @staticmethod
    def limpar_abandonados(horas: int = 24) -> int:
        db = get_db()
        result = db.execute(f"DELETE FROM carrinhos WHERE data_adicao < datetime('now', '-{horas} hours')")
        db.commit()
        return result.rowcount
