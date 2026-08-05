from database.connection import get_db
from utils.helpers import formatar_moeda, formatar_data, formatar_cpf, formatar_telefone

class PerfilService:
    
    @staticmethod
    def get_perfil(user_id: int) -> dict:
        db = get_db()
        cliente = db.execute('SELECT * FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return None
        
        total_pedidos = db.execute('SELECT COUNT(*) as t FROM pedidos WHERE cliente_id = ?',
                                   (cliente['id'],)).fetchone()['t']
        
        result = dict(cliente)
        result['total_pedidos'] = total_pedidos
        result['total_gasto_formatado'] = formatar_moeda(result.get('total_gasto', 0))
        result['saldo_formatado'] = formatar_moeda(result.get('saldo', 0))
        result['cashback_formatado'] = formatar_moeda(result.get('cashback', 0))
        result['cpf_formatado'] = formatar_cpf(result.get('cpf', '')) if result.get('cpf') else None
        result['telefone_formatado'] = formatar_telefone(result.get('telefone', '')) if result.get('telefone') else None
        
        return result
    
    @staticmethod
    def atualizar(user_id: int, dados: dict) -> dict:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return {'sucesso': False, 'mensagem': 'Cliente não encontrado'}
        
        campos = []
        valores = []
        permitidos = ['nome', 'sobrenome', 'email', 'telefone', 'data_nascimento', 'sexo']
        
        for campo in permitidos:
            if campo in dados and dados[campo] is not None:
                campos.append(f'{campo} = ?')
                valores.append(dados[campo])
        
        if not campos:
            return {'sucesso': False, 'mensagem': 'Nenhum dado para atualizar'}
        
        valores.append(user_id)
        db.execute(f'UPDATE clientes SET {", ".join(campos)} WHERE telegram_id = ?', valores)
        db.commit()
        
        return {'sucesso': True, 'mensagem': 'Perfil atualizado com sucesso!'}
    
    @staticmethod
    def get_enderecos(user_id: int) -> list:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return []
        
        return [dict(r) for r in db.execute(
            'SELECT * FROM enderecos WHERE cliente_id = ? ORDER BY principal DESC',
            (cliente['id'],)
        ).fetchall()]
