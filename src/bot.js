const TelegramBot = require('node-telegram-bot-api');
const { getDB, initDB } = require('./database');
const moment = require('moment');
const { ativacoes, vencimento } = require('./comandos/painel');
const { setPrefixo, resetPrefixo, toggleGold, limitarCmd, liberarCmd } = require('./comandos/config');
const { donoAdm, remDono, adminsDono } = require('./comandos/gestao');
const { remAdv, minhasPunicoes, listaNegraUsers, addPalavra, remPalavra } = require('./comandos/mod_avancado');
const { checkAtivo, inativos, banHost } = require('./comandos/atividade');
const { startAds, stopAds } = require('./comandos/anuncios');
const { autoFechar, dmUser, lerMsgJson } = require('./comandos/grupo_extra');
const { proibirFig, liberarFig, figBan, delFigBan, figListaNegra } = require('./comandos/figurinhas');
const { noTag, noTag2 } = require('./comandos/notag');
const { bannerBv } = require('./comandos/banner');
const { gpStatus } = require('./comandos/gpstts');

let bot = null;

async function startBot() {
    bot = new TelegramBot(process.env.BOT_TOKEN, { polling: true });
    
    // ============ COMANDOS DO PAINEL ============
    bot.onText(/\/ativa(.*)o/, (msg) => ativacoes(bot, msg));
    bot.onText(/\/vencimento/, (msg) => vencimento(bot, msg));
    bot.onText(/\/ativartudo/, async (msg) => { if (await isAdmin(msg)) { const db = getDB(); db.prepare('UPDATE grupos SET antiflood=5, antigolpe=1 WHERE chat_id=?').run(String(msg.chat.id)); bot.sendMessage(msg.chat.id, '🚀 Tudo ativado!'); }});
    bot.onText(/\/desativartudo/, async (msg) => { if (await isAdmin(msg)) { const db = getDB(); db.prepare('UPDATE grupos SET antiflood=0, antigolpe=0 WHERE chat_id=?').run(String(msg.chat.id)); bot.sendMessage(msg.chat.id, '🛑 Tudo desativado!'); }});
    
    // ============ CONFIGURAÇÕES ============
    bot.onText(/\/soadm/, async (msg) => { if (await isAdmin(msg)) { const db = getDB(); const g = db.prepare('SELECT soadm FROM grupos WHERE chat_id=?').get(String(msg.chat.id)); db.prepare('INSERT OR REPLACE INTO grupos (chat_id, soadm) VALUES (?,?)').run(String(msg.chat.id), g?.soadm ? 0 : 1); bot.sendMessage(msg.chat.id, g?.soadm ? '🔓 Desativado' : '🔒 Ativado'); }});
    bot.onText(/\/antigolpe/, async (msg) => { if (await isAdmin(msg)) { const db = getDB(); const g = db.prepare('SELECT antigolpe FROM grupos WHERE chat_id=?').get(String(msg.chat.id)); db.prepare('INSERT OR REPLACE INTO grupos (chat_id, antigolpe) VALUES (?,?)').run(String(msg.chat.id), g?.antigolpe ? 0 : 1); bot.sendMessage(msg.chat.id, g?.antigolpe ? '🛡️ Off' : '🛡️ On'); }});
    bot.onText(/\/sistemgold/, (msg) => toggleGold(bot, msg));
    bot.onText(/\/setprefixo (.+)/, (msg, m) => setPrefixo(bot, msg, m));
    bot.onText(/\/resetprefix/, (msg) => resetPrefixo(bot, msg));
    bot.onText(/\/limitarcmd (.+)/, (msg, m) => limitarCmd(bot, msg, m));
    bot.onText(/\/liberarcmd (.+)/, (msg, m) => liberarCmd(bot, msg, m));
    
    // ============ GESTÃO ============
    bot.onText(/\/donoadm/, (msg) => donoAdm(bot, msg));
    bot.onText(/\/remdono/, (msg) => remDono(bot, msg));
    bot.onText(/\/adminsdono/, (msg) => adminsDono(bot, msg));
    
    // ============ MODERAÇÃO ============
    bot.onText(/\/remadv/, (msg) => remAdv(bot, msg));
    bot.onText(/\/minhaspunicoes/, (msg) => minhasPunicoes(bot, msg));
    bot.onText(/\/listanegrausers/, (msg) => listaNegraUsers(bot, msg));
    bot.onText(/\/addpalavra (.+)/, (msg, m) => addPalavra(bot, msg, m));
    bot.onText(/\/rempalavra (.+)/, (msg, m) => remPalavra(bot, msg, m));
    
    // ============ ATIVIDADE ============
    bot.onText(/\/checkativo/, (msg) => checkAtivo(bot, msg));
    bot.onText(/\/inativos (\d+)/, (msg, m) => inativos(bot, msg, m));
    bot.onText(/\/banghost (\d+)/, (msg, m) => banHost(bot, msg, m));
    
    // ============ ANÚNCIOS ============
    bot.onText(/\/startads/, (msg) => startAds(bot, msg));
    bot.onText(/\/stopads/, (msg) => stopAds(bot, msg));
    
    // ============ GRUPO ============
    bot.onText(/\/auto (a|f) (.+)/, (msg, m) => autoFechar(bot, msg, m));
    bot.onText(/\/dm/, (msg) => dmUser(bot, msg));
    bot.onText(/\/msg/, (msg) => lerMsgJson(bot, msg));
    bot.onText(/\/notag (.+)/, (msg, m) => noTag(bot, msg, m));
    bot.onText(/\/notag2 (.+)/, (msg, m) => noTag2(bot, msg, m));
    
    // ============ FIGURINHAS ============
    bot.onText(/\/proibirfig/, (msg) => proibirFig(bot, msg));
    bot.onText(/\/liberarfig/, (msg) => liberarFig(bot, msg));
    bot.onText(/\/figban/, (msg) => figBan(bot, msg));
    bot.onText(/\/delfigban/, (msg) => delFigBan(bot, msg));
    bot.onText(/\/figlistanegra/, (msg) => figListaNegra(bot, msg));
    
    // ============ BANNER E STATUS ============
    bot.onText(/\/bannerbv (.+)/, (msg, m) => bannerBv(bot, msg, m));
    bot.onText(/\/gpstts/, (msg) => gpStatus(bot, msg));
    
    console.log('✅ DINI\'Z BOT 100% configurado!');
}

async function isAdmin(msg) {
    try {
        const admins = process.env.ADMIN_IDS.split(',').map(Number);
        return admins.includes(msg.from.id);
    } catch (e) { return false; }
}

module.exports = { startBot };
