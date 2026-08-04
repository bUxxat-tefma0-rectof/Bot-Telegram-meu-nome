const { getDB } = require('../database');

// /donoadm
async function donoAdm(bot, msg) {
    if (!await isOwner(msg)) return bot.sendMessage(msg.chat.id, '❌ Apenas o dono pode usar!');
    if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda a mensagem!');
    const db = getDB();
    db.prepare('INSERT OR REPLACE INTO admins_dono (chat_id, user_id) VALUES (?,?)').run(String(msg.chat.id), String(msg.reply_to_message.from.id));
    bot.sendMessage(msg.chat.id, '👑 *Dono admin adicionado!*', { parse_mode: 'Markdown' });
}

// /remdono
async function remDono(bot, msg) {
    if (!await isOwner(msg)) return;
    if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda a mensagem!');
    const db = getDB();
    db.prepare('DELETE FROM admins_dono WHERE chat_id=? AND user_id=?').run(String(msg.chat.id), String(msg.reply_to_message.from.id));
    bot.sendMessage(msg.chat.id, '👑 *Dono admin removido!*', { parse_mode: 'Markdown' });
}

// /adminsdono
async function adminsDono(bot, msg) {
    const db = getDB();
    const donos = db.prepare('SELECT user_id FROM admins_dono WHERE chat_id=?').all(String(msg.chat.id));
    let texto = '📋 *ADMINS DONO*\n\n';
    donos.forEach(d => texto += `👑 ${d.user_id}\n`);
    bot.sendMessage(msg.chat.id, texto || 'Nenhum.', { parse_mode: 'Markdown' });
}

async function isOwner(msg) {
    const donos = process.env.ADMIN_IDS.split(',').map(Number);
    return donos.includes(msg.from.id);
}

module.exports = { donoAdm, remDono, adminsDono };
