from database.connection import get_db
from typing import List, Optional, Dict

class CategoriaModel:
    
    @staticmethod
    def get_by_id(cat_id: int) -> Optional[Dict]:
        db = get_db()
        row = db.execute('SELECT * FROM categorias WHERE id = ?', (cat_id,)).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def listar_ativas() -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM categorias WHERE ativo = 1 ORDER BY ordem'
        ).fetchall()]
    
    @staticmethod
    def listar_todas() -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM categorias ORDER BY ordem'
        ).fetchall()]
    
    @staticmethod
    def criar(dados: Dict) -> int:
        db = get_db()
        cursor = db.execute('''
            INSERT INTO categorias (nome, emoji, descricao, banner, cor, icone, ordem, destaque)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (dados['nome'], dados.get('emoji', '📦'), dados.get('descricao', ''),
              dados.get('banner', ''), dados.get('cor', '#6366f1'), dados.get('icone', ''),
              dados.get('ordem', 0), dados.get('destaque', 0)))
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def atualizar(cat_id: int, dados: Dict) -> bool:
        db = get_db()
        campos = []
        valores = []
        permitidos = ['nome', 'emoji', 'descricao', 'banner', 'cor', 'icone', 'ordem', 'ativo', 'destaque']
        
        for campo in permitidos:
            if campo in dados:
                campos.append(f'{campo} = ?')
                valores.append(dados[campo])
        
        if not campos:
            return False
        
        valores.append(cat_id)
        db.execute(f'UPDATE categorias SET {", ".join(campos)} WHERE id = ?', valores)
        db.commit()
        return True
    
    @staticmethod
    def excluir(cat_id: int) -> bool:
        db = get_db()
        db.execute('UPDATE produtos SET categoria_id = NULL WHERE categoria_id = ?', (cat_id,))
        db.execute('DELETE FROM categorias WHERE id = ?', (cat_id,))
        db.commit()
        return True
    
    @staticmethod
    def toggle_status(cat_id: int) -> bool:
        db = get_db()
        c = db.execute('SELECT ativo FROM categorias WHERE id = ?', (cat_id,)).fetchone()
        if not c:
            return False
        novo = 0 if c['ativo'] else 1
        db.execute('UPDATE categorias SET ativo = ? WHERE id = ?', (novo, cat_id))
        db.commit()
        return True
    
    @staticmethod
    def reordenar(ordem_ids: List[int]) -> bool:
        db = get_db()
        for i, cat_id in enumerate(ordem_ids):
            db.execute('UPDATE categorias SET ordem = ? WHERE id = ?', (i + 1, cat_id))
        db.commit()
        return True
    
    @staticmethod
    def get_com_produtos() -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            '''SELECT c.*, COUNT(p.id) as total_produtos
               FROM categorias c LEFT JOIN produtos p ON c.id = p.categoria_id AND p.disponivel = 1
               WHERE c.ativo = 1 GROUP BY c.id ORDER BY c.ordem'''
        ).fetchall()]
