const { getDB } = require('../database');

// /checkativo @user
async function checkAtivo(bot, msg) {
    if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda a mensagem!');
    const db = getDB();
    const user = db.prepare('SELECT quantidade FROM mensagens_contador WHERE chat_id=? AND user_id=?').get(String(msg.chat.id), String(msg.reply_to_message.from.id));
    bot.sendMessage(msg.chat.id, `🔎 *${msg.reply_to_message.from.first_name}*\n💬 Mensagens: ${user?.quantidade || 0}`, { parse_mode: 'Markdown' });
}

// /inativos <qtd>
async function inativos(bot, msg, match) {
    if (!await isAdmin(msg)) return;
    const qtd = parseInt(match[1]);
    const db = getDB();
    const users = db.prepare('SELECT user_id, quantidade FROM mensagens_contador WHERE chat_id=? AND quantidade < ?').all(String(msg.chat.id), qtd);
    
    let texto = `💤 *INATIVOS (menos de ${qtd} msgs)*\n\n`;
    users.forEach(u => texto += `👻 ${u.user_id}: ${u.quantidade} msgs\n`);
    
    bot.sendMessage(msg.chat.id, texto || 'Nenhum inativo.', { parse_mode: 'Markdown' });
}

// /banghost <qtd>
async function banHost(bot, msg, match) {
    if (!await isAdmin(msg)) return;
    const qtd = parseInt(match[1]);
    const db = getDB();
    const users = db.prepare('SELECT user_id, quantidade FROM mensagens_contador WHERE chat_id=? AND quantidade < ?').all(String(msg.chat.id), qtd);
    
    let bans = 0;
    for (const u of users) {
        try {
            await bot.banChatMember(msg.chat.id, parseInt(u.user_id));
            await bot.unbanChatMember(msg.chat.id, parseInt(u.user_id));
            bans++;
        } catch (e) {}
    }
    
    bot.sendMessage(msg.chat.id, `💥 *${bans} inativos foram removidos!*`, { parse_mode: 'Markdown' });
}

async function isAdmin(msg) {
    try {
        const admins = process.env.ADMIN_IDS.split(',').map(Number);
        return admins.includes(msg.from.id);
    } catch (e) { return false; }
}

module.exports = { checkAtivo, inativos, banHost };
