from flask import jsonify, request
from . import api_bp
from security.jwt import JWTHandler
from security.auth import SecurityAuth
from database.connection import get_db

@api_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json
    user_id = data.get('user_id')
    senha = data.get('senha')
    
    db = get_db()
    cliente = db.execute('SELECT * FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
    
    if not cliente:
        return jsonify({'sucesso': False, 'mensagem': 'Usuário não encontrado'})
    
    if cliente.get('senha') and not SecurityAuth.verificar_senha(senha, cliente['senha']):
        return jsonify({'sucesso': False, 'mensagem': 'Senha incorreta'})
    
    token = JWTHandler.gerar_token(cliente['id'], {'telegram_id': user_id})
    
    return jsonify({
        'sucesso': True,
        'token': token,
        'cliente': {
            'id': cliente['id'],
            'nome': cliente['nome'],
            'email': cliente.get('email')
        }
    })

@api_bp.route('/api/auth/verify', methods=['POST'])
def api_verify():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    payload = JWTHandler.verificar_token(token)
    
    if payload:
        return jsonify({'valido': True, 'user_id': payload['user_id']})
    return jsonify({'valido': False}), 401
