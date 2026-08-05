from flask import jsonify, request
from . import api_bp
from database.models.cliente import ClienteModel
from database.connection import get_db

@api_bp.route('/api/clientes')
def listar_clientes():
    pagina = request.args.get('pagina', 1, type=int)
    busca = request.args.get('busca', '')
    
    if busca:
        result = ClienteModel.buscar(busca)
        return jsonify({'clientes': result, 'total': len(result)})
    
    result = ClienteModel.listar_todos(pagina=pagina)
    return jsonify(result)

@api_bp.route('/api/clientes/<int:cliente_id>')
def detalhes_cliente(cliente_id):
    cliente = ClienteModel.get_by_id(cliente_id)
    if not cliente:
        return jsonify({'erro': 'Cliente não encontrado'}), 404
    
    total_pedidos = ClienteModel.get_total_pedidos(cliente_id)
    total_gasto = ClienteModel.get_total_gasto(cliente_id)
    
    cliente['total_pedidos'] = total_pedidos
    cliente['total_gasto'] = total_gasto
    
    return jsonify(ClienteModel.formatar_dados(cliente))

@api_bp.route('/api/clientes/<int:cliente_id>/toggle', methods=['POST'])
def toggle_cliente(cliente_id):
    cliente = ClienteModel.get_by_id(cliente_id)
    if not cliente:
        return jsonify({'sucesso': False, 'mensagem': 'Cliente não encontrado'})
    
    if cliente['bloqueado']:
        ClienteModel.desbloquear(cliente_id)
        return jsonify({'sucesso': True, 'bloqueado': False})
    else:
        ClienteModel.bloquear(cliente_id)
        return jsonify({'sucesso': True, 'bloqueado': True})

@api_bp.route('/api/clientes/<int:cliente_id>/saldo', methods=['POST'])
def editar_saldo(cliente_id):
    valor = request.json.get('valor', 0)
    
    if valor > 0:
        ClienteModel.adicionar_saldo(cliente_id, valor)
    elif valor < 0:
        ClienteModel.adicionar_saldo(cliente_id, valor)
    
    cliente = ClienteModel.get_by_id(cliente_id)
    return jsonify({
        'sucesso': True,
        'saldo': cliente['saldo'],
        'saldo_formatado': f'R$ {cliente["saldo"]:,.2f}'
    })

@api_bp.route('/api/perfil')
def get_perfil():
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({})
    
    cliente = ClienteModel.get_by_telegram(user_id)
    if not cliente:
        return jsonify({})
    
    total_pedidos = ClienteModel.get_total_pedidos(cliente['id'])
    cliente['total_pedidos'] = total_pedidos
    
    return jsonify(ClienteModel.formatar_dados(cliente))

@api_bp.route('/api/perfil/atualizar', methods=['POST'])
def atualizar_perfil():
    user_id = request.json.get('userId')
    dados = request.json.get('dados', {})
    
    if not user_id:
        return jsonify({'sucesso': False, 'mensagem': 'Usuário não encontrado'})
    
    cliente = ClienteModel.get_by_telegram(user_id)
    if not cliente:
        return jsonify({'sucesso': False, 'mensagem': 'Cliente não encontrado'})
    
    if ClienteModel.atualizar(cliente['id'], dados):
        return jsonify({'sucesso': True, 'mensagem': 'Perfil atualizado!'})
    return jsonify({'sucesso': False, 'mensagem': 'Nenhum dado para atualizar'})

@api_bp.route('/api/ranking')
def get_ranking():
    limite = request.args.get('limite', 20, type=int)
    ranking = ClienteModel.get_ranking(limite)
    return jsonify(ranking)
