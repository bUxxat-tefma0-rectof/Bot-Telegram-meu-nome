const { getDB } = require('../database');

// /remadv
async function remAdv(bot, msg) {
    if (!await isAdmin(msg)) return;
    if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda a mensagem!');
    const db = getDB();
    db.prepare('DELETE FROM avisos WHERE chat_id=? AND user_id=?').run(String(msg.chat.id), String(msg.reply_to_message.from.id));
    bot.sendMessage(msg.chat.id, '✅ *Advertências removidas!*', { parse_mode: 'Markdown' });
}

// /minhaspunicoes
async function minhasPunicoes(bot, msg) {
    const db = getDB();
    const avisos = db.prepare('SELECT quantidade FROM avisos WHERE chat_id=? AND user_id=?').get(String(msg.chat.id), String(msg.from.id));
    const banido = db.prepare('SELECT * FROM banidos WHERE chat_id=? AND user_id=?').get(String(msg.chat.id), String(msg.from.id));
    
    let texto = '📜 *MINHAS PUNIÇÕES*\n\n';
    texto += `⚠️ Advertências: ${avisos?.quantidade || 0}/3\n`;
    texto += `🚫 Banido: ${banido ? 'Sim' : 'Não'}`;
    
    bot.sendMessage(msg.chat.id, texto, { parse_mode: 'Markdown' });
}

// /listanegrausers
async function listaNegraUsers(bot, msg) {
    const db = getDB();
    const bans = db.prepare('SELECT * FROM banidos WHERE chat_id=?').all(String(msg.chat.id));
    let texto = '☠️ *LISTA NEGRA*\n\n';
    bans.forEach((b, i) => texto += `${i+1}. ${b.user_id}\n   Motivo: ${b.motivo}\n   Data: ${b.data}\n\n`);
    bot.sendMessage(msg.chat.id, texto || 'Nenhum.', { parse_mode: 'Markdown' });
}

// /addpalavra <palavra>
async function addPalavra(bot, msg, match) {
    if (!await isAdmin(msg)) return;
    const db = getDB();
    db.prepare('INSERT INTO palavras_proibidas (chat_id, palavra) VALUES (?,?)').run(String(msg.chat.id), match[1].toLowerCase());
    bot.sendMessage(msg.chat.id, `🤬 *Palavra "${match[1]}" adicionada!*`, { parse_mode: 'Markdown' });
}

// /rempalavra <palavra>
async function remPalavra(bot, msg, match) {
    if (!await isAdmin(msg)) return;
    const db = getDB();
    db.prepare('DELETE FROM palavras_proibidas WHERE chat_id=? AND palavra=?').run(String(msg.chat.id), match[1].toLowerCase());
    bot.sendMessage(msg.chat.id, `✅ *Palavra "${match[1]}" removida!*`, { parse_mode: 'Markdown' });
}

async function isAdmin(msg) {
    try {
        const admins = process.env.ADMIN_IDS.split(',').map(Number);
        return admins.includes(msg.from.id);
    } catch (e) { return false; }
}

module.exports = { remAdv, minhasPunicoes, listaNegraUsers, addPalavra, remPalavra };
