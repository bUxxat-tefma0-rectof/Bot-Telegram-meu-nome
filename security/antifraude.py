from database.connection import get_db
from datetime import datetime, timedelta
from config.seguranca import SegurancaConfig
import logging

logger = logging.getLogger(__name__)

class AntiFraudeService:
    
    @staticmethod
    def verificar_compra(user_id: int, valor: float) -> dict:
        db = get_db()
        agora = datetime.now()
        
        # Verifica valor máximo
        if valor > SegurancaConfig.MAX_VALOR_COMPRA:
            return {'permitido': False, 'motivo': f'Valor máximo por compra: R$ {SegurancaConfig.MAX_VALOR_COMPRA:.2f}'}
        
        # Verifica compras na última hora
        compras_hora = db.execute(
            "SELECT COUNT(*) as t FROM pedidos WHERE cliente_id = ? AND data_pedido > ?",
            (user_id, (agora - timedelta(hours=1)).isoformat())
        ).fetchone()['t']
        
        if compras_hora >= SegurancaConfig.MAX_COMPRAS_HORA:
            return {'permitido': False, 'motivo': 'Muitas compras em 1 hora'}
        
        # Verifica compras no dia
        compras_dia = db.execute(
            "SELECT COUNT(*) as t FROM pedidos WHERE cliente_id = ? AND date(data_pedido) = date('now')",
            (user_id,)
        ).fetchone()['t']
        
        if compras_dia >= SegurancaConfig.MAX_COMPRAS_DIA:
            return {'permitido': False, 'motivo': 'Limite diário de compras atingido'}
        
        return {'permitido': True}
    
    @staticmethod
    def detectar_atividade_suspeita(user_id: int) -> list:
        alertas = []
        db = get_db()
        
        # Múltiplos cadastros do mesmo IP
        # Múltiplas tentativas de pagamento
        tentativas = db.execute(
            "SELECT COUNT(*) as t FROM logs_sistema WHERE usuario_id = ? AND acao = 'login_falha' AND data > datetime('now', '-1 hour')",
            (user_id,)
        ).fetchone()['t']
        
        if tentativas >= 5:
            alertas.append(f'Múltiplas tentativas de login ({tentativas})')
        
        # Vários pedidos cancelados
        cancelados = db.execute(
            "SELECT COUNT(*) as t FROM pedidos WHERE cliente_id = ? AND status = 'cancelado' AND data_pedido > datetime('now', '-7 days')",
            (user_id,)
        ).fetchone()['t']
        
        if cancelados >= 3:
            alertas.append(f'Muitos pedidos cancelados ({cancelados})')
        
        return alertas
    
    @staticmethod
    def bloquear_usuario(user_id: int, motivo: str):
        db = get_db()
        db.execute('UPDATE clientes SET bloqueado = 1 WHERE id = ?', (user_id,))
        db.execute('''
            INSERT INTO logs_sistema (usuario_id, acao, modulo, detalhes, data)
            VALUES (?, 'bloqueio_antifraude', 'seguranca', ?, datetime('now'))
        ''', (user_id, motivo))
        db.commit()
        logger.warning(f'🚫 Usuário {user_id} bloqueado: {motivo}')
