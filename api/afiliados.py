from flask import jsonify, request
from . import api_bp
from database.models.afiliado import AfiliadoModel
from database.connection import get_db

@api_bp.route('/api/afiliados')
def listar_afiliados():
    afiliados = AfiliadoModel.listar_todos()
    return jsonify(afiliados)

@api_bp.route('/api/afiliados/<int:afiliado_id>')
def detalhes_afiliado(afiliado_id):
    afiliado = AfiliadoModel.get_by_id(afiliado_id)
    if not afiliado:
        return jsonify({'erro': 'Afiliado não encontrado'}), 404
    
    indicados = AfiliadoModel.get_indicados(afiliado_id)
    comissoes = AfiliadoModel.get_comissoes(afiliado_id)
    
    afiliado['indicados'] = indicados
    afiliado['comissoes'] = comissoes
    
    return jsonify(afiliado)

@api_bp.route('/api/afiliados/me')
def meu_afiliado():
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({'erro': 'userId não informado'})
    
    db = get_db()
    cliente = db.execute('SELECT id, nome FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
    if not cliente:
        return jsonify({'erro': 'Cliente não encontrado'})
    
    afiliado = AfiliadoModel.get_by_cliente(cliente['id'])
    
    if not afiliado:
        result = AfiliadoModel.criar(cliente['id'], cliente['nome'] or '')
        if result.get('sucesso'):
            afiliado = result.get('afiliado')
        else:
            return jsonify({'erro': 'Erro ao criar afiliado'})
    
    indicados = AfiliadoModel.get_indicados(afiliado['id'])
    afiliado['indicados'] = indicados
    
    return jsonify(afiliado)

@api_bp.route('/api/afiliados/saque', methods=['POST'])
def solicitar_saque():
    user_id = request.json.get('userId')
    valor = request.json.get('valor')
    
    if not user_id or not valor:
        return jsonify({'sucesso': False, 'mensagem': 'Dados incompletos'})
    
    db = get_db()
    cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
    if not cliente:
        return jsonify({'sucesso': False, 'mensagem': 'Cliente não encontrado'})
    
    afiliado = AfiliadoModel.get_by_cliente(cliente['id'])
    if not afiliado:
        return jsonify({'sucesso': False, 'mensagem': 'Afiliado não encontrado'})
    
    return jsonify(AfiliadoModel.solicitar_saque(afiliado['id'], float(valor)))

@api_bp.route('/api/afiliados/<int:afiliado_id>/comissao', methods=['POST'])
def editar_comissao(afiliado_id):
    percentual = request.json.get('percentual')
    if not percentual:
        return jsonify({'sucesso': False, 'mensagem': 'Percentual não informado'})
    
    if AfiliadoModel.editar_comissao(afiliado_id, float(percentual)):
        return jsonify({'sucesso': True, 'mensagem': 'Comissão atualizada!'})
    return jsonify({'sucesso': False, 'mensagem': 'Erro ao atualizar'})

@api_bp.route('/api/afiliados/<int:afiliado_id>/toggle', methods=['POST'])
def toggle_afiliado(afiliado_id):
    if AfiliadoModel.toggle(afiliado_id):
        return jsonify({'sucesso': True})
    return jsonify({'sucesso': False})

@api_bp.route('/api/afiliados/ranking')
def ranking_afiliados():
    limite = request.args.get('limite', 20, type=int)
    ranking = AfiliadoModel.get_ranking(limite)
    return jsonify(ranking)
