const { getDB } = require('../database');
const anunciosAtivos = new Map();

// /startads
async function startAds(bot, msg) {
    if (!await isAdmin(msg)) return;
    const db = getDB();
    const ads = db.prepare('SELECT * FROM anuncios WHERE chat_id=? AND ativo=1').all(String(msg.chat.id));
    
    if (ads.length === 0) return bot.sendMessage(msg.chat.id, '❌ Nenhum anúncio configurado.');
    
    ads.forEach(ad => {
        const interval = setInterval(() => {
            bot.sendMessage(msg.chat.id, `📢 *ANÚNCIO*\n\n${ad.mensagem}`, { parse_mode: 'Markdown' });
        }, ad.intervalo * 60 * 1000);
        anunciosAtivos.set(ad.id, interval);
    });
    
    bot.sendMessage(msg.chat.id, '▶️ *Anúncios iniciados!*', { parse_mode: 'Markdown' });
}

// /stopads
async function stopAds(bot, msg) {
    if (!await isAdmin(msg)) return;
    for (const [id, interval] of anunciosAtivos) {
        clearInterval(interval);
    }
    anunciosAtivos.clear();
    bot.sendMessage(msg.chat.id, '⏸️ *Anúncios parados!*', { parse_mode: 'Markdown' });
}

async function isAdmin(msg) {
    try {
        const admins = process.env.ADMIN_IDS.split(',').map(Number);
        return admins.includes(msg.from.id);
    } catch (e) { return false; }
}

module.exports = { startAds, stopAds };
