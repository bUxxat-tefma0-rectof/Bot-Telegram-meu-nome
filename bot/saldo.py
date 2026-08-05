from database.connection import get_db
from utils.helpers import formatar_moeda
from services.pagamento import PagamentoService

class SaldoService:
    
    @staticmethod
    def get_saldo(user_id: int) -> dict:
        db = get_db()
        cliente = db.execute('SELECT saldo, cashback, pontos_fidelidade FROM clientes WHERE telegram_id = ?',
                            (user_id,)).fetchone()
        if not cliente: return {'saldo': 0, 'cashback': 0, 'pontos': 0}
        
        return {
            'saldo': cliente['saldo'],
            'saldo_formatado': formatar_moeda(cliente['saldo']),
            'cashback': cliente['cashback'],
            'cashback_formatado': formatar_moeda(cliente['cashback']),
            'pontos': cliente['pontos_fidelidade']
        }
    
    @staticmethod
    def recarregar(user_id: int, valor: float) -> dict:
        if valor < 10:
            return {'sucesso': False, 'mensagem': 'Valor mínimo: R$ 10,00'}
        
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return {'sucesso': False, 'mensagem': 'Cliente não encontrado'}
        
        pg = PagamentoService()
        return pg.processar_recarga(cliente['id'], valor)
    
    @staticmethod
    def get_extrato(user_id: int, limite: int = 20) -> list:
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return []
        
        return [dict(r) for r in db.execute(
            'SELECT * FROM recargas WHERE cliente_id = ? ORDER BY data DESC LIMIT ?',
            (cliente['id'], limite)
        ).fetchall()]
