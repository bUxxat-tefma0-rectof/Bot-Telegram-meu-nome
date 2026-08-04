const { getDB } = require('../database');

// /setprefixo <novo>
async function setPrefixo(bot, msg, match) {
    if (!await isAdmin(msg)) return;
    const prefixo = match[1];
    const db = getDB();
    db.prepare('INSERT OR REPLACE INTO grupos (chat_id, prefixo) VALUES (?,?)').run(String(msg.chat.id), prefixo);
    bot.sendMessage(msg.chat.id, `⌨️ *Prefixo alterado para:* ${prefixo}`, { parse_mode: 'Markdown' });
}

// /resetprefix
async function resetPrefixo(bot, msg) {
    if (!await isAdmin(msg)) return;
    const db = getDB();
    db.prepare('INSERT OR REPLACE INTO grupos (chat_id, prefixo) VALUES (?,?)').run(String(msg.chat.id), '/');
    bot.sendMessage(msg.chat.id, '⌨️ *Prefixo resetado para /*', { parse_mode: 'Markdown' });
}

// /sistemgold
async function toggleGold(bot, msg) {
    if (!await isAdmin(msg)) return;
    const db = getDB();
    const g = db.prepare('SELECT sistema_gold FROM grupos WHERE chat_id=?').get(String(msg.chat.id));
    const novo = g?.sistema_gold ? 0 : 1;
    db.prepare('INSERT OR REPLACE INTO grupos (chat_id, sistema_gold) VALUES (?,?)').run(String(msg.chat.id), novo);
    bot.sendMessage(msg.chat.id, novo ? '🪙 *Sistema Gold ATIVADO*' : '🪙 *Sistema Gold DESATIVADO*', { parse_mode: 'Markdown' });
}

// /limitarcmd <comando>
async function limitarCmd(bot, msg, match) {
    if (!await isAdmin(msg)) return;
    const db = getDB();
    db.prepare('INSERT INTO cmds_bloqueados (chat_id, comando) VALUES (?,?)').run(String(msg.chat.id), match[1]);
    bot.sendMessage(msg.chat.id, `⛔ *Comando /${match[1]} bloqueado!*`, { parse_mode: 'Markdown' });
}

// /liberarcmd <comando>
async function liberarCmd(bot, msg, match) {
    if (!await isAdmin(msg)) return;
    const db = getDB();
    db.prepare('DELETE FROM cmds_bloqueados WHERE chat_id=? AND comando=?').run(String(msg.chat.id), match[1]);
    bot.sendMessage(msg.chat.id, `✅ *Comando /${match[1]} liberado!*`, { parse_mode: 'Markdown' });
}

async function isAdmin(msg) {
    try {
        const admins = process.env.ADMIN_IDS.split(',').map(Number);
        if (admins.includes(msg.from.id)) return true;
        return false;
    } catch (e) { return false; }
}

module.exports = { setPrefixo, resetPrefixo, toggleGold, limitarCmd, liberarCmd };
