from database.connection import get_db
from utils.helpers import formatar_moeda

class CashbackService:
    
    @staticmethod
    def get_saldo(user_id: int) -> dict:
        db = get_db()
        cliente = db.execute('SELECT cashback, pontos_fidelidade FROM clientes WHERE telegram_id = ?',
                            (user_id,)).fetchone()
        if not cliente: return {'cashback': 0, 'pontos': 0}
        
        return {
            'cashback': cliente['cashback'],
            'cashback_formatado': formatar_moeda(cliente['cashback']),
            'pontos': cliente['pontos_fidelidade']
        }
    
    @staticmethod
    def resgatar(user_id: int) -> dict:
        db = get_db()
        cliente = db.execute('SELECT id, cashback FROM clientes WHERE telegram_id = ?',
                            (user_id,)).fetchone()
        if not cliente: return {'sucesso': False, 'mensagem': 'Cliente não encontrado'}
        
        if cliente['cashback'] < 5:
            return {'sucesso': False, 'mensagem': 'Mínimo de R$ 5,00 em cashback para resgatar'}
        
        valor = cliente['cashback']
        
        # Cria cupom com o valor do cashback
        from datetime import datetime, timedelta
        codigo = f'CASH{cliente["id"]}{datetime.now().strftime("%d%m")}'
        
        db.execute('''
            INSERT INTO cupons (codigo, tipo, valor, uso_maximo, uso_atual, valido_ate, ativo)
            VALUES (?, 'fixo', ?, 1, 0, ?, 1)
        ''', (codigo, valor, (datetime.now() + timedelta(days=30)).isoformat()))
        
        db.execute('UPDATE clientes SET cashback = 0 WHERE id = ?', (cliente['id'],))
        db.commit()
        
        return {
            'sucesso': True,
            'valor': formatar_moeda(valor),
            'cupom': codigo,
            'mensagem': f'Cashback de {formatar_moeda(valor)} resgatado! Use o cupom: {codigo}'
        }
    
    @staticmethod
    def adicionar(user_id: int, valor_pedido: float) -> float:
        cashback = valor_pedido * 0.02
        db = get_db()
        db.execute('UPDATE clientes SET cashback = cashback + ? WHERE telegram_id = ?',
                   (cashback, user_id))
        db.commit()
        return cashback
