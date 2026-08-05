from database.connection import get_db
from datetime import datetime

class PromocoesAdmin:
    
    @staticmethod
    def listar() -> list:
        db = get_db()
        return [dict(r) for r in db.execute('SELECT * FROM promocoes ORDER BY id DESC').fetchall()]
    
    @staticmethod
    def criar(dados: dict) -> dict:
        db = get_db()
        try:
            db.execute('''
                INSERT INTO promocoes (nome, tipo, valor, categoria_id, produto_id, data_inicio, data_fim)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (dados['nome'], dados.get('tipo','percentual'), float(dados.get('valor',0)),
                  dados.get('categoria_id'), dados.get('produto_id'),
                  dados.get('data_inicio'), dados.get('data_fim')))
            db.commit()
            return {'sucesso': True, 'mensagem': 'Promoção criada!'}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def toggle(promo_id: int) -> dict:
        db = get_db()
        p = db.execute('SELECT ativo FROM promocoes WHERE id = ?', (promo_id,)).fetchone()
        if not p: return {'sucesso': False}
        novo = 0 if p['ativo'] else 1
        db.execute('UPDATE promocoes SET ativo = ? WHERE id = ?', (novo, promo_id))
        db.commit()
        return {'sucesso': True}
    
    @staticmethod
    def excluir(promo_id: int):
        db = get_db()
        db.execute('DELETE FROM promocoes WHERE id = ?', (promo_id,))
        db.commit()
