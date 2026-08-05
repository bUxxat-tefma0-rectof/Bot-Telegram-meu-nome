import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ForceReply
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from database.connection import get_db
from config.geral import Config
from config.aparencia import AparenciaConfig
from config.telegram import TelegramConfig
from bot.auth import AuthService
from bot.loja import LojaService
from bot.pesquisa import PesquisaService
from bot.carrinho import CarrinhoService
from bot.checkout import CheckoutService
from bot.pedidos import PedidosService
from bot.perfil import PerfilService
from bot.favoritos import FavoritosService
from bot.cupons import CuponsService
from bot.afiliados import AfiliadosService
from bot.ranking import RankingService
from bot.suporte import SuporteService
from bot.menus import MenuService
from bot.botoes import BotoesService
from bot.reply import ReplyService
from utils.helpers import formatar_moeda, gerar_codigo
import logging

logger = logging.getLogger(__name__)

estados = {}
ultima_msg = {}
_bot_instance = None

def get_bot():
    return _bot_instance

class LojaBot:
    def __init__(self):
        global _bot_instance
        self.app = Application.builder().token(Config.BOT_TOKEN_CLIENTE).build()
        _bot_instance = self.app.bot
        self.BASE_URL = Config.RENDER_EXTERNAL_URL or 'https://seu-site.onrender.com'
        self._setup_handlers()
    
    def _setup_handlers(self):
        self.app.add_handler(CommandHandler('start', self.start))
        self.app.add_handler(CommandHandler('menu', self.menu))
        self.app.add_handler(CommandHandler('help', self.help))
        self.app.add_handler(CallbackQueryHandler(self.callback_handler))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.mensagem_handler))
        self.app.add_handler(MessageHandler(filters.VOICE, self.audio_handler))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.foto_handler))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db = get_db()
        cliente = db.execute('SELECT * FROM clientes WHERE telegram_id = ?', (user.id,)).fetchone()
        
        if cliente and cliente.get('nome') and cliente.get('verificado'):
            estados[user.id] = {'tela': 'menu'}
            await self._mostrar_menu_principal(update, user.id, cliente['nome'].split()[0])
        else:
            estados[user.id] = {'tela': 'cadastro', 'aguardando': 'nome'}
            msg = db.execute("SELECT conteudo FROM mensagens_bot WHERE chave='cadastro_nome'").fetchone()
            texto = msg['conteudo'] if msg else '📝 Digite seu nome completo:'
            await update.message.reply_text(
                texto,
                parse_mode='Markdown',
                reply_markup=ForceReply(selective=True)
            )
    
    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db = get_db()
        cliente = db.execute('SELECT nome FROM clientes WHERE telegram_id = ?', (user.id,)).fetchone()
        if cliente:
            await self._mostrar_menu_principal(update, user.id, cliente['nome'].split()[0])
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            '🛒 *Loja Digital*\n\n'
            '📋 Comandos:\n'
            '/start - Iniciar\n'
            '/menu - Menu principal\n'
            '/help - Ajuda\n\n'
            '💡 Você também pode enviar áudio ou foto!',
            parse_mode='Markdown'
        )
    
    async def _mostrar_menu_principal(self, update, user_id, nome):
        db = get_db()
        botoes = db.execute(
            "SELECT * FROM botoes_menu WHERE menu='principal' AND ativo=1 ORDER BY linha, ordem"
        ).fetchall()
        
        kb = []
        linha_atual = 0
        row = []
        
        for btn in botoes:
            if btn['linha'] != linha_atual:
                if row:
                    kb.append(row)
                row = []
                linha_atual = btn['linha']
            
            texto = f"{btn['emoji'] or ''} {btn['texto']}"
            if btn['url']:
                row.append(InlineKeyboardButton(texto, url=btn['url']))
            elif btn['webapp_url']:
                row.append(InlineKeyboardButton(texto, web_app=WebAppInfo(url=btn['webapp_url'])))
            else:
                row.append(InlineKeyboardButton(texto, callback_data=btn['callback_data']))
        
        if row:
            kb.append(row)
        
        # Botão WebApp
        kb.append([InlineKeyboardButton('🛍️ ABRIR LOJA COMPLETA', web_app=WebAppInfo(url=f'{self.BASE_URL}/app'))])
        
        # Mensagem de boas-vindas do banco
        msg = db.execute("SELECT conteudo FROM mensagens_bot WHERE chave='start'").fetchone()
        texto = msg['conteudo'] if msg else 'Bem-vindo(a) {nome} à {loja}!'
        texto = texto.replace('{nome}', nome).replace('{loja}', Config.NOME_LOJA)
        
        if hasattr(update, 'message') and update.message:
            await update.message.reply_text(texto, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
        else:
            await update.callback_query.message.edit_text(texto, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        data = query.data
        msg_id = query.message.message_id
        ultima_msg[user_id] = msg_id
        
        db = get_db()
        cliente = db.execute('SELECT * FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
        if not cliente:
            await query.message.reply_text('❌ Faça o cadastro primeiro com /start')
            return
        
        # Roteamento
        if data == 'menu_principal':
            await self._mostrar_menu_principal(update, user_id, cliente['nome'].split()[0] if cliente['nome'] else 'Cliente')
        
        elif data == 'menu_categorias':
            cats = LojaService.get_categorias()
            kb = [[InlineKeyboardButton(f'{c["emoji"]} {c["nome"]}', callback_data=f'cat_{c["id"]}')] for c in cats]
            kb.append([InlineKeyboardButton('🔍 Pesquisar', callback_data='menu_pesquisar')])
            kb.append([InlineKeyboardButton('⬅️ Voltar', callback_data='menu_principal')])
            await self._editar_msg(query.message, '📂 *CATEGORIAS*\n\nEscolha uma categoria:', kb)
        
        elif data == 'menu_pesquisar':
            estados[user_id] = {'tela': 'pesquisa', 'aguardando': 'termo'}
            await self._editar_msg(query.message, '🔍 Digite o nome do produto que deseja buscar:', 
                                   [[InlineKeyboardButton('⬅️ Voltar', callback_data='menu_principal')]])
        
        elif data == 'menu_carrinho':
            await self._mostrar_carrinho(query, user_id)
        
        elif data == 'menu_pedidos':
            await self._mostrar_pedidos(query, user_id)
        
        elif data == 'menu_perfil':
            await self._mostrar_perfil(query, user_id)
        
        elif data == 'menu_favoritos':
            await self._mostrar_favoritos(query, user_id)
        
        elif data == 'menu_cupons':
            cupons = CuponsService.listar_disponiveis()
            if not cupons:
                await self._editar_msg(query.message, '🎟 Nenhum cupom disponível no momento.', 
                                       [[InlineKeyboardButton('⬅️ Voltar', callback_data='menu_principal')]])
            else:
                kb = [[InlineKeyboardButton(f'{c["codigo"]} - {c["valor"]}{"%" if c["tipo"]=="percentual" else "R$"}', 
                        callback_data=f'cupom_{c["codigo"]}')] for c in cupons[:10]]
                kb.append([InlineKeyboardButton('⬅️ Voltar', callback_data='menu_principal')])
                await self._editar_msg(query.message, '🎟 *CUPONS DISPONÍVEIS*', kb)
        
        elif data == 'menu_afiliados':
            await self._mostrar_afiliados(query, user_id)
        
        elif data == 'menu_ranking':
            rank = RankingService.get_ranking()
            msg = '🏆 *RANKING DE CLIENTES*\n\n'
            for i, r in enumerate(rank[:10]):
                medalha = ['🥇','🥈','🥉'][i] if i < 3 else f'{i+1}º'
                msg += f'{medalha} {r["nome"]} - {formatar_moeda(r["total_gasto"])}\n'
            await self._editar_msg(query.message, msg, [[InlineKeyboardButton('⬅️ Voltar', callback_data='menu_principal')]])
        
        elif data == 'menu_suporte':
            await self._mostrar_suporte(query)
        
        # Categorias e Produtos
        elif data.startswith('cat_'):
            cat_id = data.split('_')[1]
            prods = LojaService.get_produtos_por_categoria(cat_id)
            cat = LojaService.get_categoria(cat_id)
            kb = [[InlineKeyboardButton(
                f'{p["nome"]} - {formatar_moeda(p["preco_promocional"] or p["preco"])}',
                callback_data=f'prod_{p["id"]}'
            )] for p in prods[:12]]
            kb.append([InlineKeyboardButton('⬅️ Voltar', callback_data='menu_categorias')])
            await self._editar_msg(query.message, f'{cat["emoji"]} *{cat["nome"]}*\n\n{len(prods)} produtos:', kb)
        
        elif data.startswith('prod_'):
            prod_id = data.split('_')[1]
            p = LojaService.get_produto(prod_id)
            if p:
                await self._mostrar_produto(query, user_id, p)
        
        elif data.startswith('addcarr_'):
            prod_id = data.split('_')[1]
            await CarrinhoService.adicionar(user_id, prod_id)
            await query.answer('✅ Adicionado ao carrinho!', show_alert=True)
        
        elif data.startswith('addcarr_qtd_'):
            _, _, prod_id, qtd = data.split('_')
            await CarrinhoService.adicionar(user_id, prod_id, int(qtd))
            await query.answer(f'✅ {qtd}x adicionado!', show_alert=True)
        
        elif data.startswith('fav_'):
            prod_id = data.split('_')[1]
            FavoritosService.toggle(user_id, prod_id)
            is_fav = FavoritosService.is_favorito(user_id, prod_id)
            await query.answer('❤️ Favoritado!' if is_fav else '❌ Removido')
        
        elif data.startswith('carr_del_'):
            await CarrinhoService.remover(user_id, data.split('_')[2])
            await self._mostrar_carrinho(query, user_id)
        
        elif data.startswith('carr_qtd_'):
            _, _, carrinho_id, qtd = data.split('_')
            await CarrinhoService.atualizar_quantidade(user_id, carrinho_id, int(qtd))
            await self._mostrar_carrinho(query, user_id)
        
        elif data == 'checkout_pix':
            await self._checkout(query, user_id, 'pix')
        
        elif data == 'checkout_dinheiro':
            await self._checkout(query, user_id, 'dinheiro')
        
        elif data.startswith('cupom_'):
            codigo = data.split('_')[1]
            r = CuponsService.aplicar(user_id, codigo)
            await query.answer(r['mensagem'], show_alert=True)
        
        elif data == 'recarregar':
            estados[user_id] = {'tela': 'recarga', 'aguardando': 'valor'}
            await self._editar_msg(query.message, '💰 Digite o valor da recarga (mínimo R$ 10,00):',
                                   [[InlineKeyboardButton('⬅️ Voltar', callback_data='menu_perfil')]])
    
    async def mensagem_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        texto = update.message.text.strip() if update.message.text else None
        estado = estados.get(user_id)
        
        if not estado or not estado.get('aguardando') or not texto:
            return
        
        db = get_db()
        
        # Cadastro - Nome
        if estado['aguardando'] == 'nome':
            if len(texto) < 3 or len(texto.split()) < 2:
                await update.message.reply_text('❌ Digite *nome e sobrenome*.', parse_mode='Markdown')
                return
            partes = texto.split()
            nome, sobrenome = partes[0], ' '.join(partes[1:])
            
            existe = db.execute('SELECT * FROM clientes WHERE telegram_id = ?', (user_id,)).fetchone()
            if existe:
                db.execute('UPDATE clientes SET nome=?, sobrenome=? WHERE telegram_id=?', (nome, sobrenome, user_id))
            else:
                db.execute('INSERT INTO clientes (telegram_id, nome, sobrenome) VALUES (?,?,?)', (user_id, nome, sobrenome))
            db.commit()
            
            codigo = AuthService.gerar_codigo(user_id)
            estado['aguardando'] = 'codigo'
            await update.message.reply_text(
                f'✅ Nome: *{nome} {sobrenome}*\n\n🔐 Código: `{codigo}`\n\n_Digite o código de 6 dígitos:_',
                parse_mode='Markdown'
            )
        
        # Cadastro - Código
        elif estado['aguardando'] == 'codigo':
            if AuthService.verificar_codigo(user_id, texto):
                estados[user_id] = {'tela': 'menu'}
                c = db.execute('SELECT nome FROM clientes WHERE telegram_id=?', (user_id,)).fetchone()
                await update.message.reply_text(f'🎉 *Cadastro concluído!*\n\nBem-vindo(a), *{c["nome"].split()[0]}*!', parse_mode='Markdown')
                await self._mostrar_menu_principal(update, user_id, c['nome'].split()[0])
            else:
                await update.message.reply_text('❌ Código incorreto. Tente novamente.')
        
        # Pesquisa
        elif estado['aguardando'] == 'termo':
            estado['aguardando'] = None
            prods = PesquisaService.pesquisar(texto)
            if not prods:
                await update.message.reply_text(f'🔍 Nenhum resultado para "{texto}".')
                return
            kb = [[InlineKeyboardButton(
                f'{p["nome"]} - {formatar_moeda(p["preco_promocional"] or p["preco"])}',
                callback_data=f'prod_{p["id"]}'
            )] for p in prods[:12]]
            kb.append([InlineKeyboardButton('⬅️ Voltar', callback_data='menu_principal')])
            await update.message.reply_text(f'🔍 *{len(prods)} resultados para "{texto}"*', 
                                           parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
        
        # Recarga
        elif estado['aguardando'] == 'valor':
            try:
                valor = float(texto.replace(',', '.'))
                if valor < 10:
                    await update.message.reply_text('❌ Valor mínimo: R$ 10,00')
                    return
                from services.pagamento import PagamentoService
                pg = PagamentoService()
                result = pg.processar_recarga(db.execute('SELECT id FROM clientes WHERE telegram_id=?', (user_id,)).fetchone()['id'], valor)
                if result['sucesso']:
                    await update.message.reply_photo(result['qr_buffer'], 
                        caption=f'💳 *PIX para recarga*\n\n💰 Valor: {formatar_moeda(valor)}\n\n📋 `{result["copia_cola"]}`\n\n⏰ Expira em 30 min',
                        parse_mode='Markdown')
                else:
                    await update.message.reply_text('❌ Erro ao gerar PIX.')
            except:
                await update.message.reply_text('❌ Valor inválido.')
            estado['aguardando'] = None
    
    async def audio_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        estado = estados.get(user_id)
        if not estado or not estado.get('aguardando'):
            return
        
        await update.message.reply_text('🎙️ *Processando áudio...*', parse_mode='Markdown')
        
        try:
            file = await update.message.voice.get_file()
            from services.reconhecimento import ReconhecimentoService
            result = await ReconhecimentoService.transcrever_audio(file.file_path)
            
            if result.get('sucesso'):
                texto = result['texto']
                await update.message.reply_text(f'🎙️ *Você disse:* _{texto}_', parse_mode='Markdown')
                update.message.text = texto
                await self.mensagem_handler(update, context)
            else:
                await update.message.reply_text('❌ Não foi possível transcrever o áudio.')
        except Exception as e:
            logger.error(f'Erro áudio: {e}')
            await update.message.reply_text('❌ Erro ao processar áudio.')
    
    async def foto_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('📸 Foto recebida! Em breve teremos processamento de imagens.')
    
    # ============ MÉTODOS AUXILIARES ============
    
    async def _mostrar_produto(self, query, user_id, p):
        preco = p['preco_promocional'] or p['preco']
        msg = f'📦 *{p["nome"]}*\n\n'
        if p.get('marca'): msg += f'🏷 Marca: {p["marca"]}\n'
        if p.get('descricao'): msg += f'📝 {p["descricao"]}\n'
        if p.get('peso'): msg += f'⚖️ {p["peso"]}\n'
        msg += f'\n💰 *Preço: {formatar_moeda(preco)}*'
        if p['preco_promocional']:
            msg += f'\n🔥 De: ~~{formatar_moeda(p["preco"])}~~ ({(1-p["preco_promocional"]/p["preco"])*100:.0f}% OFF)'
        msg += f'\n📦 Estoque: {p["estoque"]} {p.get("unidade", "un")}'
        
        kb = [
            [InlineKeyboardButton('🛒 COMPRAR', callback_data=f'addcarr_{p["id"]}'),
             InlineKeyboardButton('❤️ Favoritar', callback_data=f'fav_{p["id"]}')],
            [InlineKeyboardButton('⬅️ Voltar', callback_data=f'cat_{p["categoria_id"]}')]
        ]
        
        if p.get('foto'):
            try:
                await query.message.reply_photo(p['foto'], caption=msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
            except:
                await self._editar_msg(query.message, msg, kb)
        else:
            await self._editar_msg(query.message, msg, kb)
    
    async def _mostrar_carrinho(self, query, user_id):
        c = CarrinhoService.listar(user_id)
        if not c['itens']:
            await self._editar_msg(query.message, '🛒 *Carrinho Vazio*', 
                                   [[InlineKeyboardButton('🛍️ Ver Produtos', callback_data='menu_categorias')],
                                    [InlineKeyboardButton('⬅️ Voltar', callback_data='menu_principal')]])
            return
        
        msg = '🛒 *SEU CARRINHO*\n\n'
        kb = []
        for i in c['itens']:
            preco = i.get('preco_promocional') or i.get('preco', 0)
            msg += f'📦 {i["nome"]}\n   {i["quantidade"]}x {formatar_moeda(preco)} = {formatar_moeda(preco * i["quantidade"])}\n\n'
            kb.append([
                InlineKeyboardButton('➖', callback_data=f'carr_qtd_{i["id"]}_{i["quantidade"]-1}'),
                InlineKeyboardButton(f'{i["quantidade"]}', callback_data='noop'),
                InlineKeyboardButton('➕', callback_data=f'carr_qtd_{i["id"]}_{i["quantidade"]+1}'),
                InlineKeyboardButton('🗑', callback_data=f'carr_del_{i["id"]}')
            ])
        
        total = c['total']
        taxa = float(Config.TAXA_ENTREGA or 5)
        msg += f'📦 Subtotal: {formatar_moeda(total)}\n'
        msg += f'🚚 Entrega: {formatar_moeda(taxa)}\n'
        msg += f'💰 *Total: {formatar_moeda(total + taxa)}*'
        
        kb.append([InlineKeyboardButton('💳 PAGAR COM PIX', callback_data='checkout_pix')])
        kb.append([InlineKeyboardButton('💵 DINHEIRO NA ENTREGA', callback_data='checkout_dinheiro')])
        kb.append([InlineKeyboardButton('⬅️ Voltar', callback_data='menu_principal')])
        
        await self._editar_msg(query.message, msg, kb)
    
    async def _checkout(self, query, user_id, metodo):
        await query.message.reply_text('⏳ Processando seu pedido...')
        r = CheckoutService.finalizar(user_id, metodo)
        
        if r['sucesso']:
            if r.get('qr_buffer'):
                await query.message.reply_photo(
                    r['qr_buffer'],
                    caption=f'💳 *PIX GERADO*\n\n📦 Pedido: {r["numero"]}\n💰 Valor: {formatar_moeda(r["total"])}\n\n📋 *PIX Copia e Cola:*\n`{r.get("copia_cola", "")}`\n\n⏰ Expira em {Config.TEMPO_EXPIRACAO_PIX} minutos\n\n_Assim que o pagamento for confirmado, seu pedido será processado._',
                    parse_mode='Markdown'
                )
            else:
                await query.message.reply_text(
                    f'✅ *Pedido {r["numero"]} realizado!*\n\n💰 Total: {formatar_moeda(r["total"])}\n💳 Pagamento: {metodo.upper()}\n\nObrigado por comprar conosco! 🛒',
                    parse_mode='Markdown'
                )
        else:
            await query.message.reply_text(f'❌ {r["mensagem"]}')
    
    async def _mostrar_pedidos(self, query, user_id):
        peds = PedidosService.listar(user_id)
        if not peds:
            await self._editar_msg(query.message, '📦 *Nenhum pedido encontrado*', 
                                   [[InlineKeyboardButton('🛍️ Fazer Compras', callback_data='menu_categorias')],
                                    [InlineKeyboardButton('⬅️ Voltar', callback_data='menu_principal')]])
            return
        
        msg = '📦 *SEUS PEDIDOS*\n\n'
        status_emoji = {'recebido':'📥','confirmado':'✅','separando':'📦','entregue':'🏠','cancelado':'❌'}
        for p in peds[:15]:
            emoji = status_emoji.get(p['status'], '📋')
            msg += f'{emoji} {p["numero"]} - {formatar_moeda(p["total"])} - {p["status"].upper()}\n'
        
        await self._editar_msg(query.message, msg, 
                               [[InlineKeyboardButton('⬅️ Voltar', callback_data='menu_principal')]])
    
    async def _mostrar_perfil(self, query, user_id):
        p = PerfilService.get_perfil(user_id)
        if not p:
            await self._editar_msg(query.message, '❌ Perfil não encontrado', 
                                   [[InlineKeyboardButton('⬅️ Voltar', callback_data='menu_principal')]])
            return
        
        msg = f'👤 *MEU PERFIL*\n\n'
        msg += f'📝 Nome: {p.get("nome", "N/A")} {p.get("sobrenome", "")}\n'
        msg += f'📧 Email: {p.get("email", "N/A")}\n'
        msg += f'📱 Telefone: {p.get("telefone", "N/A")}\n'
        msg += f'🆔 ID: `{user_id}`\n\n'
        msg += f'💰 Saldo: {formatar_moeda(p.get("saldo", 0))}\n'
        msg += f'💵 Total Gasto: {formatar_moeda(p.get("total_gasto", 0))}\n'
        msg += f'⭐ Pontos: {p.get("pontos_fidelidade", 0)}\n'
        msg += f'💎 Cashback: {formatar_moeda(p.get("cashback", 0))}'
        
        kb = [
            [InlineKeyboardButton('💰 Recarregar Saldo', callback_data='recarregar'),
             InlineKeyboardButton('📦 Meus Pedidos', callback_data='menu_pedidos')],
            [InlineKeyboardButton('❤️ Favoritos', callback_data='menu_favoritos'),
             InlineKeyboardButton('👥 Afiliados', callback_data='menu_afiliados')],
            [InlineKeyboardButton('⬅️ Voltar', callback_data='menu_principal')]
        ]
        await self._editar_msg(query.message, msg, kb)
    
    async def _mostrar_favoritos(self, query, user_id):
        favs = FavoritosService.listar(user_id)
        if not favs:
            await self._editar_msg(query.message, '❤️ *Nenhum favorito ainda*', 
                                   [[InlineKeyboardButton('🛍️ Ver Produtos', callback_data='menu_categorias')],
                                    [InlineKeyboardButton('⬅️ Voltar', callback_data='menu_principal')]])
            return
        
        kb = [[InlineKeyboardButton(
            f'{f["nome"]} - {formatar_moeda(f.get("preco_promocional") or f.get("preco", 0))}',
            callback_data=f'prod_{f["produto_id"]}'
        )] for f in favs]
        kb.append([InlineKeyboardButton('⬅️ Voltar', callback_data='menu_principal')])
        await self._editar_msg(query.message, '❤️ *FAVORITOS*', kb)
    
    async def _mostrar_afiliados(self, query, user_id):
        a = AfiliadosService.get_afiliado(user_id)
        if not a:
            # Criar afiliado
            AfiliadosService.criar_afiliado(user_id)
            a = AfiliadosService.get_afiliado(user_id)
        
        msg = f'👥 *PROGRAMA DE AFILIADOS*\n\n'
        msg += f'🔗 Seu código: `{a["codigo"]}`\n'
        msg += f'💰 Comissão: {a["comissao_percentual"]}%\n'
        msg += f'👥 Indicações: {a["total_indicacoes"]}\n'
        msg += f'💵 Saldo: {formatar_moeda(a["saldo_comissao"])}\n\n'
        msg += f'📋 *Link de indicação:*\nhttps://t.me/{(await self.app.bot.get_me()).username}?start={a["codigo"]}'
        
        await self._editar_msg(query.message, msg, 
                               [[InlineKeyboardButton('💰 Solicitar Saque', callback_data='afiliado_saque')],
                                [InlineKeyboardButton('⬅️ Voltar', callback_data='menu_principal')]])
    
    async def _mostrar_suporte(self, query):
        msg = '📞 *SUPORTE*\n\nEntre em contato conosco:\n📱 Telegram: @suporte\n📧 Email: suporte@loja.com\n\n⏰ Horário: Seg-Sex 9h às 18h'
        await self._editar_msg(query.message, msg, 
                               [[InlineKeyboardButton('⬅️ Voltar', callback_data='menu_principal')]])
    
    async def _editar_msg(self, message, text, kb):
        try:
            await message.edit_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
        except:
            await message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    
    def run(self):
        logger.info('🤖 Bot Cliente iniciando...')
        self.app.run_polling()

def start_bot_cliente():
    bot = LojaBot()
    bot.run()
