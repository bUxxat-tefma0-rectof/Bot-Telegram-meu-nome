from database.connection import get_db
from utils.helpers import gerar_numero_pedido, formatar_moeda
from services.pix import PixService
from config.geral import Config
import logging

logger = logging.getLogger(__name__)

class CheckoutService:
    
    @staticmethod
    def finalizar(user_id: int, metodo: str, cupom: str = None, comentario: str = None, endereco_id: int = None) -> dict:
        db = get_db()
        cliente = db.execute('SELECT * FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente:
            return {'sucesso': False, 'mensagem': 'Cliente não encontrado'}
        
        from bot.carrinho import CarrinhoService
        carrinho = CarrinhoService.listar(user_id)
        
        if not carrinho['itens']:
            return {'sucesso': False, 'mensagem': 'Carrinho vazio'}
        
        # Verifica estoque
        for item in carrinho['itens']:
            if item['estoque'] < item['quantidade']:
                return {'sucesso': False, 'mensagem': f'Estoque insuficiente para: {item["nome"]}'}
        
        subtotal = carrinho['total']
        taxa_entrega = float(Config.TAXA_ENTREGA or 5)
        desconto = 0
        
        # Cupom
        if cupom:
            from bot.cupons import CuponsService
            cupom_data = db.execute('SELECT * FROM cupons WHERE codigo = ? AND ativo = 1', (cupom.upper(),)).fetchone()
            if cupom_data and cupom_data['uso_atual'] < cupom_data['uso_maximo']:
                if cupom_data['tipo'] == 'percentual':
                    desconto = subtotal * (cupom_data['valor'] / 100)
                else:
                    desconto = min(cupom_data['valor'], subtotal)
                db.execute('UPDATE cupons SET uso_atual = uso_atual + 1 WHERE id = ?', (cupom_data['id'],))
        
        total = subtotal + taxa_entrega - desconto
        
        if total < float(Config.PEDIDO_MINIMO or 10):
            return {'sucesso': False, 'mensagem': f'Pedido mínimo: {formatar_moeda(float(Config.PEDIDO_MINIMO or 10))}'}
        
        numero = gerar_numero_pedido()
        
        # Cria pedido
        cursor = db.execute('''
            INSERT INTO pedidos (numero, cliente_id, endereco_id, status, subtotal, taxa_entrega, desconto, total, cupom, comentario, pagamento_metodo)
            VALUES (?, ?, ?, 'recebido', ?, ?, ?, ?, ?, ?, ?)
        ''', (numero, cliente['id'], endereco_id, subtotal, taxa_entrega, desconto, total, cupom, comentario, metodo))
        pedido_id = cursor.lastrowid
        
        # Itens
        for item in carrinho['itens']:
            preco = item.get('preco_promocional') or item.get('preco', 0)
            db.execute('''
                INSERT INTO itens_pedido (pedido_id, produto_id, produto_nome, quantidade, preco_unitario, comentario)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (pedido_id, item['produto_id'], item['nome'], item['quantidade'], preco, item.get('comentario')))
            db.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', (item['quantidade'], item['produto_id']))
        
        # Limpa carrinho
        CarrinhoService.limpar(user_id)
        db.commit()
        
        # Gera PIX se for o método escolhido
        if metodo == 'pix':
            pix_service = PixService()
            result = pix_service.gerar_pix_pedido(pedido_id, cliente['id'])
            
            return {
                'sucesso': True,
                'numero': numero,
                'total': total,
                'pedido_id': pedido_id,
                'qr_buffer': result.get('qr_buffer'),
                'copia_cola': result.get('copia_cola'),
                'payment_id': result.get('payment_id')
            }
        
        return {
            'sucesso': True,
            'numero': numero,
            'total': total,
            'pedido_id': pedido_id
        }
