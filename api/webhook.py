from flask import jsonify, request
from . import api_bp
from services.webhook import WebhookService
from services.logs import LogService
import hashlib
import hmac
import json

@api_bp.route('/api/webhooks/mercadopago', methods=['POST'])
def webhook_mercadopago():
    try:
        data = request.json
        
        if not data:
            return jsonify({'status': 'ok'})
        
        LogService.registrar(None, 'webhook_recebido', 'webhooks', 
                            f'Mercado Pago: {json.dumps(data)[:200]}')
        
        webhook_service = WebhookService()
        result = webhook_service.processar_webhook_mercadopago(data)
        
        return jsonify({'status': 'ok', 'result': result})
        
    except Exception as e:
        LogService.registrar(None, 'webhook_erro', 'webhooks', str(e))
        return jsonify({'status': 'error', 'mensagem': str(e)}), 500

@api_bp.route('/api/webhooks/teste', methods=['POST'])
def webhook_teste():
    data = request.json
    url = data.get('url', '')
    
    import requests
    try:
        resp = requests.post(url, json={'teste': True, 'timestamp': __import__('datetime').datetime.now().isoformat()}, timeout=5)
        return jsonify({
            'sucesso': True,
            'status_code': resp.status_code,
            'resposta': resp.text[:200]
        })
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)})

@api_bp.route('/api/webhooks', methods=['GET'])
def listar_webhooks():
    from database.connection import get_db
    db = get_db()
    webhooks = [dict(r) for r in db.execute(
        "SELECT * FROM configuracoes WHERE chave LIKE 'webhook_%'"
    ).fetchall()]
    
    result = []
    for w in webhooks:
        try:
            dados = json.loads(w['valor'])
            dados['id'] = w['id']
            dados['chave'] = w['chave']
            result.append(dados)
        except:
            pass
    
    return jsonify(result)

@api_bp.route('/api/webhooks', methods=['POST'])
def criar_webhook():
    data = request.json
    url = data.get('url')
    eventos = data.get('eventos', [])
    
    if not url:
        return jsonify({'sucesso': False, 'mensagem': 'URL não informada'})
    
    from database.connection import get_db
    db = get_db()
    webhooks = db.execute("SELECT * FROM configuracoes WHERE chave LIKE 'webhook_%'").fetchall()
    chave = f"webhook_{len(webhooks) + 1}"
    
    dados = json.dumps({'url': url, 'eventos': eventos, 'ativo': True})
    db.execute("INSERT INTO configuracoes (chave, valor, categoria) VALUES (?, ?, 'webhooks')",
               (chave, dados))
    db.commit()
    
    return jsonify({'sucesso': True, 'mensagem': 'Webhook criado!'})

@api_bp.route('/api/webhooks/<int:webhook_id>', methods=['DELETE'])
def excluir_webhook(webhook_id):
    from database.connection import get_db
    db = get_db()
    db.execute('DELETE FROM configuracoes WHERE id = ?', (webhook_id,))
    db.commit()
    return jsonify({'sucesso': True, 'mensagem': 'Webhook excluído!'})
