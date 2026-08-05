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

from config.geral import Config
from database.connection import init_database, get_db
from services.scheduler import SchedulerService
from services.backup import BackupService
from services.logs import LogService

# Flask para API e WebApp
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

# Configuração de logging
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
    """Cria a aplicação Flask para API e WebApp"""
    app = Flask(__name__, 
                static_folder='webapp/assets',
                static_url_path='/assets')
    
    CORS(app)
    
    # ============ ROTAS WEB ============
    
    @app.route('/')
    def home():
        return jsonify({
            'status': 'online',
            'sistema': Config.NOME_LOJA,
            'versao': '2.0.0',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
    
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
        cats = [dict(r) for r in db.execute(
            'SELECT * FROM categorias WHERE ativo = 1 ORDER BY ordem'
        ).fetchall()]
        return jsonify(cats)
    
    # ============ API PRODUTOS ============
    
    @app.route('/api/produtos')
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
    
    @app.route('/api/produtos/ofertas')
    def api_ofertas():
        db = get_db()
        prods = [dict(r) for r in db.execute(
            'SELECT * FROM produtos WHERE disponivel = 1 AND estoque > 0 AND preco_promocional IS NOT NULL ORDER BY ((preco - preco_promocional) / preco * 100) DESC LIMIT 30'
        ).fetchall()]
        return jsonify({'produtos': prods})
    
    @app.route('/api/produtos/pesquisar')
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
    
    @app.route('/api/produtos/<int:produto_id>')
    def api_produto(produto_id):
        db = get_db()
        p = db.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,)).fetchone()
        return jsonify(dict(p) if p else {})
    
    # ============ API CARRINHO ============
    
    @app.route('/api/carrinho')
    def api_carrinho():
        user_id = request.args.get('userId')
        if not user_id:
            return jsonify({'itens': []})
        
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente:
            return jsonify({'itens': []})
        
        itens = [dict(r) for r in db.execute(
            '''SELECT c.*, p.nome, p.preco, p.preco_promocional, p.foto, p.marca, p.estoque
               FROM carrinhos c JOIN produtos p ON c.produto_id = p.id
               WHERE c.cliente_id = ? AND p.disponivel = 1''',
            (cliente['id'],)
        ).fetchall()]
        
        return jsonify({'itens': itens})
    
    @app.route('/api/carrinho/add', methods=['POST'])
    def api_carrinho_add():
        data = request.json
        user_id = data.get('userId')
        produto_id = data.get('produtoId')
        quantidade = data.get('quantidade', 1)
        
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente:
            return jsonify({'sucesso': False, 'mensagem': 'Cliente não encontrado'})
        
        produto = db.execute('SELECT * FROM produtos WHERE id = ? AND disponivel = 1', (produto_id,)).fetchone()
        if not produto:
            return jsonify({'sucesso': False, 'mensagem': 'Produto indisponível'})
        if produto['estoque'] < quantidade:
            return jsonify({'sucesso': False, 'mensagem': 'Estoque insuficiente'})
        
        existe = db.execute('SELECT * FROM carrinhos WHERE cliente_id = ? AND produto_id = ?',
                           (cliente['id'], produto_id)).fetchone()
        
        if existe:
            db.execute('UPDATE carrinhos SET quantidade = quantidade + ? WHERE id = ?',
                       (quantidade, existe['id']))
        else:
            db.execute('INSERT INTO carrinhos (cliente_id, produto_id, quantidade) VALUES (?,?,?)',
                       (cliente['id'], produto_id, quantidade))
        db.commit()
        
        return jsonify({'sucesso': True, 'mensagem': 'Adicionado ao carrinho!'})
    
    @app.route('/api/carrinho/update', methods=['POST'])
    def api_carrinho_update():
        data = request.json
        carrinho_id = data.get('carrinhoId')
        quantidade = data.get('quantidade', 1)
        
        db = get_db()
        if quantidade > 0:
            db.execute('UPDATE carrinhos SET quantidade = ? WHERE id = ?', (quantidade, carrinho_id))
        else:
            db.execute('DELETE FROM carrinhos WHERE id = ?', (carrinho_id,))
        db.commit()
        
        return jsonify({'sucesso': True})
    
    @app.route('/api/carrinho/remover', methods=['POST'])
    def api_carrinho_remover():
        data = request.json
        db = get_db()
        db.execute('DELETE FROM carrinhos WHERE id = ?', (data.get('carrinhoId'),))
        db.commit()
        return jsonify({'sucesso': True})
    
    # ============ API PERFIL ============
    
    @app.route('/api/perfil')
    def api_perfil():
        user_id = request.args.get('userId')
        if not user_id:
            return jsonify({})
        
        db = get_db()
        cliente = db.execute('SELECT * FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente:
            return jsonify({})
        
        total_pedidos = db.execute('SELECT COUNT(*) as t FROM pedidos WHERE cliente_id = ?',
                                   (cliente['id'],)).fetchone()['t']
        
        result = dict(cliente)
        result['total_pedidos'] = total_pedidos
        
        return jsonify(result)
    
    # ============ API PEDIDOS ============
    
    @app.route('/api/pedidos')
    def api_pedidos():
        user_id = request.args.get('userId')
        if not user_id:
            return jsonify({'pedidos': []})
        
        db = get_db()
        cliente = db.execute('SELECT id FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente:
            return jsonify({'pedidos': []})
        
        pedidos = [dict(r) for r in db.execute(
            'SELECT * FROM pedidos WHERE cliente_id = ? ORDER BY data_pedido DESC LIMIT 20',
            (cliente['id'],)
        ).fetchall()]
        
        return jsonify({'pedidos': pedidos})
    
    @app.route('/api/pedidos/finalizar', methods=['POST'])
    def api_pedidos_finalizar():
        try:
            data = request.json
            user_id = data.get('userId')
            metodo = data.get('metodoPagamento', 'pix')
            
            db = get_db()
            cliente = db.execute('SELECT * FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
            if not cliente:
                return jsonify({'sucesso': False, 'mensagem': 'Cliente não encontrado'})
            
            # Busca carrinho
            itens = [dict(r) for r in db.execute(
                '''SELECT c.*, p.nome, p.preco, p.preco_promocional, p.estoque
                   FROM carrinhos c JOIN produtos p ON c.produto_id = p.id
                   WHERE c.cliente_id = ?''', (cliente['id'],)
            ).fetchall()]
            
            if not itens:
                return jsonify({'sucesso': False, 'mensagem': 'Carrinho vazio'})
            
            # Verifica estoque
            for item in itens:
                if item['quantidade'] > item['estoque']:
                    return jsonify({'sucesso': False, 'mensagem': f'Estoque insuficiente: {item["nome"]}'})
            
            # Calcula total
            subtotal = sum((i.get('preco_promocional') or i['preco']) * i['quantidade'] for i in itens)
            taxa = Config.TAXA_ENTREGA
            total = subtotal + taxa
            
            # Gera número
            from utils.helpers import gerar_numero_pedido
            numero = gerar_numero_pedido()
            
            # Cria pedido
            cursor = db.execute('''
                INSERT INTO pedidos (numero, cliente_id, status, subtotal, taxa_entrega, total, pagamento_metodo)
                VALUES (?, ?, 'recebido', ?, ?, ?, ?)
            ''', (numero, cliente['id'], subtotal, taxa, total, metodo))
            pedido_id = cursor.lastrowid
            
            # Itens do pedido
            for item in itens:
                preco = item.get('preco_promocional') or item['preco']
                db.execute('''
                    INSERT INTO itens_pedido (pedido_id, produto_nome, quantidade, preco_unitario)
                    VALUES (?, ?, ?, ?)
                ''', (pedido_id, item['nome'], item['quantidade'], preco))
                
                # Atualiza estoque
                db.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?',
                           (item['quantidade'], item['produto_id']))
            
            # Limpa carrinho
            db.execute('DELETE FROM carrinhos WHERE cliente_id = ?', (cliente['id'],))
            db.commit()
            
            result = {'sucesso': True, 'numero': numero, 'total': total, 'pedido_id': pedido_id}
            
            # Gera PIX se for o método
            if metodo == 'pix':
                from services.pagamento import PagamentoService
                pg = PagamentoService()
                pix = pg.gerar_pix(total, f'Pedido {numero}', numero)
                
                if pix.get('sucesso'):
                    db.execute('''
                        UPDATE pedidos SET pagamento_id = ?, pagamento_qrcode = ?
                        WHERE id = ?
                    ''', (pix['payment_id'], pix['copia_cola'], pedido_id))
                    db.commit()
                    
                    result['pagamento'] = {
                        'qr_code_base64': pix.get('qr_code_base64', ''),
                        'copia_cola': pix.get('copia_cola', ''),
                        'payment_id': pix['payment_id']
                    }
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f'Erro ao finalizar pedido: {e}')
            return jsonify({'sucesso': False, 'mensagem': 'Erro interno'})
    
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
        result = ProdutosAdmin.listar()
        return jsonify(result)
    
    @app.route('/api/admin/produtos/<int:produto_id>', methods=['PUT', 'DELETE'])
    def api_admin_produto(produto_id):
        from admin.produtos import ProdutosAdmin
        if request.method == 'PUT':
            return jsonify(ProdutosAdmin.editar(produto_id, request.json))
        elif request.method == 'DELETE':
            return jsonify(ProdutosAdmin.excluir(produto_id))
    
    @app.route('/api/admin/produtos/<int:produto_id>/toggle', methods=['POST'])
    def api_admin_toggle_produto(produto_id):
        from admin.produtos import ProdutosAdmin
        return jsonify(ProdutosAdmin.toggle_status(produto_id))
    
    @app.route('/api/admin/pedidos')
    def api_admin_pedidos():
        from admin.pedidos import PedidosAdmin
        filtro = request.args.get('filtro', 'pendentes')
        result = PedidosAdmin.listar(filtro=filtro)
        return jsonify(result)
    
    @app.route('/api/admin/pedidos/<int:pedido_id>/status', methods=['PUT'])
    def api_admin_pedido_status(pedido_id):
        from admin.pedidos import PedidosAdmin
        status = request.json.get('status')
        return jsonify(PedidosAdmin.alterar_status(pedido_id, status))
    
    @app.route('/api/admin/clientes')
    def api_admin_clientes():
        from admin.clientes import ClientesAdmin
        result = ClientesAdmin.listar()
        return jsonify(result)
    
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
        from flask import Response
        
        if tipo == 'produtos':
            result = ExportacaoService.exportar_produtos_csv()
        elif tipo == 'pedidos':
            result = ExportacaoService.exportar_pedidos_csv()
        elif tipo == 'clientes':
            result = ExportacaoService.exportar_clientes_csv()
        else:
            return jsonify({'erro': 'Tipo inválido'})
        
        return Response(
            result['dados'],
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename={tipo}.csv'}
        )
    
    return app


def main():
    """Função principal"""
    logger.info('🛒 Iniciando Loja Digital Telegram...')
    
    # Inicializa banco de dados
    init_database()
    logger.info('✅ Banco de dados pronto')
    
    # Inicia agendador
    scheduler = SchedulerService()
    scheduler.iniciar()
    logger.info('✅ Agendador iniciado')
    
    # Backup automático
    BackupService.agendar_backup_automatico()
    
    # Inicia bot cliente
    from bot.cliente import LojaBot
    bot_cliente = LojaBot()
    threading.Thread(target=bot_cliente.run, daemon=True).start()
    logger.info('✅ Bot Cliente iniciado')
    
    # Inicia bot admin
    from bot.admin import start_bot_admin
    threading.Thread(target=start_bot_admin, daemon=True).start()
    logger.info('✅ Bot Admin iniciado')
    
    # Inicia servidor Flask
    app = create_flask_app()
    port = int(os.getenv('PORT', 3000))
    
    logger.info(f'🌐 Servidor web na porta {port}')
    logger.info(f'🛍️ WebApp: http://localhost:{port}/app')
    logger.info(f'👑 Admin: http://localhost:{port}/admin')
    logger.info('🛒 Loja Digital pronta!')
    
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    main()
