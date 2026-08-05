from database.connection import get_db
from config.geral import Config
from utils.helpers import formatar_moeda
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NotificacaoService:
    
    @staticmethod
    def enviar(cliente_id: int, tipo: str, titulo: str, mensagem: str):
        try:
            db = get_db()
            db.execute('''
                INSERT INTO notificacoes (cliente_id, tipo, titulo, mensagem, data)
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (cliente_id, tipo, titulo, mensagem))
            db.commit()
            
            # Tenta enviar via Telegram
            try:
                cliente = db.execute('SELECT telegram_id FROM clientes WHERE id = ?', (cliente_id,)).fetchone()
                if cliente:
                    from bot.cliente import get_bot
                    bot = get_bot()
                    if bot:
                        import asyncio
                        async def send():
                            await bot.send_message(
                                chat_id=cliente['telegram_id'],
                                text=f'🔔 *{titulo}*\n\n{mensagem}',
                                parse_mode='Markdown'
                            )
                        asyncio.create_task(send())
            except:
                pass
                
        except Exception as e:
            logger.error(f'Erro ao enviar notificação: {e}')
    
    @staticmethod
    def notificar_pagamento_aprovado(cliente_id: int, pedido: dict):
        titulo = '✅ Pagamento Aprovado!'
        mensagem = f'Seu pagamento do pedido *{pedido["numero"]}* foi aprovado!\n\n💰 Valor: {formatar_moeda(pedido["total"])}\n\nSeu pedido está sendo preparado.'
        NotificacaoService.enviar(cliente_id, 'pagamento', titulo, mensagem)
    
    @staticmethod
    def notificar_pagamento_recusado(cliente_id: int, pedido_id: int):
        titulo = '❌ Pagamento Recusado'
        mensagem = f'O pagamento do seu pedido foi recusado.\nTente novamente ou use outro método.'
        NotificacaoService.enviar(cliente_id, 'pagamento', titulo, mensagem)
    
    @staticmethod
    def notificar_pedido_entregue(cliente_id: int, pedido: dict):
        titulo = '🏠 Pedido Entregue!'
        mensagem = f'Seu pedido *{pedido["numero"]}* foi entregue!\n\nObrigado por comprar conosco! ❤️\n\nAvalie sua experiência!'
        NotificacaoService.enviar(cliente_id, 'pedido', titulo, mensagem)
    
    @staticmethod
    def notificar_estoque_baixo(produto: dict):
        db = get_db()
        admin_id = Config.ADMIN_IDS[0] if Config.ADMIN_IDS else None
        if admin_id:
            titulo = '⚠️ Estoque Baixo'
            mensagem = f'Produto: *{produto["nome"]}*\nEstoque: {produto["estoque"]} unidades\n\nReponha o estoque!'
            NotificacaoService.enviar(admin_id, 'estoque', titulo, mensagem)
    
    @staticmethod
    def notificar_promocao(mensagem: str):
        db = get_db()
        clientes = db.execute('SELECT id FROM clientes WHERE bloqueado = 0').fetchall()
        for c in clientes:
            NotificacaoService.enviar(c['id'], 'promocao', '🎉 Promoção!', mensagem)
    
    @staticmethod
    def notificar_aniversariantes():
        db = get_db()
        hoje = datetime.now()
        clientes = db.execute(
            "SELECT id, nome FROM clientes WHERE data_nascimento LIKE ?",
            (f'%/{hoje.day:02d}/{hoje.month:02d}',)
        ).fetchall()
        
        for c in clientes:
            NotificacaoService.enviar(
                c['id'], 'aniversario', '🎂 Feliz Aniversário!',
                f'Parabéns, {c["nome"]}! Ganhe 10% de desconto hoje!\nCupom: ANIVER{c["id"]}'
            )
    
    @staticmethod
    def get_nao_lidas(cliente_id: int) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM notificacoes WHERE cliente_id = ? AND lida = 0 ORDER BY data DESC LIMIT 20',
            (cliente_id,)
        ).fetchall()]
    
    @staticmethod
    def marcar_como_lida(notificacao_id: int):
        db = get_db()
        db.execute('UPDATE notificacoes SET lida = 1 WHERE id = ?', (notificacao_id,))
        db.commit()
