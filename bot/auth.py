from database.connection import get_db
from utils.helpers import gerar_codigo, validar_cpf, validar_email, validar_telefone
import logging

logger = logging.getLogger(__name__)

class AuthService:
    
    @staticmethod
    def gerar_codigo(user_id: int) -> str:
        db = get_db()
        codigo = gerar_codigo()
        
        existe = db.execute('SELECT * FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if existe:
            db.execute('UPDATE clientes SET codigo_verificacao = ?, etapa_cadastro = ? WHERE telegram_id = ?',
                       (codigo, 'verificar', user_id))
        else:
            db.execute('INSERT INTO clientes (telegram_id, codigo_verificacao, etapa_cadastro) VALUES (?, ?, ?)',
                       (user_id, codigo, 'verificar'))
        db.commit()
        
        logger.info(f'🔐 Código gerado para {user_id}: {codigo}')
        return codigo
    
    @staticmethod
    def verificar_codigo(user_id: int, codigo: str) -> bool:
        db = get_db()
        cliente = db.execute('SELECT * FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        
        if not cliente or not cliente.get('codigo_verificacao'):
            return False
        
        if str(codigo).strip() != cliente['codigo_verificacao']:
            return False
        
        db.execute('UPDATE clientes SET verificado = 1, codigo_verificacao = NULL, etapa_cadastro = ? WHERE telegram_id = ?',
                   ('completo', user_id))
        db.commit()
        return True
    
    @staticmethod
    def login_cpf(user_id: int, cpf: str) -> dict:
        db = get_db()
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        
        if not validar_cpf(cpf_limpo):
            return {'sucesso': False, 'mensagem': 'CPF inválido.'}
        
        cliente = db.execute('SELECT * FROM clientes WHERE cpf = ?', (cpf_limpo,)).fetchone()
        if not cliente:
            return {'sucesso': False, 'mensagem': 'CPF não encontrado.'}
        if cliente.get('bloqueado'):
            return {'sucesso': False, 'mensagem': 'Conta bloqueada.'}
        
        db.execute('UPDATE clientes SET telegram_id = ? WHERE id = ?', (user_id, cliente['id']))
        db.commit()
        return {'sucesso': True, 'cliente': dict(cliente)}
    
    @staticmethod
    def get_cliente_por_telegram(user_id: int) -> dict:
        db = get_db()
        cliente = db.execute('SELECT * FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        return dict(cliente) if cliente else None
