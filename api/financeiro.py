from flask import jsonify, request
from . import api_bp
from database.connection import get_db
from services.pagamento import PagamentoService
from services.pix import PixService
from utils.helpers import formatar_moeda

@api_bp.route('/api/financeiro/resumo')
def resumo_financeiro():
    db = get_db()
    
    return jsonify({
        'faturamento_total': db.execute("SELECT COALESCE(SUM(total), 0) as t FROM pedidos WHERE pagamento_status = 'approved'").fetchone()['t'],
        'faturamento_mes': db.execute("SELECT COALESCE(SUM(total), 0) as t FROM pedidos WHERE pagamento_status = 'approved' AND strftime('%Y-%m', data_pedido) = strftime('%Y-%m', 'now')").fetchone()['t'],
        'faturamento_hoje': db.execute("SELECT COALESCE(SUM(total), 0) as t FROM pedidos WHERE pagamento_status = 'approved' AND date(data_pedido) = date('now')").fetchone()['t'],
        'total_pix': db.execute("SELECT COALESCE(SUM(total), 0) as t FROM pedidos WHERE pagamento_metodo = 'pix' AND pagamento_status = 'approved'").fetchone()['t'],
        'total_dinheiro': db.execute("SELECT COALESCE(SUM(total), 0) as t FROM pedidos WHERE pagamento_metodo = 'dinheiro' AND pagamento_status = 'approved'").fetchone()['t'],
        'total_taxas': db.execute("SELECT COALESCE(SUM(taxa_entrega), 0) as t FROM pedidos WHERE pagamento_status = 'approved'").fetchone()['t'],
        'total_descontos': db.execute("SELECT COALESCE(SUM(desconto), 0) as t FROM pedidos WHERE pagamento_status = 'approved'").fetchone()['t']
    })

@api_bp.route('/api/financeiro/extrato')
def extrato_financeiro():
    db = get_db()
    limite = request.args.get('limite', 50, type=int)
    
    pedidos = [dict(r) for r in db.execute(
        'SELECT numero, total, pagamento_metodo, pagamento_status, data_pedido FROM pedidos ORDER BY data_pedido DESC LIMIT ?',
        (limite,)
    ).fetchall()]
    
    return jsonify(pedidos)

@api_bp.route('/api/financeiro/recargas')
def listar_recargas():
    db = get_db()
    limite = request.args.get('limite', 50, type=int)
    
    recargas = [dict(r) for r in db.execute(
        'SELECT r.*, c.nome FROM recargas r JOIN clientes c ON r.cliente_id = c.id ORDER BY r.data DESC LIMIT ?',
        (limite,)
    ).fetchall()]
    
    return jsonify(recargas)

@api_bp.route('/api/financeiro/pix/pendentes')
def pix_pendentes():
    db = get_db()
    peds = [dict(r) for r in db.execute(
        "SELECT p.*, c.nome FROM pedidos p JOIN clientes c ON p.cliente_id = c.id WHERE p.pagamento_metodo = 'pix' AND p.pagamento_status = 'pendente' ORDER BY p.data_pedido"
    ).fetchall()]
    return jsonify(peds)

@api_bp.route('/api/financeiro/pix/verificar/<int:pedido_id>', methods=['POST'])
def verificar_pix_manual(pedido_id):
    pix_service = PixService()
    result = pix_service.verificar_manualmente(pedido_id)
    return jsonify(result)

@api_bp.route('/api/financeiro/pix/aprovar/<int:pedido_id>', methods=['POST'])
def aprovar_pix_manual(pedido_id):
    db = get_db()
    db.execute("UPDATE pedidos SET pagamento_status = 'approved', status = 'confirmado' WHERE id = ?", (pedido_id,))
    db.commit()
    return jsonify({'sucesso': True, 'mensagem': 'Pagamento aprovado!'})

@api_bp.route('/api/financeiro/reembolsar/<int:pedido_id>', methods=['POST'])
def reembolsar_pedido(pedido_id):
    db = get_db()
    pedido = db.execute('SELECT * FROM pedidos WHERE id = ?', (pedido_id,)).fetchone()
    
    if not pedido:
        return jsonify({'sucesso': False, 'mensagem': 'Pedido não encontrado'})
    
    pg = PagamentoService()
    if pedido.get('pagamento_id') and not pedido['pagamento_id'].startswith('manual_'):
        pg.reembolsar(pedido['pagamento_id'])
    
    db.execute("UPDATE pedidos SET status = 'reembolsado', pagamento_status = 'refunded' WHERE id = ?", (pedido_id,))
    
    # Devolve estoque
    itens = db.execute('SELECT * FROM itens_pedido WHERE pedido_id = ?', (pedido_id,)).fetchall()
    for item in itens:
        db.execute('UPDATE produtos SET estoque = estoque + ? WHERE nome = ?',
                   (item['quantidade'], item['produto_nome']))
    
    db.commit()
    return jsonify({'sucesso': True, 'mensagem': 'Reembolso realizado!'})
