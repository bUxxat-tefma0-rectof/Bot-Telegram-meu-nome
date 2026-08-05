from database.connection import get_db
from utils.helpers import formatar_moeda, formatar_data, formatar_cpf, formatar_telefone

class ClientesAdmin:
    
    @staticmethod
    def listar(pagina: int = 1, limite: int = 20, busca: str = '') -> dict:
        db = get_db()
        where = ''
        params = []
        
        if busca:
            where = 'WHERE (nome LIKE ? OR telefone LIKE ? OR cpf LIKE ? OR email LIKE ?)'
            termo = f'%{busca}%'
            params = [termo, termo, termo, termo]
        
        total = db.execute(f'SELECT COUNT(*) as t FROM clientes {where}', params).fetchone()['t']
        offset = (pagina - 1) * limite
        
        clientes = [dict(r) for r in db.execute(
            f'''SELECT *, (SELECT COUNT(*) FROM pedidos WHERE cliente_id = c.id) as total_pedidos
                FROM clientes c {where} ORDER BY total_gasto DESC LIMIT ? OFFSET ?''',
            params + [limite, offset]
        ).fetchall()]
        
        return {'clientes': clientes, 'total': total, 'pagina': pagina}
    
    @staticmethod
    def get_detalhes(cliente_id: int) -> dict:
        db = get_db()
        cliente = db.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,)).fetchone()
        if not cliente: return None
        
        pedidos = [dict(r) for r in db.execute(
            'SELECT * FROM pedidos WHERE cliente_id = ? ORDER BY data_pedido DESC LIMIT 20',
            (cliente_id,)
        ).fetchall()]
        
        enderecos = [dict(r) for r in db.execute(
            'SELECT * FROM enderecos WHERE cliente_id = ?', (cliente_id,)
        ).fetchall()]
        
        result = dict(cliente)
        result['pedidos'] = pedidos
        result['enderecos'] = enderecos
        result['cpf_formatado'] = formatar_cpf(result.get('cpf',''))
        result['telefone_formatado'] = formatar_telefone(result.get('telefone',''))
        result['total_gasto_formatado'] = formatar_moeda(result.get('total_gasto', 0))
        
        return result
    
    @staticmethod
    def toggle_bloqueio(cliente_id: int) -> dict:
        db = get_db()
        c = db.execute('SELECT bloqueado FROM clientes WHERE id = ?', (cliente_id,)).fetchone()
        if not c: return {'sucesso': False}
        
        novo = 0 if c['bloqueado'] else 1
        db.execute('UPDATE clientes SET bloqueado = ? WHERE id = ?', (novo, cliente_id))
        db.commit()
        return {'sucesso': True, 'bloqueado': novo}
    
    @staticmethod
    def editar_saldo(cliente_id: int, valor: float) -> dict:
        db = get_db()
        db.execute('UPDATE clientes SET saldo = saldo + ? WHERE id = ?', (valor, cliente_id))
        db.commit()
        return {'sucesso': True, 'mensagem': f'Saldo alterado em {formatar_moeda(valor)}'}
