const { getDB } = require('../database');

// /gpstts - Adiciona status ao grupo
async function gpStatus(bot, msg) {
    if (!await isAdmin(msg)) return;
    if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda uma mensagem para adicionar como status!');
    
    const db = getDB();
    db.prepare('INSERT OR REPLACE INTO grupos (chat_id, status_msg) VALUES (?,?)').run(String(msg.chat.id), msg.reply_to_message.text || '🖼️ Mídia');
    
    // Fixa a mensagem
    try {
        await bot.pinChatMessage(msg.chat.id, msg.reply_to_message.message_id);
        bot.sendMessage(msg.chat.id, '✨ *Status do grupo atualizado!*', { parse_mode: 'Markdown' });
    } catch (e) {
        bot.sendMessage(msg.chat.id, '✨ *Status salvo! (Não foi possível fixar)*', { parse_mode: 'Markdown' });
    }
}

async function isAdmin(msg) {
    try {
        const admins = process.env.ADMIN_IDS.split(',').map(Number);
        return admins.includes(msg.from.id);
    } catch (e) { return false; }
}

module.exports = { gpStatus };
