const { getDB } = require('../database');

// /figadv - Figurinha gera advertência
async function figAdv(bot, msg) {
    if (!await isAdmin(msg)) return;
    if (!msg.reply_to_message || !msg.reply_to_message.sticker) {
        return bot.sendMessage(msg.chat.id, '❌ Responda uma figurinha!');
    }
    const db = getDB();
    const hash = msg.reply_to_message.sticker.file_unique_id;
    db.prepare('INSERT INTO fig_adv (grupo_id, hash) VALUES (?,?)').run(String(msg.chat.id), hash);
    bot.sendMessage(msg.chat.id, '⚠️ *Figurinha marcada como advertência!*', { parse_mode: 'Markdown' });
}

// /delfigadv - Remove figurinha de advertência
async function delFigAdv(bot, msg) {
    if (!await isAdmin(msg)) return;
    if (!msg.reply_to_message || !msg.reply_to_message.sticker) {
        return bot.sendMessage(msg.chat.id, '❌ Responda uma figurinha!');
    }
    const db = getDB();
    db.prepare('DELETE FROM fig_adv WHERE grupo_id=? AND hash=?').run(String(msg.chat.id), msg.reply_to_message.sticker.file_unique_id);
    bot.sendMessage(msg.chat.id, '✅ *Figurinha de advertência removida!*', { parse_mode: 'Markdown' });
}

// /figdel - Figurinha que deleta a mensagem
async function figDel(bot, msg) {
    if (!await isAdmin(msg)) return;
    if (!msg.reply_to_message || !msg.reply_to_message.sticker) {
        return bot.sendMessage(msg.chat.id, '❌ Responda uma figurinha!');
    }
    const db = getDB();
    const hash = msg.reply_to_message.sticker.file_unique_id;
    db.prepare('INSERT INTO fig_del (grupo_id, hash) VALUES (?,?)').run(String(msg.chat.id), hash);
    bot.sendMessage(msg.chat.id, '🗑️ *Figurinha marcada para deletar!*', { parse_mode: 'Markdown' });
}

// /delfigdel - Remove figurinha de deletar
async function delFigDel(bot, msg) {
    if (!await isAdmin(msg)) return;
    if (!msg.reply_to_message || !msg.reply_to_message.sticker) {
        return bot.sendMessage(msg.chat.id, '❌ Responda uma figurinha!');
    }
    const db = getDB();
    db.prepare('DELETE FROM fig_del WHERE grupo_id=? AND hash=?').run(String(msg.chat.id), msg.reply_to_message.sticker.file_unique_id);
    bot.sendMessage(msg.chat.id, '✅ *Figurinha de deletar removida!*', { parse_mode: 'Markdown' });
}

async function isAdmin(msg) {
    try {
        const admins = process.env.ADMIN_IDS.split(',').map(Number);
        return admins.includes(msg.from.id);
    } catch (e) { return false; }
}

module.exports = { figAdv, delFigAdv, figDel, delFigDel };
