from flask import jsonify, request
from . import api_bp
from database.models.pedido import PedidoModel
from database.models.carrinho import CarrinhoModel
from services.pix import PixService
from services.notificacoes import NotificacaoService
from utils.helpers import gerar_numero_pedido, formatar_moeda
from config.geral import Config

@api_bp.route('/api/pedidos')
def listar_pedidos():
    user_id = request.args.get('userId')
    filtro = request.args.get('filtro', 'todos')
    pagina = request.args.get('pagina', 1, type=int)
    
    if user_id:
        from database.connection import get_db
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if cliente:
            pedidos = PedidoModel.listar_por_cliente(cliente['id'])
            return jsonify({'pedidos': pedidos})
    
    result = PedidoModel.listar_todos(filtro=filtro, pagina=pagina)
    return jsonify(result)

@api_bp.route('/api/pedidos/<int:pedido_id>')
def detalhes_pedido(pedido_id):
    pedido = PedidoModel.get_by_id(pedido_id)
    if not pedido:
        return jsonify({'erro': 'Pedido não encontrado'}), 404
    return jsonify(pedido)

@api_bp.route('/api/pedidos/finalizar', methods=['POST'])
def finalizar_pedido():
    try:
        data = request.json
        user_id = data.get('userId')
        metodo = data.get('metodoPagamento', 'pix')
        tipo_entrega = data.get('tipoEntrega', 'entrega')
        endereco_id = data.get('enderecoId')
        cupom = data.get('cupom')
        comentario = data.get('comentario')
        
        from database.connection import get_db
        db = get_db()
        cliente = db.execute('SELECT * FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente:
            return jsonify({'sucesso': False, 'mensagem': 'Cliente não encontrado'})
        
        carrinho = CarrinhoModel.get_total(cliente['id'])
        if not carrinho['itens']:
            return jsonify({'sucesso': False, 'mensagem': 'Carrinho vazio'})
        
        # Verifica estoque
        for item in carrinho['itens']:
            if item['quantidade'] > item.get('estoque', 0):
                return jsonify({'sucesso': False, 'mensagem': f'Estoque insuficiente: {item["nome"]}'})
        
        subtotal = carrinho['total']
        taxa = Config.TAXA_ENTREGA
        desconto = 0
        
        # Cupom
        if cupom:
            from database.models.cupom import CupomModel
            validacao = CupomModel.validar(cupom, subtotal)
            if validacao['valido']:
                desconto = CupomModel.calcular_desconto(validacao['cupom'], subtotal)
        
        total = subtotal + taxa - desconto
        
        if total < Config.PEDIDO_MINIMO:
            return jsonify({'sucesso': False, 'mensagem': f'Pedido mínimo: {formatar_moeda(Config.PEDIDO_MINIMO)}'})
        
        numero = gerar_numero_pedido()
        
        # Cria pedido
        pedido_id = PedidoModel.criar(cliente['id'], {
            'numero': numero,
            'endereco_id': endereco_id,
            'tipo_entrega': tipo_entrega,
            'subtotal': subtotal,
            'taxa_entrega': taxa,
            'desconto': desconto,
            'total': total,
            'cupom': cupom,
            'comentario': comentario,
            'pagamento_metodo': metodo
        })
        
        # Itens
        for item in carrinho['itens']:
            preco = item.get('preco_promocional') or item.get('preco', 0)
            PedidoModel.adicionar_item(pedido_id, item['produto_id'], item['nome'], 
                                       item['quantidade'], preco, item.get('comentario'))
            db.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?',
                       (item['quantidade'], item['produto_id']))
        
        # Cupom
        if cupom and desconto > 0:
            CupomModel.usar(validacao['cupom']['id'], cliente['id'], pedido_id)
        
        # Limpa carrinho
        CarrinhoModel.limpar(cliente['id'])
        db.commit()
        
        # PIX
        result = {'sucesso': True, 'numero': numero, 'total': total, 'pedido_id': pedido_id}
        
        if metodo == 'pix':
            pix_service = PixService()
            pix_result = pix_service.gerar_pix_pedido(pedido_id, cliente['id'])
            result['pagamento'] = {
                'qr_code_base64': pix_result.get('qr_code_base64', ''),
                'copia_cola': pix_result.get('copia_cola', ''),
                'payment_id': pix_result.get('payment_id', '')
            }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)})

@api_bp.route('/api/pedidos/<int:pedido_id>/cancelar', methods=['POST'])
def cancelar_pedido(pedido_id):
    user_id = request.json.get('userId')
    
    if user_id:
        from database.connection import get_db
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if cliente:
            pedido = db.execute('SELECT * FROM pedidos WHERE id = ? AND cliente_id = ?',
                               (pedido_id, cliente['id'])).fetchone()
            if not pedido:
                return jsonify({'sucesso': False, 'mensagem': 'Pedido não encontrado'})
    
    if PedidoModel.cancelar(pedido_id):
        NotificacaoService.notificar_pedido_cancelado(pedido_id)
        return jsonify({'sucesso': True, 'mensagem': 'Pedido cancelado'})
    return jsonify({'sucesso': False, 'mensagem': 'Não foi possível cancelar'})

@api_bp.route('/api/pedidos/<int:pedido_id>/pagar', methods=['POST'])
def pagar_pedido(pedido_id):
    from database.connection import get_db
    db = get_db()
    pedido = db.execute('SELECT * FROM pedidos WHERE id = ?', (pedido_id,)).fetchone()
    
    if not pedido:
        return jsonify({'sucesso': False, 'mensagem': 'Pedido não encontrado'})
    
    pix_service = PixService()
    result = pix_service.gerar_pix_pedido(pedido_id, pedido['cliente_id'])
    
    return jsonify({
        'sucesso': result.get('sucesso', False),
        'qr_code_base64': result.get('qr_code_base64', ''),
        'copia_cola': result.get('copia_cola', ''),
        'payment_id': result.get('payment_id', '')
    })
