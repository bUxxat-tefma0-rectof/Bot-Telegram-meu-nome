from database.connection import get_db
from datetime import datetime, timedelta

class CuponsAdmin:
    
    @staticmethod
    def listar() -> list:
        db = get_db()
        return [dict(r) for r in db.execute('SELECT * FROM cupons ORDER BY id DESC').fetchall()]
    
    @staticmethod
    def criar(dados: dict) -> dict:
        db = get_db()
        try:
            valido_ate = None
            if dados.get('dias_validade'):
                valido_ate = (datetime.now() + timedelta(days=int(dados['dias_validade']))).isoformat()
            
            db.execute('''
                INSERT INTO cupons (codigo, tipo, valor, valor_minimo, uso_maximo, valido_ate)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (dados['codigo'].upper(), dados.get('tipo','percentual'), float(dados['valor']),
                  float(dados.get('valor_minimo', 0)), int(dados.get('uso_maximo', 100)), valido_ate))
            db.commit()
            return {'sucesso': True, 'mensagem': f'Cupom {dados["codigo"].upper()} criado!'}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def toggle(cupom_id: int) -> dict:
        db = get_db()
        c = db.execute('SELECT ativo FROM cupons WHERE id = ?', (cupom_id,)).fetchone()
        if not c: return {'sucesso': False}
        novo = 0 if c['ativo'] else 1
        db.execute('UPDATE cupons SET ativo = ? WHERE id = ?', (novo, cupom_id))
        db.commit()
        return {'sucesso': True}
    
    @staticmethod
    def excluir(cupom_id: int):
        db = get_db()
        db.execute('DELETE FROM cupons WHERE id = ?', (cupom_id,))
        db.commit()
