from database.connection import get_db
from services.upload import UploadService
from datetime import datetime

class BannersAdmin:
    
    @staticmethod
    def listar() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM banners ORDER BY ordem'
        ).fetchall()]
    
    @staticmethod
    def criar(dados: dict) -> dict:
        db = get_db()
        try:
            db.execute('''
                INSERT INTO banners (titulo, imagem, url, ordem, data_inicio, data_fim)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (dados.get('titulo', ''), dados['imagem'], dados.get('url', ''),
                  dados.get('ordem', 0), dados.get('data_inicio'), dados.get('data_fim')))
            db.commit()
            return {'sucesso': True, 'mensagem': 'Banner criado!'}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def editar(banner_id: int, dados: dict) -> dict:
        db = get_db()
        campos = []
        valores = []
        permitidos = ['titulo', 'imagem', 'url', 'ordem', 'ativo', 'data_inicio', 'data_fim']
        
        for campo in permitidos:
            if campo in dados:
                campos.append(f'{campo} = ?')
                valores.append(dados[campo])
        
        if not campos:
            return {'sucesso': False}
        
        valores.append(banner_id)
        db.execute(f'UPDATE banners SET {", ".join(campos)} WHERE id = ?', valores)
        db.commit()
        return {'sucesso': True, 'mensagem': 'Banner atualizado!'}
    
    @staticmethod
    def excluir(banner_id: int):
        db = get_db()
        db.execute('DELETE FROM banners WHERE id = ?', (banner_id,))
        db.commit()
    
    @staticmethod
    def toggle(banner_id: int) -> dict:
        db = get_db()
        b = db.execute('SELECT ativo FROM banners WHERE id = ?', (banner_id,)).fetchone()
        if not b: return {'sucesso': False}
        novo = 0 if b['ativo'] else 1
        db.execute('UPDATE banners SET ativo = ? WHERE id = ?', (novo, banner_id))
        db.commit()
        return {'sucesso': True, 'ativo': novo}
    
    @staticmethod
    def get_ativos() -> list:
        db = get_db()
        agora = datetime.now().isoformat()
        return [dict(r) for r in db.execute(
            """SELECT * FROM banners WHERE ativo = 1 
               AND (data_inicio IS NULL OR data_inicio <= ?) 
               AND (data_fim IS NULL OR data_fim >= ?)
               ORDER BY ordem""",
            (agora, agora)
        ).fetchall()]
