from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from database.connection import get_db
from config.geral import Config
from admin.dashboard import DashboardAdmin
from admin.produtos import ProdutosAdmin
from admin.pedidos import PedidosAdmin
from admin.clientes import ClientesAdmin
from utils.helpers import formatar_moeda
import logging

logger = logging.getLogger(__name__)

estados_admin = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in Config.ADMIN_IDS:
        await update.message.reply_text('⛔ Acesso negado.')
        return
    
    await show_dashboard(update)

async def show_dashboard(update):
    stats = DashboardAdmin.get_estatisticas()
    
    msg = f'📊 *PAINEL ADMINISTRATIVO*\n\n'
    msg += f'👥 Clientes: *{stats["clientes"]["total"]}*\n'
    msg += f'📦 Pedidos Hoje: *{stats["pedidos"]["hoje"]}*\n'
    msg += f'⚠️ Pendentes: *{stats["pedidos"]["pendentes"]}*\n'
    msg += f'💰 Faturamento Mês: *{formatar_moeda(stats["faturamento"]["mes"])}*\n'
    msg += f'📦 Produtos: *{stats["produtos"]["ativos"]}*\n\n'
    msg += f'Selecione uma opção:'
    
    kb = [
        [InlineKeyboardButton('📦 Produtos', callback_data='adm_produtos'),
         InlineKeyboardButton('📂 Categorias', callback_data='adm_categorias')],
        [InlineKeyboardButton('📋 Pedidos', callback_data='adm_pedidos'),
         InlineKeyboardButton('👥 Clientes', callback_data='adm_clientes')],
        [InlineKeyboardButton('💰 Financeiro', callback_data='adm_financeiro'),
         InlineKeyboardButton('🎟 Cupons', callback_data='adm_cupons')],
        [InlineKeyboardButton('👥 Afiliados', callback_data='adm_afiliados'),
         InlineKeyboardButton('💬 Mensagens', callback_data='adm_mensagens')],
        [InlineKeyboardButton('🔘 Botões', callback_data='adm_botoes'),
         InlineKeyboardButton('⚙️ Config', callback_data='adm_config')],
        [InlineKeyboardButton('📊 Relatórios', callback_data='adm_relatorios'),
         InlineKeyboardButton('💾 Backup', callback_data='adm_backup')],
        [InlineKeyboardButton('📢 Broadcast', callback_data='adm_broadcast')]
    ]
    
    if hasattr(update, 'message') and update.message:
        await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update.callback_query.message.edit_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    
    if user_id not in Config.ADMIN_IDS:
        return
    
    if data == 'adm_voltar':
        await show_dashboard(update)
        return
    
    if data == 'adm_broadcast':
        estados_admin[user_id] = {'aguardando': 'broadcast'}
        await query.message.edit_text('📢 Digite a mensagem para enviar a TODOS os clientes:')
        return
    
    # Produtos
    if data == 'adm_produtos':
        result = ProdutosAdmin.listar()
        prods = result['produtos'][:15]
        kb = [[InlineKeyboardButton(f'{"✅" if p["disponivel"] else "❌"} {p["nome"]} - {formatar_moeda(p["preco"])}', 
                callback_data=f'adm_prod_{p["id"]}')] for p in prods]
        kb.append([InlineKeyboardButton('➕ Novo Produto', callback_data='adm_prod_novo')])
        kb.append([InlineKeyboardButton('⬅️ Voltar', callback_data='adm_voltar')])
        await query.message.edit_text(f'📦 *PRODUTOS* ({result["total"]})', 
                                      parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    
    # Pedidos
    elif data == 'adm_pedidos':
        result = PedidosAdmin.listar(filtro='pendentes')
        peds = result['pedidos'][:15]
        kb = [[InlineKeyboardButton(f'{p["numero"]} - {p["cliente_nome"]} - {formatar_moeda(p["total"])}', 
                callback_data=f'adm_ped_{p["id"]}')] for p in peds]
        kb.append([InlineKeyboardButton('⬅️ Voltar', callback_data='adm_voltar')])
        await query.message.edit_text(f'📋 *PEDIDOS PENDENTES* ({result["total"]})',
                                      parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    
    # Clientes
    elif data == 'adm_clientes':
        result = ClientesAdmin.listar()
        clis = result['clientes'][:15]
        kb = [[InlineKeyboardButton(f'{c.get("nome", "Sem nome")} - {formatar_moeda(c.get("total_gasto", 0))}', 
                callback_data=f'adm_cli_{c["id"]}')] for c in clis]
        kb.append([InlineKeyboardButton('⬅️ Voltar', callback_data='adm_voltar')])
        await query.message.edit_text(f'👥 *CLIENTES* ({result["total"]})',
                                      parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    
    # Voltar
    elif data == 'adm_voltar':
        await show_dashboard(update)

async def mensagem_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    estado = estados_admin.get(user_id)
    
    if not estado or not estado.get('aguardando'):
        return
    
    if estado['aguardando'] == 'broadcast':
        texto = update.message.text
        db = get_db()
        clientes = db.execute('SELECT telegram_id FROM clientes WHERE bloqueado = 0').fetchall()
        
        enviados = 0
        for c in clientes:
            try:
                await context.bot.send_message(c['telegram_id'], 
                    f'📢 *{Config.NOME_LOJA}*\n\n{texto}', parse_mode='Markdown')
                enviados += 1
            except:
                pass
        
        estados_admin.pop(user_id, None)
        await update.message.reply_text(f'✅ Mensagem enviada para {enviados} clientes!')

def start_bot_admin():
    app = Application.builder().token(Config.BOT_TOKEN_ADMIN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensagem_handler))
    
    logger.info('👑 Bot Admin iniciando...')
    app.run_polling()
