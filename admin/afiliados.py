from database.connection import get_db
from utils.helpers import formatar_moeda

class AfiliadosAdmin:
    
    @staticmethod
    def listar() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            '''SELECT a.*, c.nome, c.telefone, c.email
               FROM afiliados a JOIN clientes c ON a.cliente_id = c.id
               ORDER BY a.total_comissoes DESC'''
        ).fetchall()]
    
    @staticmethod
    def get_detalhes(afiliado_id: int) -> dict:
        db = get_db()
        afiliado = db.execute('''
            SELECT a.*, c.nome, c.telefone, c.email, c.total_gasto
            FROM afiliados a JOIN clientes c ON a.cliente_id = c.id
            WHERE a.id = ?
        ''', (afiliado_id,)).fetchone()
        
        if not afiliado: return None
        
        indicados = [dict(r) for r in db.execute(
            'SELECT nome, total_gasto, data_cadastro FROM clientes WHERE afiliado_id = ?',
            (afiliado_id,)
        ).fetchall()]
        
        comissoes = [dict(r) for r in db.execute(
            'SELECT * FROM comissoes WHERE afiliado_id = ? ORDER BY data DESC',
            (afiliado_id,)
        ).fetchall()]
        
        result = dict(afiliado)
        result['indicados'] = indicados
        result['comissoes'] = comissoes
        return result
    
    @staticmethod
    def editar_comissao(afiliado_id: int, percentual: float) -> dict:
        db = get_db()
        db.execute('UPDATE afiliados SET comissao_percentual = ? WHERE id = ?', (percentual, afiliado_id))
        db.commit()
        return {'sucesso': True, 'mensagem': f'Comissão alterada para {percentual}%'}
    
    @staticmethod
    def toggle(afiliado_id: int) -> dict:
        db = get_db()
        a = db.execute('SELECT ativo FROM afiliados WHERE id = ?', (afiliado_id,)).fetchone()
        if not a: return {'sucesso': False}
        novo = 0 if a['ativo'] else 1
        db.execute('UPDATE afiliados SET ativo = ? WHERE id = ?', (novo, afiliado_id))
        db.commit()
        return {'sucesso': True, 'ativo': novo}
    
    @staticmethod
    def aprovar_saque(afiliado_id: int, valor: float) -> dict:
        db = get_db()
        afiliado = db.execute('SELECT saldo_comissao FROM afiliados WHERE id = ?', (afiliado_id,)).fetchone()
        if not afiliado or afiliado['saldo_comissao'] < valor:
            return {'sucesso': False, 'mensagem': 'Saldo insuficiente'}
        
        db.execute('UPDATE afiliados SET saldo_comissao = saldo_comissao - ? WHERE id = ?',
                   (valor, afiliado_id))
        db.commit()
        return {'sucesso': True, 'mensagem': f'Saque de {formatar_moeda(valor)} aprovado!'}
    
    @staticmethod
    def get_solicitacoes_saque() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT * FROM comissoes WHERE status = 'pendente' ORDER BY data"
        ).fetchall()]
