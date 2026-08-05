from .connection import get_db
import logging

logger = logging.getLogger(__name__)

def inserir_dados_padrao():
    db = get_db()
    
    # Categorias padrão
    if db.execute('SELECT COUNT(*) FROM categorias').fetchone()[0] == 0:
        categorias = [
            ('Alimentos', '🍎', 'Produtos alimentícios em geral', '#ef4444'),
            ('Bebidas', '🥤', 'Bebidas e refrigerantes', '#3b82f6'),
            ('Limpeza', '🧹', 'Produtos de limpeza doméstica', '#10b981'),
            ('Higiene', '🧼', 'Produtos de higiene pessoal', '#8b5cf6'),
            ('Açougue', '🥩', 'Carnes e derivados', '#f59e0b'),
            ('Hortifruti', '🥬', 'Frutas, verduras e legumes', '#84cc16'),
            ('Padaria', '🍞', 'Pães, bolos e doces', '#f97316'),
            ('Laticínios', '🧀', 'Leite, queijos e derivados', '#06b6d4'),
            ('Congelados', '❄️', 'Alimentos congelados', '#64748b'),
            ('Pet Shop', '🐾', 'Produtos para animais', '#ec4899')
        ]
        for nome, emoji, desc, cor in categorias:
            db.execute(
                'INSERT INTO categorias (nome, emoji, descricao, cor) VALUES (?,?,?,?)',
                (nome, emoji, desc, cor)
            )
        logger.info('✅ 10 categorias padrão inseridas')
    
    # Configurações padrão
    if db.execute('SELECT COUNT(*) FROM configuracoes').fetchone()[0] == 0:
        configs = [
            ('nome_loja', 'Loja Digital', 'texto', 'geral', 'Nome da loja'),
            ('msg_start', 'Bem-vindo(a) {nome} à {loja}! 🛒\n\nEscolha uma opção:', 'texto', 'mensagens', 'Mensagem inicial'),
            ('msg_compra', '✅ Pedido {numero} confirmado!\n\n💰 Total: {total}\n📦 Status: {status}', 'texto', 'mensagens', 'Mensagem de compra'),
            ('msg_pix', '💳 PIX gerado!\n\n📋 `{pix}`\n\n⏰ Expira em {expiracao} min', 'texto', 'mensagens', 'Mensagem PIX'),
            ('cor_primaria', '#6366f1', 'cor', 'aparencia', 'Cor principal'),
            ('cor_secundaria', '#ec4899', 'cor', 'aparencia', 'Cor secundária'),
            ('cor_fundo', '#f8fafc', 'cor', 'aparencia', 'Cor de fundo'),
            ('tema', 'light', 'tema', 'aparencia', 'Tema (light/dark)'),
            ('comissao_padrao', '5', 'numero', 'afiliados', 'Comissão padrão (%)'),
            ('pedido_minimo', '10', 'numero', 'geral', 'Pedido mínimo (R$)'),
            ('taxa_entrega', '5', 'numero', 'geral', 'Taxa de entrega (R$)'),
            ('tempo_expiracao_pix', '30', 'numero', 'pagamentos', 'Expiração PIX (min)'),
            ('max_tentativas', '5', 'numero', 'seguranca', 'Máx. tentativas login'),
            ('gateway_ativo', 'mercadopago', 'texto', 'pagamentos', 'Gateway ativo'),
            ('aprovacao_automatica', '1', 'texto', 'pagamentos', 'Aprovação automática'),
        ]
        for chave, valor, tipo, cat, desc in configs:
            db.execute(
                'INSERT INTO configuracoes (chave, valor, tipo, categoria, descricao) VALUES (?,?,?,?,?)',
                (chave, valor, tipo, cat, desc)
            )
        logger.info('✅ 15 configurações padrão inseridas')
    
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
            ('principal', '📞 Suporte', 'menu_suporte', None, 10, 1),
        ]
        for menu, texto, callback, url, ordem, linha in botoes:
            db.execute(
                'INSERT INTO botoes_menu (menu, texto, callback_data, url, ordem, linha) VALUES (?,?,?,?,?,?)',
                (menu, texto, callback, url, ordem, linha)
            )
        logger.info('✅ 10 botões padrão inseridos')
    
    # Mensagens do bot
    if db.execute('SELECT COUNT(*) FROM mensagens_bot').fetchone()[0] == 0:
        mensagens = [
            ('start', 'Bem-vindo(a) {nome} à {loja}! 🛒\n\nEscolha uma opção:'),
            ('cadastro_nome', '📝 Digite seu nome completo:'),
            ('cadastro_sucesso', '🎉 Cadastro realizado com sucesso! Bem-vindo(a) {nome}!'),
            ('compra_sucesso', '✅ Pedido {numero} confirmado!\n\n💰 Total: {total}\n📦 Status: {status}'),
            ('pix_gerado', '💳 PIX gerado!\n\n📋 `{pix}`\n\n⏰ Expira em {expiracao} minutos'),
            ('pagamento_aprovado', '✅ Pagamento aprovado! Seu pedido está sendo preparado.'),
            ('erro_geral', '❌ Ocorreu um erro. Tente novamente mais tarde.'),
            ('carrinho_vazio', '🛒 Seu carrinho está vazio! Que tal adicionar alguns produtos?'),
        ]
        for chave, conteudo in mensagens:
            db.execute(
                'INSERT INTO mensagens_bot (chave, conteudo) VALUES (?,?)',
                (chave, conteudo)
            )
        logger.info('✅ 8 mensagens padrão inseridas')
    
    db.commit()
    logger.info('✅ Dados padrão inseridos com sucesso')
