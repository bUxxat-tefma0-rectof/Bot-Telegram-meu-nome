from .connection import get_db
import logging

logger = logging.getLogger(__name__)

def inserir_dados_padrao():
    db = get_db()
    
    # Categorias padrão
    if db.execute('SELECT COUNT(*) FROM categorias').fetchone()[0] == 0:
        categorias = [
            ('Eletrônicos', '📱', 'Produtos eletrônicos em geral', '#6366f1'),
            ('Roupas', '👕', 'Moda masculina e feminina', '#ec4899'),
            ('Casa e Decoração', '🏠', 'Itens para seu lar', '#f59e0b'),
            ('Beleza', '💄', 'Cosméticos e perfumaria', '#10b981'),
            ('Esportes', '⚽', 'Artigos esportivos', '#3b82f6'),
            ('Livros', '📚', 'Livros físicos e digitais', '#8b5cf6'),
            ('Brinquedos', '🎮', 'Jogos e brinquedos', '#ef4444'),
            ('Alimentos', '🍎', 'Alimentos e bebidas', '#84cc16')
        ]
        for nome, emoji, desc, cor in categorias:
            db.execute(
                'INSERT INTO categorias (nome, emoji, descricao, cor) VALUES (?,?,?,?)',
                (nome, emoji, desc, cor)
            )
        logger.info('✅ Categorias padrão inseridas')
    
    # Configurações padrão
    if db.execute('SELECT COUNT(*) FROM configuracoes').fetchone()[0] == 0:
        configs = [
            ('nome_loja', 'Loja Digital', 'texto', 'geral', 'Nome da loja'),
            ('msg_start', 'Bem-vindo(a) {nome} à {loja}! 🛒\n\nEscolha uma opção:', 'texto', 'mensagens', 'Mensagem inicial'),
            ('msg_compra', '✅ Pedido {numero} confirmado!\n\n💰 Total: {total}\n📦 Status: {status}', 'texto', 'mensagens', 'Mensagem de compra'),
            ('msg_pix', '💳 PIX gerado para o pedido {numero}\n\n📋 Copia e Cola:\n`{pix}`\n\n⏰ Expira em {expiracao} minutos', 'texto', 'mensagens', 'Mensagem PIX'),
            ('msg_entrega', '🏠 Pedido {numero} entregue!\n\nObrigado por comprar conosco! ❤️', 'texto', 'mensagens', 'Mensagem de entrega'),
            ('cor_primaria', '#6366f1', 'cor', 'aparencia', 'Cor principal'),
            ('cor_secundaria', '#ec4899', 'cor', 'aparencia', 'Cor secundária'),
            ('cor_fundo', '#f8fafc', 'cor', 'aparencia', 'Cor de fundo'),
            ('tema', 'light', 'tema', 'aparencia', 'Tema (light/dark)'),
            ('comissao_padrao', '5', 'numero', 'afiliados', 'Comissão padrão (%)'),
            ('pedido_minimo', '10', 'numero', 'geral', 'Pedido mínimo (R$)'),
            ('taxa_entrega', '5', 'numero', 'geral', 'Taxa de entrega (R$)'),
            ('tempo_expiracao_pix', '30', 'numero', 'pagamentos', 'Tempo expiração PIX (min)'),
            ('max_tentativas', '5', 'numero', 'seguranca', 'Máximo de tentativas')
        ]
        for chave, valor, tipo, cat, desc in configs:
            db.execute(
                'INSERT INTO configuracoes (chave, valor, tipo, categoria, descricao) VALUES (?,?,?,?,?)',
                (chave, valor, tipo, cat, desc)
            )
        logger.info('✅ Configurações padrão inseridas')
    
    # Botões do menu principal
    if db.execute('SELECT COUNT(*) FROM botoes_menu').fetchone()[0] == 0:
        botoes = [
            ('principal', '🛍️ Produtos', 'menu_categorias', None, 1, 1),
            ('principal', '🔍 Pesquisar', 'menu_pesquisar', None, 2, 1),
            ('principal', '🛒 Carrinho', 'menu_carrinho', None, 3, 1),
            ('principal', '📦 Pedidos', 'menu_pedidos', None, 4, 1),
            ('principal', '❤️ Favoritos', 'menu_favoritos', None, 5, 1),
            ('principal', '👤 Perfil', 'menu_perfil', None, 6, 1),
            ('principal', '🎟 Cupons', 'menu_cupons', None, 7, 1),
            ('principal', '👥 Afiliados', 'menu_afiliados', None, 8, 1),
            ('principal', '🏆 Ranking', 'menu_ranking', None, 9, 1),
            ('principal', '📞 Suporte', 'menu_suporte', None, 10, 1)
        ]
        for menu, texto, callback, url, ordem, linha in botoes:
            db.execute(
                'INSERT INTO botoes_menu (menu, texto, callback_data, url, ordem, linha) VALUES (?,?,?,?,?,?)',
                (menu, texto, callback, url, ordem, linha)
            )
        logger.info('✅ Botões padrão inseridos')
    
    # Mensagens do bot
    if db.execute('SELECT COUNT(*) FROM mensagens_bot').fetchone()[0] == 0:
        mensagens = [
            ('start', 'Bem-vindo(a) {nome} à {loja}! 🛒\n\nEscolha uma opção:'),
            ('cadastro_nome', '📝 Digite seu nome completo:'),
            ('cadastro_sucesso', '🎉 Cadastro realizado com sucesso!'),
            ('compra_sucesso', '✅ Pedido {numero} confirmado! Total: {total}'),
            ('pix_gerado', '💳 PIX gerado!\n\n📋 `{pix}`\n\n⏰ Expira em {expiracao} min'),
            ('pagamento_aprovado', '✅ Pagamento aprovado! Preparando seu pedido...'),
            ('erro_geral', '❌ Ocorreu um erro. Tente novamente.'),
            ('carrinho_vazio', '🛒 Seu carrinho está vazio!')
        ]
        for chave, conteudo in mensagens:
            db.execute(
                'INSERT INTO mensagens_bot (chave, conteudo) VALUES (?,?)',
                (chave, conteudo)
            )
        logger.info('✅ Mensagens padrão inseridas')
    
    db.commit()
