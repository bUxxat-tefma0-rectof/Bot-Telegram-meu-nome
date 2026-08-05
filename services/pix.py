from services.pagamento import PagamentoService
from database.connection import get_db
from config.notificacoes import NotificacaoConfig
from config.geral import Config
from services.notificacoes import NotificacaoService
from services.logs import LogService
import threading
import time
import logging

logger = logging.getLogger(__name__)

class PixService:
    def __init__(self):
        self.pagamento = PagamentoService()
        self.verificacoes_ativas = {}
    
    def gerar_pix_pedido(self, pedido_id: int, cliente_id: int) -> dict:
        db = get_db()
        pedido = db.execute('SELECT * FROM pedidos WHERE id = ?', (pedido_id,)).fetchone()
        
        if not pedido:
            return {'sucesso': False, 'mensagem': 'Pedido não encontrado'}
        
        descricao = f"Pedido {pedido['numero']} - {Config.NOME_LOJA}"
        result = self.pagamento.gerar_pix(pedido['total'], descricao, pedido['numero'])
        
        if result['sucesso']:
            db.execute('''
                UPDATE pedidos SET pagamento_id = ?, pagamento_qrcode = ?, pagamento_status = 'pendente'
                WHERE id = ?
            ''', (result['payment_id'], result['copia_cola'], pedido_id))
            db.commit()
            
            LogService.registrar(
                cliente_id, 'pix_gerado', 'pedido',
                f'PIX gerado para pedido {pedido["numero"]}',
                None, result['payment_id']
            )
            
            self.iniciar_verificacao(pedido_id, result['payment_id'], cliente_id)
        
        return result
    
    def iniciar_verificacao(self, pedido_id: int, payment_id: str, cliente_id: int):
        def verificar():
            tentativas = 0
            max_tentativas = NotificacaoConfig.MAX_VERIFICACOES_PIX
            
            while tentativas < max_tentativas:
                time.sleep(NotificacaoConfig.INTERVALO_VERIFICACAO_PIX)
                tentativas += 1
                
                result = self.pagamento.verificar_pagamento(payment_id)
                
                if result['aprovado']:
                    self.confirmar_pagamento(pedido_id, payment_id, cliente_id)
                    break
                elif result['recusado']:
                    self.recusar_pagamento(pedido_id, payment_id, cliente_id)
                    break
        
        thread = threading.Thread(target=verificar, daemon=True)
        thread.start()
        self.verificacoes_ativas[pedido_id] = thread
    
    def confirmar_pagamento(self, pedido_id: int, payment_id: str, cliente_id: int):
        db = get_db()
        db.execute('''
            UPDATE pedidos SET status = 'confirmado', pagamento_status = 'approved', data_pagamento = datetime('now')
            WHERE id = ?
        ''', (pedido_id,))
        
        pedido = db.execute('SELECT * FROM pedidos WHERE id = ?', (pedido_id,)).fetchone()
        
        db.execute('''
            UPDATE clientes SET total_gasto = total_gasto + ?
            WHERE id = ?
        ''', (pedido['total'], cliente_id))
        
        # Cashback
        cashback = pedido['total'] * 0.02
        db.execute('UPDATE clientes SET cashback = cashback + ? WHERE id = ?', (cashback, cliente_id))
        
        # Pontos fidelidade
        pontos = int(pedido['total'])
        db.execute('UPDATE clientes SET pontos_fidelidade = pontos_fidelidade + ? WHERE id = ?', (pontos, cliente_id))
        
        # Comissão afiliado
        cliente = db.execute('SELECT afiliado_id FROM clientes WHERE id = ?', (cliente_id,)).fetchone()
        if cliente and cliente['afiliado_id']:
            afiliado = db.execute('SELECT * FROM afiliados WHERE id = ?', (cliente['afiliado_id'],)).fetchone()
            if afiliado:
                comissao = pedido['total'] * (afiliado['comissao_percentual'] / 100)
                db.execute('''
                    UPDATE afiliados SET total_comissoes = total_comissoes + ?, saldo_comissao = saldo_comissao + ?
                    WHERE id = ?
                ''', (comissao, comissao, afiliado['id']))
                db.execute('''
                    INSERT INTO comissoes (afiliado_id, pedido_id, valor, status)
                    VALUES (?, ?, ?, 'aprovado')
                ''', (afiliado['id'], pedido_id, comissao))
        
        db.commit()
        
        NotificacaoService.notificar_pagamento_aprovado(cliente_id, pedido)
        LogService.registrar(cliente_id, 'pagamento_aprovado', 'pedido', f'Pagamento aprovado: {payment_id}', None, payment_id)
        
        logger.info(f'✅ Pagamento confirmado: Pedido {pedido["numero"]}')
    
    def recusar_pagamento(self, pedido_id: int, payment_id: str, cliente_id: int):
        db = get_db()
        db.execute("UPDATE pedidos SET pagamento_status = 'rejected' WHERE id = ?", (pedido_id,))
        db.commit()
        
        NotificacaoService.notificar_pagamento_recusado(cliente_id, pedido_id)
        LogService.registrar(cliente_id, 'pagamento_recusado', 'pedido', f'Pagamento recusado: {payment_id}')
    
    def verificar_manualmente(self, pedido_id: int) -> dict:
        db = get_db()
        pedido = db.execute('SELECT * FROM pedidos WHERE id = ?', (pedido_id,)).fetchone()
        
        if not pedido or not pedido['pagamento_id']:
            return {'sucesso': False, 'mensagem': 'Pedido sem PIX vinculado'}
        
        result = self.pagamento.verificar_pagamento(pedido['pagamento_id'])
        
        if result['aprovado']:
            self.confirmar_pagamento(pedido_id, pedido['pagamento_id'], pedido['cliente_id'])
            return {'sucesso': True, 'aprovado': True, 'mensagem': 'Pagamento confirmado!'}
        
        return {'sucesso': True, 'aprovado': False, 'status': result['status']}
