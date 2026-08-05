from flask import jsonify, request
from . import api_bp
from database.connection import get_db
from admin.dashboard import DashboardAdmin
from admin.produtos import ProdutosAdmin
from admin.categorias import CategoriasAdmin
from admin.pedidos import PedidosAdmin
from admin.clientes import ClientesAdmin
from admin.financeiro import FinanceiroAdmin
from admin.cupons import CuponsAdmin
from admin.afiliados import AfiliadosAdmin
from admin.mensagens import MensagensAdmin
from admin.botoes import BotoesAdmin
from admin.temas import TemasAdmin
from admin.config import ConfigAdmin
from services.backup import BackupService

# ============ DASHBOARD ============
@api_bp.route('/admin/dashboard')
def admin_dashboard():
    stats = DashboardAdmin.get_estatisticas()
    top = DashboardAdmin.get_top_produtos(5)
    return jsonify({**stats, 'top_produtos': top})

# ============ PRODUTOS ============
@api_bp.route('/admin/produtos')
def admin_produtos():
    pagina = request.args.get('pagina', 1, type=int)
    result = ProdutosAdmin.listar(pagina=pagina)
    return jsonify(result)

@api_bp.route('/admin/produtos/<int:produto_id>', methods=['GET', 'PUT', 'DELETE'])
def admin_produto(produto_id):
    if request.method == 'GET':
        db = get_db()
        p = db.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,)).fetchone()
        return jsonify(dict(p) if p else {})
    elif request.method == 'PUT':
        return jsonify(ProdutosAdmin.editar(produto_id, request.json))
    elif request.method == 'DELETE':
        return jsonify(ProdutosAdmin.excluir(produto_id))

@api_bp.route('/admin/produtos/<int:produto_id>/toggle', methods=['POST'])
def admin_toggle_produto(produto_id):
    return jsonify(ProdutosAdmin.toggle_status(produto_id))

# ============ CATEGORIAS ============
@api_bp.route('/admin/categorias')
def admin_categorias():
    return jsonify(CategoriasAdmin.listar())

# ============ PEDIDOS ============
@api_bp.route('/admin/pedidos')
def admin_pedidos():
    filtro = request.args.get('filtro', 'pendentes')
    result = PedidosAdmin.listar(filtro=filtro)
    return jsonify(result)

@api_bp.route('/admin/pedidos/<int:pedido_id>/status', methods=['PUT'])
def admin_pedido_status(pedido_id):
    status = request.json.get('status')
    return jsonify(PedidosAdmin.alterar_status(pedido_id, status))

# ============ CLIENTES ============
@api_bp.route('/admin/clientes')
def admin_clientes():
    result = ClientesAdmin.listar()
    return jsonify(result)

@api_bp.route('/admin/clientes/<int:cliente_id>/toggle', methods=['POST'])
def admin_toggle_cliente(cliente_id):
    return jsonify(ClientesAdmin.toggle_bloqueio(cliente_id))

# ============ FINANCEIRO ============
@api_bp.route('/admin/financeiro')
def admin_financeiro():
    return jsonify(FinanceiroAdmin.get_resumo())

# ============ CUPONS ============
@api_bp.route('/admin/cupons')
def admin_cupons():
    return jsonify(CuponsAdmin.listar())

@api_bp.route('/admin/cupons/<int:cupom_id>/toggle', methods=['POST'])
def admin_toggle_cupom(cupom_id):
    return jsonify(CuponsAdmin.toggle(cupom_id))

# ============ AFILIADOS ============
@api_bp.route('/admin/afiliados')
def admin_afiliados():
    return jsonify(AfiliadosAdmin.listar())

# ============ MENSAGENS ============
@api_bp.route('/admin/mensagens')
def admin_mensagens():
    return jsonify(MensagensAdmin.listar())

@api_bp.route('/admin/mensagens', methods=['PUT'])
def admin_editar_mensagem():
    data = request.json
    return jsonify(MensagensAdmin.editar(data['chave'], data['conteudo']))

# ============ BOTÕES ============
@api_bp.route('/admin/botoes')
def admin_botoes():
    return jsonify(BotoesAdmin.listar())

@api_bp.route('/admin/botoes/<int:botao_id>/toggle', methods=['POST'])
def admin_toggle_botao(botao_id):
    return jsonify(BotoesAdmin.toggle(botao_id))

# ============ APARÊNCIA ============
@api_bp.route('/admin/aparencia')
def admin_aparencia():
    return jsonify(TemasAdmin.get_tema_atual())

@api_bp.route('/admin/aparencia', methods=['PUT'])
def admin_salvar_aparencia():
    return jsonify(TemasAdmin.salvar_tema(request.json))

# ============ CONFIGURAÇÕES ============
@api_bp.route('/admin/config')
def admin_config():
    configs = ConfigAdmin.get_todas()
    flat = {}
    for cat, items in configs.items():
        for chave, info in items.items():
            flat[chave] = info['valor']
    return jsonify(flat)

@api_bp.route('/admin/config', methods=['PUT'])
def admin_salvar_config():
    return jsonify(ConfigAdmin.salvar_varias(request.json))

# ============ BACKUP ============
@api_bp.route('/admin/backup', methods=['POST'])
def admin_backup():
    return jsonify(BackupService.realizar_backup())

# ============ EXPORTAÇÃO ============
@api_bp.route('/admin/exportar/<tipo>')
def admin_exportar(tipo):
    from services.exportacao import ExportacaoService
    from flask import Response
    
    if tipo == 'produtos':
        result = ExportacaoService.exportar_produtos_csv()
    elif tipo == 'pedidos':
        result = ExportacaoService.exportar_pedidos_csv()
    elif tipo == 'clientes':
        result = ExportacaoService.exportar_clientes_csv()
    else:
        return jsonify({'erro': 'Tipo inválido'})
    
    return Response(result['dados'], mimetype='text/csv', 
                   headers={'Content-Disposition': f'attachment;filename={tipo}.csv'})
