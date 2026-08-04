const { getDB } = require('../database');

// /auto a <hora> ou /auto f <hora>
async function autoFechar(bot, msg, match) {
    if (!await isAdmin(msg)) return;
    const acao = match[1]; // a = abrir, f = fechar
    const hora = match[2];
    
    const [h, m] = hora.split(':').map(Number);
    const agora = new Date();
    const alvo = new Date(agora);
    alvo.setHours(h, m || 0, 0, 0);
    
    if (alvo < agora) alvo.setDate(alvo.getDate() + 1);
    const timeout = alvo - agora;
    
    setTimeout(async () => {
        if (acao === 'f') {
            await bot.setChatPermissions(msg.chat.id, { can_send_messages: false });
            bot.sendMessage(msg.chat.id, '🔒 *Grupo fechado automaticamente!*', { parse_mode: 'Markdown' });
        } else {
            await bot.setChatPermissions(msg.chat.id, { can_send_messages: true, can_send_media_messages: true });
            bot.sendMessage(msg.chat.id, '🔓 *Grupo aberto automaticamente!*', { parse_mode: 'Markdown' });
        }
    }, timeout);
    
    bot.sendMessage(msg.chat.id, `⏰ *Auto ${acao === 'f' ? 'fechar' : 'abrir'} configurado para ${hora}!*`, { parse_mode: 'Markdown' });
}

// /dm - apaga mensagem respondida e manda no privado
async function dmUser(bot, msg) {
    if (!await isAdmin(msg)) return;
    if (!msg.reply_to_message) return;
    try {
        await bot.sendMessage(msg.reply_to_message.from.id, `📩 Mensagem do grupo ${msg.chat.title}:\n\n${msg.reply_to_message.text || 'Mídia'}`);
        await bot.deleteMessage(msg.chat.id, msg.reply_to_message.message_id);
        await bot.deleteMessage(msg.chat.id, msg.message_id);
    } catch (e) {
        bot.sendMessage(msg.chat.id, '❌ Não foi possível enviar DM.');
    }
}

// /msg - Lê JSON da mensagem
async function lerMsgJson(bot, msg) {
    if (!msg.reply_to_message) return;
    bot.sendMessage(msg.chat.id, `📊 \`${JSON.stringify(msg.reply_to_message, null, 2).substring(0, 3000)}\``, { parse_mode: 'Markdown' });
}

async function isAdmin(msg) {
    try {
        const admins = process.env.ADMIN_IDS.split(',').map(Number);
        return admins.includes(msg.from.id);
    } catch (e) { return false; }
}

module.exports = { autoFechar, dmUser, lerMsgJson };
