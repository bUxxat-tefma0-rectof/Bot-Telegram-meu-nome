from flask import jsonify, request
from . import api_bp
from database.connection import get_db

@api_bp.route('/api/produtos')
def api_produtos():
    db = get_db()
    categoria_id = request.args.get('categoria_id')
    limite = request.args.get('limite', 50, type=int)
    
    if categoria_id:
        prods = [dict(r) for r in db.execute(
            'SELECT * FROM produtos WHERE categoria_id = ? AND disponivel = 1 AND estoque > 0 AND oculto = 0 ORDER BY destaque DESC LIMIT ?',
            (categoria_id, limite)
        ).fetchall()]
    else:
        prods = [dict(r) for r in db.execute(
            'SELECT * FROM produtos WHERE disponivel = 1 AND estoque > 0 AND oculto = 0 ORDER BY destaque DESC LIMIT ?',
            (limite,)
        ).fetchall()]
    
    return jsonify({'produtos': prods})

@api_bp.route('/api/produtos/ofertas')
def api_ofertas():
    db = get_db()
    prods = [dict(r) for r in db.execute(
        'SELECT * FROM produtos WHERE disponivel = 1 AND estoque > 0 AND preco_promocional IS NOT NULL ORDER BY ((preco - preco_promocional) / preco * 100) DESC LIMIT 30'
    ).fetchall()]
    return jsonify({'produtos': prods})

@api_bp.route('/api/produtos/pesquisar')
def api_pesquisar():
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify({'produtos': []})
    
    db = get_db()
    busca = f'%{q}%'
    prods = [dict(r) for r in db.execute(
        'SELECT * FROM produtos WHERE disponivel = 1 AND estoque > 0 AND (nome LIKE ? OR marca LIKE ? OR descricao LIKE ?) LIMIT 30',
        (busca, busca, busca)
    ).fetchall()]
    return jsonify({'produtos': prods})

@api_bp.route('/api/produtos/<int:produto_id>')
def api_produto(produto_id):
    db = get_db()
    p = db.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,)).fetchone()
    return jsonify(dict(p) if p else {})
