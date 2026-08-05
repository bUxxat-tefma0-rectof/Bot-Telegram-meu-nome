from database.connection import get_db

class CategoriasAdmin:
    
    @staticmethod
    def listar() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM categorias ORDER BY ordem'
        ).fetchall()]
    
    @staticmethod
    def criar(dados: dict) -> dict:
        db = get_db()
        try:
            db.execute('''
                INSERT INTO categorias (nome, emoji, descricao, banner, cor, icone, ordem, destaque)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dados['nome'], dados.get('emoji', '📦'), dados.get('descricao', ''),
                  dados.get('banner', ''), dados.get('cor', '#6366f1'), dados.get('icone', ''),
                  dados.get('ordem', 0), dados.get('destaque', 0)))
            db.commit()
            return {'sucesso': True, 'mensagem': 'Categoria criada!'}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def editar(cat_id: int, dados: dict) -> dict:
        db = get_db()
        campos = []
        valores = []
        permitidos = ['nome', 'emoji', 'descricao', 'banner', 'cor', 'icone', 'ordem', 'ativo', 'destaque']
        
        for campo in permitidos:
            if campo in dados:
                campos.append(f'{campo} = ?')
                valores.append(dados[campo])
        
        if not campos:
            return {'sucesso': False}
        
        valores.append(cat_id)
        db.execute(f'UPDATE categorias SET {", ".join(campos)} WHERE id = ?', valores)
        db.commit()
        return {'sucesso': True, 'mensagem': 'Categoria atualizada!'}
    
    @staticmethod
    def excluir(cat_id: int) -> dict:
        db = get_db()
        db.execute('UPDATE produtos SET categoria_id = NULL WHERE categoria_id = ?', (cat_id,))
        db.execute('DELETE FROM categorias WHERE id = ?', (cat_id,))
        db.commit()
        return {'sucesso': True, 'mensagem': 'Categoria excluída!'}
    
    @staticmethod
    def reordenar(ordem_ids: list) -> dict:
        db = get_db()
        for i, cat_id in enumerate(ordem_ids):
            db.execute('UPDATE categorias SET ordem = ? WHERE id = ?', (i + 1, cat_id))
        db.commit()
        return {'sucesso': True, 'mensagem': 'Ordem atualizada!'}
