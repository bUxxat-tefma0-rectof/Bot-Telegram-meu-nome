const { getDB } = require('../database');
const moment = require('moment');

// /ativações - Mostra status de todas as configurações
async function ativacoes(bot, msg) {
    const db = getDB();
    const g = db.prepare('SELECT * FROM grupos WHERE chat_id=?').get(String(msg.chat.id)) || {};
    
    const texto = `🔐 *CONFIGURAÇÕES ATIVAS*\n\n` +
        `🛡️ Anti Golpe: ${g.antigolpe ? '✅' : '❌'}\n` +
        `🌊 Anti Flood: ${g.antiflood ? g.antiflood + ' msgs' : '❌'}\n` +
        `🔒 Só Admins: ${g.soadm ? '✅' : '❌'}\n` +
        `🔠 Limite Caractere: ${g.limite_caractere || '❌'}\n` +
        `🪙 Sistema Gold: ${g.sistema_gold ? '✅' : '❌'}\n` +
        `📝 Prefixo: ${g.prefixo || '/'}`;
    
    bot.sendMessage(msg.chat.id, texto, { parse_mode: 'Markdown' });
}

// /vencimento - Status do bot
async function vencimento(bot, msg) {
    const db = getDB();
    const totalGrupos = db.prepare('SELECT COUNT(*) as t FROM grupos').get().t;
    const totalBans = db.prepare('SELECT COUNT(*) as t FROM banidos').get().t;
    const uptime = process.uptime();
    const horas = Math.floor(uptime / 3600);
    const minutos = Math.floor((uptime % 3600) / 60);
    
    const texto = `⏳ *STATUS DO BOT*\n\n` +
        `📊 Grupos: *${totalGrupos}*\n` +
        `🚫 Bans: *${totalBans}*\n` +
        `⏱️ Online: *${horas}h ${minutos}m*\n` +
        `✅ Status: *Operacional*`;
    
    bot.sendMessage(msg.chat.id, texto, { parse_mode: 'Markdown' });
}

module.exports = { ativacoes, vencimento };
