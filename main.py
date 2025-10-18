import os
from flask import Flask, request, jsonify
import stripe
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

app = Flask(__name__)

# Config Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')  # Coloque no Render: rk_live_51R3SVMP4GG93m2pTFr4WLUG8Gzr6sp6n00zQpmRUo0TQszqoA2mBqlCqsibAcMn8iVLLNRV idqyZXwMcbzWK6jsV00gVF0y9q0

# Seus 5 produtos (exemplo: nome e preço em centavos)
PRODUTOS = {
    'produto1': {'nome': 'Produto 1 - Camiseta', 'preco': 1000},  # R$10
    'produto2': {'nome': 'Produto 2 - Calça', 'preco': 2000},     # R$20
    'produto3': {'nome': 'Produto 3 - Sapato', 'preco': 1500},    # R$15
    'produto4': {'nome': 'Produto 4 - Bolsa', 'preco': 2500},     # R$25
    'produto5': {'nome': 'Produto 5 - Óculos', 'preco': 800},     # R$8
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(PRODUTOS[p]['nome'], callback_data=p)] for p in PRODUTOS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Escolha um produto pra comprar:', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    produto_id = query.data
    produto = PRODUTOS[produto_id]
    
    # Cria Payment Intent no Stripe
    try:
        intent = stripe.PaymentIntent.create(
            amount=produto['preco'],
            currency='brl',
            metadata={'produto': produto['nome']}
        )
        # Link de pagamento (use o client_secret pra checkout no app ou web)
        payment_url = f"https://buy.stripe.com/test_{intent['client_secret']}"  # Link teste; pra prod, use Stripe Checkout
        await query.edit_message_text(
            f"Produto: {produto['nome']}\nPreço: R${produto['preco']/100}\n\nPague aqui: {payment_url}"
        )
    except Exception as e:
        await query.edit_message_text(f"Erro no pagamento: {str(e)}")

# Handlers pro bot (mas como é webhook, rode localmente pra dev)
def main():
    application = Application.builder().token('8038870550:AAGpUN3AjPZuaL29UaSq2HDQnBhWTnN6hmw').build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == '__main__':
    main()

# Webhook endpoint pro Render (POST de updates do Telegram)
@app.route('/', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), app.bot)  # Precisa inicializar bot
    # Aqui você processa o update com os handlers (start, button)
    # Pra simplificar, use a lib python-telegram-bot com webhook mode
    return jsonify({'status': 'ok'})

# Rode o bot em polling se não webhook (pra teste local)
if __name__ == '__main__':
    # Pra Render, use: gunicorn app:app ou algo
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
