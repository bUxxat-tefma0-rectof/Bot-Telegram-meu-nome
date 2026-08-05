from database.connection import get_db
from utils.helpers import gerar_codigo_afiliado, formatar_moeda

class AfiliadosService:
    
    @staticmethod
    def criar_afiliado(user_id: int) -> dict:
        db = get_db()
        cliente = db.execute('SELECT * FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return {'sucesso': False, 'mensagem': 'Cliente não encontrado'}
        
        existe = db.execute('SELECT * FROM afiliados WHERE cliente_id = ?', (cliente['id'],)).fetchone()
        if existe:
            return {'sucesso': True, 'afiliado': dict(existe)}
        
        codigo = gerar_codigo_afiliado(cliente.get('nome', 'CLI'))
        
        cursor = db.execute('''
            INSERT INTO afiliados (cliente_id, codigo, comissao_percentual)
            VALUES (?, ?, ?)
        ''', (cliente['id'], codigo, 5))
        db.commit()
        
        return {'sucesso': True, 'afiliado': {'codigo': codigo, 'comissao_percentual': 5}}
    
    @staticmethod
    def get_afiliado(user_id: int) -> dict:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return None
        
        afiliado = db.execute('SELECT * FROM afiliados WHERE cliente_id = ?', (cliente['id'],)).fetchone()
        return dict(afiliado) if afiliado else None
    
    @staticmethod
    def processar_indicacao(codigo_afiliado: str, novo_cliente_id: int):
        db = get_db()
        afiliado = db.execute('SELECT * FROM afiliados WHERE codigo = ? AND ativo = 1',
                              (codigo_afiliado,)).fetchone()
        if not afiliado: return
        
        db.execute('UPDATE clientes SET afiliado_id = ? WHERE id = ?',
                   (afiliado['id'], novo_cliente_id))
        db.execute('UPDATE afiliados SET total_indicacoes = total_indicacoes + 1 WHERE id = ?',
                   (afiliado['id'],))
        db.commit()
    
    @staticmethod
    def solicitar_saque(user_id: int) -> dict:
        db = get_db()
        afiliado = AfiliadosService.get_afiliado(user_id)
        if not afiliado: return {'sucesso': False, 'mensagem': 'Afiliado não encontrado'}
        
        if afiliado['saldo_comissao'] < 50:
            return {'sucesso': False, 'mensagem': 'Saldo mínimo para saque: R$ 50,00'}
        
        # Aqui implementaria a lógica de saque
        return {'sucesso': True, 'mensagem': 'Saque solicitado com sucesso! O pagamento será processado em até 7 dias.'}
