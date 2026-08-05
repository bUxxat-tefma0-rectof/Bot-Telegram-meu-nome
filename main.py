"""
Loja Digital Telegram - Sistema Completo
Arquivo principal de inicialização
"""

import os
import sys
import logging
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Criar pastas necessárias
os.makedirs('logs', exist_ok=True)
os.makedirs('backups', exist_ok=True)
os.makedirs('storage/temp', exist_ok=True)
os.makedirs('storage/exports', exist_ok=True)
os.makedirs('uploads/produtos', exist_ok=True)
os.makedirs('uploads/banners', exist_ok=True)
os.makedirs('uploads/logos', exist_ok=True)

from config.geral import Config
from database.connection import init_database, get_db
from services.scheduler import SchedulerService
from services.backup import BackupService

# Flask
from flask import Flask, send_from_directory, jsonify, request, Response
from flask_cors import CORS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/loja.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def create_flask_app():
    app = Flask(__name__, static_folder='webapp/assets', static_url_path='/assets')
    CORS(app)
    
    # ============ ROTAS WEB ============
    @app.route('/')
    def home():
        return jsonify({'status': 'online', 'sistema': Config.NOME_LOJA, 'versao': '2.0.0'})
    
    @app.route('/app')
    def webapp_loja():
        return send_from_directory('webapp', 'index.html')
    
    @app.route('/admin')
    def webapp_admin():
        return send_from_directory('webapp', 'admin.html')
    
    @app.route('/webapp/<path:path>')
    def serve_webapp(path):
        return send_from_directory('webapp', path)
    
    # ============ API CATEGORIAS ============
    @app.route('/api/categorias')
    def api_categorias():
        db = get_db()
        cats = [dict(r) for r in db.execute('SELECT * FROM categorias WHERE ativo = 1 ORDER BY ordem').fetchall()]
        return jsonify(cats)
    
    # ============ API PRODUTOS ============
    @app.route('/api/produtos')
    def api_produtos():
        db = get_db()
        categoria_id = request.args.get('categoria_id')
        limite = request.args.get('limite', 50, type=int)
        if categoria_id:
            prods = [dict(r) for r in db.execute('SELECT * FROM produtos WHERE categoria_id = ? AND disponivel = 1 AND estoque > 0 AND oculto = 0 ORDER BY destaque DESC LIMIT ?', (categoria_id, limite)).fetchall()]
        else:
            prods = [dict(r) for r in db.execute('SELECT * FROM produtos WHERE disponivel = 1 AND estoque > 0 AND oculto = 0 ORDER BY destaque DESC LIMIT ?', (limite,)).fetchall()]
        return jsonify({'produtos': prods})
    
    @app.route('/api/produtos/ofertas')
    def api_ofertas():
        db = get_db()
        prods = [dict(r) for r in db.execute('SELECT * FROM produtos WHERE disponivel = 1 AND estoque > 0 AND preco_promocional IS NOT NULL ORDER BY ((preco - preco_promocional) / preco * 100) DESC LIMIT 30').fetchall()]
        return jsonify({'produtos': prods})
    
    @app.route('/api/produtos/pesquisar')
    def api_pesquisar():
        q = request.args.get('q', '')
        if len(q) < 2: return jsonify({'produtos': []})
        db = get_db()
        busca = f'%{q}%'
        prods = [dict(r) for r in db.execute('SELECT * FROM produtos WHERE disponivel = 1 AND estoque > 0 AND (nome LIKE ? OR marca LIKE ? OR descricao LIKE ?) LIMIT 30', (busca, busca, busca)).fetchall()]
        return jsonify({'produtos': prods})
    
    # ============ API CARRINHO ============
    @app.route('/api/carrinho')
    def api_carrinho():
        user_id = request.args.get('userId')
        if not user_id: return jsonify({'itens': []})
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return jsonify({'itens': []})
        itens = [dict(r) for r in db.execute("SELECT c.*, p.nome, p.preco, p.preco_promocional, p.foto, p.marca, p.estoque FROM carrinhos c JOIN produtos p ON c.produto_id = p.id WHERE c.cliente_id = ? AND p.disponivel = 1", (cliente['id'],)).fetchall()]
        return jsonify({'itens': itens})
    
    @app.route('/api/carrinho/add', methods=['POST'])
    def api_carrinho_add():
        data = request.json
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (data.get('userId'),)).fetchone()
        if not cliente: return jsonify({'sucesso': False})
        existe = db.execute('SELECT * FROM carrinhos WHERE cliente_id = ? AND produto_id = ?', (cliente['id'], data.get('produtoId'))).fetchone()
        if existe:
            db.execute('UPDATE carrinhos SET quantidade = quantidade + ? WHERE id = ?', (data.get('quantidade', 1), existe['id']))
        else:
            db.execute('INSERT INTO carrinhos (cliente_id, produto_id, quantidade) VALUES (?,?,?)', (cliente['id'], data.get('produtoId'), data.get('quantidade', 1)))
        db.commit()
        return jsonify({'sucesso': True})
    
    @app.route('/api/carrinho/update', methods=['POST'])
    def api_carrinho_update():
        data = request.json
        db = get_db()
        if data.get('quantidade', 1) > 0:
            db.execute('UPDATE carrinhos SET quantidade = ? WHERE id = ?', (data['quantidade'], data['carrinhoId']))
        else:
            db.execute('DELETE FROM carrinhos WHERE id = ?', (data['carrinhoId'],))
        db.commit()
        return jsonify({'sucesso': True})
    
    @app.route('/api/carrinho/remover', methods=['POST'])
    def api_carrinho_remover():
        db = get_db()
        db.execute('DELETE FROM carrinhos WHERE id = ?', (request.json.get('carrinhoId'),))
        db.commit()
        return jsonify({'sucesso': True})
    
    # ============ API PERFIL ============
    @app.route('/api/perfil')
    def api_perfil():
        user_id = request.args.get('userId')
        if not user_id: return jsonify({})
        db = get_db()
        cliente = db.execute('SELECT * FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return jsonify({})
        total_pedidos = db.execute('SELECT COUNT(*) as t FROM pedidos WHERE cliente_id = ?', (cliente['id'],)).fetchone()['t']
        result = dict(cliente)
        result['total_pedidos'] = total_pedidos
        return jsonify(result)
    
    # ============ API PEDIDOS ============
    @app.route('/api/pedidos')
    def api_pedidos():
        user_id = request.args.get('userId')
        if not user_id: return jsonify({'pedidos': []})
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return jsonify({'pedidos': []})
        pedidos = [dict(r) for r in db.execute('SELECT * FROM pedidos WHERE cliente_id = ? ORDER BY data_pedido DESC LIMIT 20', (cliente['id'],)).fetchall()]
        return jsonify({'pedidos': pedidos})
    
    @app.route('/api/pedidos/finalizar', methods=['POST'])
    def api_pedidos_finalizar():
        try:
            data = request.json
            db = get_db()
            cliente = db.execute('SELECT * FROM clientes WHERE telegram_id = ?', (data.get('userId'),)).fetchone()
            if not cliente: return jsonify({'sucesso': False, 'mensagem': 'Cliente não encontrado'})
            
            itens = [dict(r) for r in db.execute("SELECT c.*, p.nome, p.preco, p.preco_promocional, p.estoque FROM carrinhos c JOIN produtos p ON c.produto_id = p.id WHERE c.cliente_id = ?", (cliente['id'],)).fetchall()]
            if not itens: return jsonify({'sucesso': False, 'mensagem': 'Carrinho vazio'})
            
            for item in itens:
                if item['quantidade'] > item['estoque']:
                    return jsonify({'sucesso': False, 'mensagem': f'Estoque insuficiente: {item["nome"]}'})
            
            subtotal = sum((i.get('preco_promocional') or i['preco']) * i['quantidade'] for i in itens)
            taxa = Config.TAXA_ENTREGA
            total = subtotal + taxa
            
            from utils.helpers import gerar_numero_pedido
            numero = gerar_numero_pedido()
            
            cursor = db.execute("INSERT INTO pedidos (numero, cliente_id, status, subtotal, taxa_entrega, total, pagamento_metodo) VALUES (?, ?, 'recebido', ?, ?, ?, ?)", (numero, cliente['id'], subtotal, taxa, total, data.get('metodoPagamento', 'pix')))
            pedido_id = cursor.lastrowid
            
            for item in itens:
                preco = item.get('preco_promocional') or item['preco']
                db.execute('INSERT INTO itens_pedido (pedido_id, produto_nome, quantidade, preco_unitario) VALUES (?,?,?,?)', (pedido_id, item['nome'], item['quantidade'], preco))
                db.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', (item['quantidade'], item['produto_id']))
            
            db.execute('DELETE FROM carrinhos WHERE cliente_id = ?', (cliente['id'],))
            db.commit()
            
            result = {'sucesso': True, 'numero': numero, 'total': total, 'pedido_id': pedido_id}
            
            if data.get('metodoPagamento') == 'pix':
                from services.pagamento import PagamentoService
                pg = PagamentoService()
                pix = pg.gerar_pix(total, f'Pedido {numero}', numero)
                if pix.get('sucesso'):
                    db.execute('UPDATE pedidos SET pagamento_id = ?, pagamento_qrcode = ? WHERE id = ?', (pix['payment_id'], pix['copia_cola'], pedido_id))
                    db.commit()
                    result['pagamento'] = {'qr_code_base64': pix.get('qr_code_base64', ''), 'copia_cola': pix.get('copia_cola', ''), 'payment_id': pix['payment_id']}
            
            return jsonify(result)
        except Exception as e:
            logger.error(f'Erro pedido: {e}')
            return jsonify({'sucesso': False, 'mensagem': 'Erro interno'})
    
    # ============ API CEP ============
    @app.route('/api/cep/<cep>')
    def api_cep(cep):
        from services.cep import CepService
        return jsonify(CepService.consultar(cep))
    
    # ============ API ENDEREÇOS ============
    @app.route('/api/enderecos')
    def api_enderecos():
        user_id = request.args.get('userId')
        if not user_id: return jsonify([])
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return jsonify([])
        enderecos = [dict(r) for r in db.execute('SELECT * FROM enderecos WHERE cliente_id = ? ORDER BY principal DESC', (cliente['id'],)).fetchall()]
        return jsonify(enderecos)
    
    @app.route('/api/enderecos/salvar', methods=['POST'])
    def api_endereco_salvar():
        data = request.json
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (data.get('userId'),)).fetchone()
        if not cliente: return jsonify({'sucesso': False})
        total = db.execute('SELECT COUNT(*) as t FROM enderecos WHERE cliente_id = ?', (cliente['id'],)).fetchone()['t']
        principal = 1 if total == 0 else 0
        db.execute('INSERT INTO enderecos (cliente_id, apelido, cep, logradouro, numero, complemento, referencia, bairro, cidade, estado, principal) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                   (cliente['id'], data.get('apelido','Principal'), data.get('cep'), data.get('logradouro'), data.get('numero'), data.get('complemento'), data.get('referencia'), data.get('bairro'), data.get('cidade'), data.get('estado'), principal))
        db.commit()
        return jsonify({'sucesso': True})
    
    @app.route('/api/enderecos/deletar', methods=['POST'])
    def api_endereco_deletar():
        db = get_db()
        db.execute('DELETE FROM enderecos WHERE id = ?', (request.json.get('enderecoId'),))
        db.commit()
        return jsonify({'sucesso': True})
    
    @app.route('/api/enderecos/principal', methods=['POST'])
    def api_endereco_principal():
        data = request.json
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (data.get('userId'),)).fetchone()
        if cliente:
            db.execute('UPDATE enderecos SET principal = 0 WHERE cliente_id = ?', (cliente['id'],))
            db.execute('UPDATE enderecos SET principal = 1 WHERE id = ?', (data.get('enderecoId'),))
            db.commit()
        return jsonify({'sucesso': True})
    
    # ============ API CUPONS ============
    @app.route('/api/cupons/validar')
    def api_cupom_validar():
        from database.models.cupom import CupomModel
        return jsonify(CupomModel.validar(request.args.get('codigo', '')))
    
    # ============ API AFILIADOS ============
    @app.route('/api/afiliados/me')
    def api_afiliado_me():
        user_id = request.args.get('userId')
        if not user_id: return jsonify({})
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return jsonify({})
        afiliado = db.execute('SELECT * FROM afiliados WHERE cliente_id = ?', (cliente['id'],)).fetchone()
        return jsonify(dict(afiliado) if afiliado else {})
    
    @app.route('/api/afiliados/saque', methods=['POST'])
    def api_afiliado_saque():
        data = request.json
        from database.models.afiliado import AfiliadoModel
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (data.get('userId'),)).fetchone()
        if not cliente: return jsonify({'sucesso': False})
        afiliado = db.execute('SELECT * FROM afiliados WHERE cliente_id = ?', (cliente['id'],)).fetchone()
        if not afiliado: return jsonify({'sucesso': False})
        return jsonify(AfiliadoModel.solicitar_saque(afiliado['id'], float(data.get('valor', 0))))
    
    # ============ API RANKING ============
    @app.route('/api/ranking')
    def api_ranking():
        from database.models.cliente import ClienteModel
        return jsonify(ClienteModel.get_ranking())
    
    # ============ API NOTIFICAÇÕES ============
    @app.route('/api/notificacoes')
    def api_notificacoes():
        user_id = request.args.get('userId')
        if not user_id: return jsonify([])
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente: return jsonify([])
        notifs = [dict(r) for r in db.execute('SELECT * FROM notificacoes WHERE cliente_id = ? ORDER BY data DESC LIMIT 20', (cliente['id'],)).fetchall()]
        return jsonify(notifs)
    
    # ============ API ADMIN ============
    @app.route('/api/admin/dashboard')
    def api_admin_dashboard():
        from admin.dashboard import DashboardAdmin
        stats = DashboardAdmin.get_estatisticas()
        top = DashboardAdmin.get_top_produtos(5)
        return jsonify({**stats, 'top_produtos': top})
    
    @app.route('/api/admin/produtos')
    def api_admin_produtos():
        from admin.produtos import ProdutosAdmin
        return jsonify(ProdutosAdmin.listar())
    
    @app.route('/api/admin/produtos/<int:produto_id>', methods=['PUT', 'DELETE'])
    def api_admin_produto(produto_id):
        from admin.produtos import ProdutosAdmin
        if request.method == 'PUT': return jsonify(ProdutosAdmin.editar(produto_id, request.json))
        return jsonify(ProdutosAdmin.excluir(produto_id))
    
    @app.route('/api/admin/produtos/<int:produto_id>/toggle', methods=['POST'])
    def api_admin_toggle_produto(produto_id):
        from admin.produtos import ProdutosAdmin
        return jsonify(ProdutosAdmin.toggle_status(produto_id))
    
    @app.route('/api/admin/pedidos')
    def api_admin_pedidos():
        from admin.pedidos import PedidosAdmin
        return jsonify(PedidosAdmin.listar(filtro=request.args.get('filtro', 'pendentes')))
    
    @app.route('/api/admin/pedidos/<int:pedido_id>/status', methods=['PUT'])
    def api_admin_pedido_status(pedido_id):
        from admin.pedidos import PedidosAdmin
        return jsonify(PedidosAdmin.alterar_status(pedido_id, request.json.get('status')))
    
    @app.route('/api/admin/clientes')
    def api_admin_clientes():
        from admin.clientes import ClientesAdmin
        return jsonify(ClientesAdmin.listar())
    
    @app.route('/api/admin/clientes/<int:cliente_id>/toggle', methods=['POST'])
    def api_admin_toggle_cliente(cliente_id):
        from admin.clientes import ClientesAdmin
        return jsonify(ClientesAdmin.toggle_bloqueio(cliente_id))
    
    @app.route('/api/admin/financeiro')
    def api_admin_financeiro():
        from admin.financeiro import FinanceiroAdmin
        return jsonify(FinanceiroAdmin.get_resumo())
    
    @app.route('/api/admin/cupons')
    def api_admin_cupons():
        from admin.cupons import CuponsAdmin
        return jsonify(CuponsAdmin.listar())
    
    @app.route('/api/admin/cupons/<int:cupom_id>/toggle', methods=['POST'])
    def api_admin_toggle_cupom(cupom_id):
        from admin.cupons import CuponsAdmin
        return jsonify(CuponsAdmin.toggle(cupom_id))
    
    @app.route('/api/admin/afiliados')
    def api_admin_afiliados():
        from admin.afiliados import AfiliadosAdmin
        return jsonify(AfiliadosAdmin.listar())
    
    @app.route('/api/admin/mensagens')
    def api_admin_mensagens():
        from admin.mensagens import MensagensAdmin
        return jsonify(MensagensAdmin.listar())
    
    @app.route('/api/admin/mensagens', methods=['PUT'])
    def api_admin_editar_mensagem():
        from admin.mensagens import MensagensAdmin
        data = request.json
        return jsonify(MensagensAdmin.editar(data['chave'], data['conteudo']))
    
    @app.route('/api/admin/botoes')
    def api_admin_botoes():
        from admin.botoes import BotoesAdmin
        return jsonify(BotoesAdmin.listar())
    
    @app.route('/api/admin/botoes/<int:botao_id>/toggle', methods=['POST'])
    def api_admin_toggle_botao(botao_id):
        from admin.botoes import BotoesAdmin
        return jsonify(BotoesAdmin.toggle(botao_id))
    
    @app.route('/api/admin/aparencia')
    def api_admin_aparencia():
        from admin.temas import TemasAdmin
        return jsonify(TemasAdmin.get_tema_atual())
    
    @app.route('/api/admin/aparencia', methods=['PUT'])
    def api_admin_salvar_aparencia():
        from admin.temas import TemasAdmin
        return jsonify(TemasAdmin.salvar_tema(request.json))
    
    @app.route('/api/admin/config')
    def api_admin_config():
        from admin.config import ConfigAdmin
        configs = ConfigAdmin.get_todas()
        flat = {}
        for cat, items in configs.items():
            for chave, info in items.items():
                flat[chave] = info['valor']
        return jsonify(flat)
    
    @app.route('/api/admin/config', methods=['PUT'])
    def api_admin_salvar_config():
        from admin.config import ConfigAdmin
        return jsonify(ConfigAdmin.salvar_varias(request.json))
    
    @app.route('/api/admin/backup', methods=['POST'])
    def api_admin_backup():
        return jsonify(BackupService.realizar_backup())
    
    @app.route('/api/admin/exportar/<tipo>')
    def api_admin_exportar(tipo):
        from services.exportacao import ExportacaoService
        if tipo == 'produtos': result = ExportacaoService.exportar_produtos_csv()
        elif tipo == 'pedidos': result = ExportacaoService.exportar_pedidos_csv()
        elif tipo == 'clientes': result = ExportacaoService.exportar_clientes_csv()
        else: return jsonify({'erro': 'Tipo inválido'})
        return Response(result['dados'], mimetype='text/csv', headers={'Content-Disposition': f'attachment;filename={tipo}.csv'})
    
    # ============ WEBHOOK ============
    @app.route('/api/webhooks/mercadopago', methods=['POST'])
    def api_webhook_mp():
        from services.webhook import WebhookService
        ws = WebhookService()
        result = ws.processar_webhook_mercadopago(request.json or {})
        return jsonify({'status': 'ok', 'result': result})
    
    # ============ ERROS ============
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'erro': 'Rota não encontrada'}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'erro': 'Erro interno do servidor'}), 500
    
    return app


def main():
    logger.info('🛒 Iniciando Loja Digital Telegram...')
    
    init_database()
    logger.info('✅ Banco de dados pronto')
    
    scheduler = SchedulerService()
    scheduler.iniciar()
    logger.info('✅ Agendador iniciado')
    
    BackupService.agendar_backup_automatico()
    
    from bot.cliente import LojaBot
    bot_cliente = LojaBot()
    threading.Thread(target=bot_cliente.run, daemon=True).start()
    logger.info('✅ Bot Cliente iniciado')
    
    from bot.admin import start_bot_admin
    threading.Thread(target=start_bot_admin, daemon=True).start()
    logger.info('✅ Bot Admin iniciado')
    
    app = create_flask_app()
    port = int(os.getenv('PORT', 3000))
    
    logger.info(f'🌐 Servidor na porta {port}')
    logger.info(f'🛍️ WebApp: http://localhost:{port}/app')
    logger.info(f'👑 Admin: http://localhost:{port}/admin')
    logger.info('🛒 Loja Digital pronta!')
    
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    main()
