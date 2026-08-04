const { getDB } = require('../database');

// /proibirfig
async function proibirFig(bot, msg) {
    if (!await isAdmin(msg)) return;
    if (!msg.reply_to_message || !msg.reply_to_message.sticker) return bot.sendMessage(msg.chat.id, '❌ Responda uma figurinha!');
    const db = getDB();
    const hash = msg.reply_to_message.sticker.file_unique_id;
    db.prepare('INSERT INTO figurinhas_proibidas (grupo_id, hash) VALUES (?,?)').run(String(msg.chat.id), hash);
    bot.sendMessage(msg.chat.id, '🛑 *Figurinha proibida!*', { parse_mode: 'Markdown' });
}

// /liberarfig
async function liberarFig(bot, msg) {
    if (!await isAdmin(msg)) return;
    const db = getDB();
    db.prepare('DELETE FROM figurinhas_proibidas WHERE grupo_id=?').run(String(msg.chat.id));
    bot.sendMessage(msg.chat.id, '✅ *Todas figurinhas liberadas!*', { parse_mode: 'Markdown' });
}

// /figban
async function figBan(bot, msg) {
    if (!await isAdmin(msg)) return;
    if (!msg.reply_to_message || !msg.reply_to_message.sticker) return bot.sendMessage(msg.chat.id, '❌ Responda uma figurinha!');
    const db = getDB();
    db.prepare('INSERT INTO figurinhas_proibidas (grupo_id, hash) VALUES (?,?)').run(String(msg.chat.id), msg.reply_to_message.sticker.file_unique_id);
    bot.sendMessage(msg.chat.id, '🔨 *Figurinha banida!*', { parse_mode: 'Markdown' });
}

// /delfigban
async function delFigBan(bot, msg) {
    if (!await isAdmin(msg)) return;
    if (!msg.reply_to_message || !msg.reply_to_message.sticker) return bot.sendMessage(msg.chat.id, '❌ Responda uma figurinha!');
    const db = getDB();
    db.prepare('DELETE FROM figurinhas_proibidas WHERE grupo_id=? AND hash=?').run(String(msg.chat.id), msg.reply_to_message.sticker.file_unique_id);
    bot.sendMessage(msg.chat.id, '✅ *Figurinha liberada!*', { parse_mode: 'Markdown' });
}

// /figlistanegra
async function figListaNegra(bot, msg) {
    const db = getDB();
    const figs = db.prepare('SELECT COUNT(*) as t FROM figurinhas_proibidas WHERE grupo_id=?').get(String(msg.chat.id));
    bot.sendMessage(msg.chat.id, `📜 *${figs.t} figurinhas na lista negra*`, { parse_mode: 'Markdown' });
}

async function isAdmin(msg) {
    try {
        const admins = process.env.ADMIN_IDS.split(',').map(Number);
        return admins.includes(msg.from.id);
    } catch (e) { return false; }
}

module.exports = { proibirFig, liberarFig, figBan, delFigBan, figListaNegra };
