const { getDB } = require('../database');

// /addprefix <prefixo>
async function addPrefix(bot, msg, match) {
    if (!await isAdmin(msg)) return;
    const prefixo = match[1];
    const db = getDB();
    db.prepare('INSERT INTO prefixos_extra (chat_id, prefixo) VALUES (?,?)').run(String(msg.chat.id), prefixo);
    bot.sendMessage(msg.chat.id, `➕ *Prefixo "${prefixo}" adicionado!*`, { parse_mode: 'Markdown' });
}

// /multiprefixo - Lista todos prefixos
async function listPrefixes(bot, msg) {
    const db = getDB();
    const prefixos = db.prepare('SELECT prefixo FROM prefixos_extra WHERE chat_id=?').all(String(msg.chat.id));
    const padrao = db.prepare('SELECT prefixo FROM grupos WHERE chat_id=?').get(String(msg.chat.id));
    
    let texto = '⌨️ *PREFIXOS ATIVOS*\n\n';
    texto += `📌 Padrão: ${padrao?.prefixo || '/'}\n`;
    prefixos.forEach((p, i) => texto += `➕ Extra ${i+1}: ${p.prefixo}\n`);
    
    bot.sendMessage(msg.chat.id, texto, { parse_mode: 'Markdown' });
}

// /remprefix <prefixo>
async function remPrefix(bot, msg, match) {
    if (!await isAdmin(msg)) return;
    const db = getDB();
    db.prepare('DELETE FROM prefixos_extra WHERE chat_id=? AND prefixo=?').run(String(msg.chat.id), match[1]);
    bot.sendMessage(msg.chat.id, `➖ *Prefixo "${match[1]}" removido!*`, { parse_mode: 'Markdown' });
}

async function isAdmin(msg) {
    try {
        const admins = process.env.ADMIN_IDS.split(',').map(Number);
        return admins.includes(msg.from.id);
    } catch (e) { return false; }
}

module.exports = { addPrefix, listPrefixes, remPrefix };
