const { getDB } = require('../database');

// /bannerbv <url da imagem>
async function bannerBv(bot, msg, match) {
    if (!await isAdmin(msg)) return;
    const url = match[1];
    const db = getDB();
    db.prepare('INSERT OR REPLACE INTO grupos (chat_id, banner) VALUES (?,?)').run(String(msg.chat.id), url);
    bot.sendMessage(msg.chat.id, '🖼️ *Banner de boas-vindas atualizado!*', { parse_mode: 'Markdown' });
}

async function isAdmin(msg) {
    try {
        const admins = process.env.ADMIN_IDS.split(',').map(Number);
        return admins.includes(msg.from.id);
    } catch (e) { return false; }
}

module.exports = { bannerBv };
