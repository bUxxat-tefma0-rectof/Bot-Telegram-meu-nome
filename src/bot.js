const TelegramBot = require('node-telegram-bot-api');
const { getDB } = require('./database');
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
const { addPrefix, listPrefixes, remPrefix } = require('./comandos/multiprefixo');
const { figAdv, delFigAdv, figDel, delFigDel } = require('./comandos/fig_adv_del');

let bot = null;

async function startBot() {
    bot = new TelegramBot(process.env.BOT_TOKEN, { polling: true });
    
    // ============ PAINEL ============
    bot.onText(/\/ativa(.*)o/, (msg) => ativacoes(bot, msg));
    bot.onText(/\/vencimento/, (msg) => vencimento(bot, msg));
    
    bot.onText(/\/ativartudo/, async (msg) => {
        if (!await isAdmin(msg)) return;
        const db = getDB();
        db.prepare('UPDATE grupos SET antiflood=5, antigolpe=1 WHERE chat_id=?').run(String(msg.chat.id));
        bot.sendMessage(msg.chat.id, '🚀 *Todas as proteções ativadas!*', { parse_mode: 'Markdown' });
    });
    
    bot.onText(/\/desativartudo/, async (msg) => {
        if (!await isAdmin(msg)) return;
        const db = getDB();
        db.prepare('UPDATE grupos SET antiflood=0, antigolpe=0 WHERE chat_id=?').run(String(msg.chat.id));
        bot.sendMessage(msg.chat.id, '🛑 *Todas as proteções desativadas!*', { parse_mode: 'Markdown' });
    });
    
    bot.onText(/\/rankadmin/, async (msg) => {
        const db = getDB();
        const rank = db.prepare('SELECT user_id, quantidade FROM mensagens_contador WHERE chat_id=? ORDER BY quantidade DESC LIMIT 10').all(String(msg.chat.id));
        let texto = '🏆 *RANK ADMIN*\n\n';
        rank.forEach((r, i) => texto += `${i+1}º - ${r.user_id}: ${r.quantidade} msgs\n`);
        bot.sendMessage(msg.chat.id, texto || 'Sem dados.', { parse_mode: 'Markdown' });
    });
    
    // ============ CONFIGURAÇÕES ============
    bot.onText(/\/soadm/, async (msg) => {
        if (!await isAdmin(msg)) return;
        const db = getDB();
        const g = db.prepare('SELECT soadm FROM grupos WHERE chat_id=?').get(String(msg.chat.id));
        const novo = g?.soadm ? 0 : 1;
        db.prepare('INSERT OR REPLACE INTO grupos (chat_id, soadm) VALUES (?,?)').run(String(msg.chat.id), novo);
        bot.sendMessage(msg.chat.id, novo ? '🔒 *Modo Só Admins ATIVADO*' : '🔓 *Modo Só Admins DESATIVADO*', { parse_mode: 'Markdown' });
    });
    
    bot.onText(/\/antigolpe/, async (msg) => {
        if (!await isAdmin(msg)) return;
        const db = getDB();
        const g = db.prepare('SELECT antigolpe FROM grupos WHERE chat_id=?').get(String(msg.chat.id));
        const novo = g?.antigolpe ? 0 : 1;
        db.prepare('INSERT OR REPLACE INTO grupos (chat_id, antigolpe) VALUES (?,?)').run(String(msg.chat.id), novo);
        bot.sendMessage(msg.chat.id, novo ? '🛡️ *Anti Golpe ATIVADO*' : '🛡️ *Anti Golpe DESATIVADO*', { parse_mode: 'Markdown' });
    });
    
    bot.onText(/\/antiflood (\d+)/, async (msg, match) => {
        if (!await isAdmin(msg)) return;
        const db = getDB();
        db.prepare('INSERT OR REPLACE INTO grupos (chat_id, antiflood) VALUES (?,?)').run(String(msg.chat.id), parseInt(match[1]));
        bot.sendMessage(msg.chat.id, `🌊 *AntiFlood: ${match[1]} msgs*`, { parse_mode: 'Markdown' });
    });
    
    bot.onText(/\/limitecaractere (\d+)/, async (msg, match) => {
        if (!await isAdmin(msg)) return;
        const db = getDB();
        db.prepare('INSERT OR REPLACE INTO grupos (chat_id, limite_caractere) VALUES (?,?)').run(String(msg.chat.id), parseInt(match[1]));
        bot.sendMessage(msg.chat.id, `🔠 *Limite: ${match[1]} caracteres*`, { parse_mode: 'Markdown' });
    });
    
    bot.onText(/\/setbemvindo (.+)/, async (msg, match) => {
        if (!await isAdmin(msg)) return;
        const db = getDB();
        db.prepare('INSERT OR REPLACE INTO grupos (chat_id, bemvindo) VALUES (?,?)').run(String(msg.chat.id), match[1]);
        bot.sendMessage(msg.chat.id, '📝 *Boas-vindas atualizada!*', { parse_mode: 'Markdown' });
    });
    
    bot.onText(/\/setprefixo (.+)/, (msg, m) => setPrefixo(bot, msg, m));
    bot.onText(/\/resetprefix/, (msg) => resetPrefixo(bot, msg));
    bot.onText(/\/sistemgold/, (msg) => toggleGold(bot, msg));
    bot.onText(/\/limitarcmd (.+)/, (msg, m) => limitarCmd(bot, msg, m));
    bot.onText(/\/liberarcmd (.+)/, (msg, m) => liberarCmd(bot, msg, m));
    
    // ============ MULTIPREFIXO ============
    bot.onText(/\/addprefix (.+)/, (msg, m) => addPrefix(bot, msg, m));
    bot.onText(/\/multiprefixo/, (msg) => listPrefixes(bot, msg));
    bot.onText(/\/remprefix (.+)/, (msg, m) => remPrefix(bot, msg, m));
    
    // ============ GESTÃO ============
    bot.onText(/\/promover/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda a mensagem!');
        try {
            await bot.promoteChatMember(msg.chat.id, msg.reply_to_message.from.id, {
                can_manage_chat: true, can_delete_messages: true,
                can_restrict_members: true, can_invite_users: true
            });
            bot.sendMessage(msg.chat.id, '⬆️ *Promovido a admin!*', { parse_mode: 'Markdown' });
        } catch (e) {
            bot.sendMessage(msg.chat.id, '❌ Não foi possível promover.');
        }
    });
    
    bot.onText(/\/rebaixar/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda a mensagem!');
        try {
            await bot.promoteChatMember(msg.chat.id, msg.reply_to_message.from.id, {
                can_manage_chat: false, can_delete_messages: false,
                can_restrict_members: false, can_invite_users: false
            });
            bot.sendMessage(msg.chat.id, '⬇️ *Rebaixado!*', { parse_mode: 'Markdown' });
        } catch (e) {
            bot.sendMessage(msg.chat.id, '❌ Não foi possível rebaixar.');
        }
    });
    
    bot.onText(/\/addmod/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda!');
        const db = getDB();
        db.prepare('INSERT OR REPLACE INTO moderadores (chat_id, user_id) VALUES (?,?)').run(String(msg.chat.id), String(msg.reply_to_message.from.id));
        bot.sendMessage(msg.chat.id, '👮 *Moderador adicionado!*', { parse_mode: 'Markdown' });
    });
    
    bot.onText(/\/remmod/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda!');
        const db = getDB();
        db.prepare('DELETE FROM moderadores WHERE chat_id=? AND user_id=?').run(String(msg.chat.id), String(msg.reply_to_message.from.id));
        bot.sendMessage(msg.chat.id, '👮 *Moderador removido!*', { parse_mode: 'Markdown' });
    });
    
    bot.onText(/\/mods/, async (msg) => {
        const db = getDB();
        const mods = db.prepare('SELECT user_id FROM moderadores WHERE chat_id=?').all(String(msg.chat.id));
        let texto = '🛡️ *MODERADORES*\n\n';
        mods.forEach(m => texto += `👮 ${m.user_id}\n`);
        bot.sendMessage(msg.chat.id, texto || 'Nenhum.', { parse_mode: 'Markdown' });
    });
    
    bot.onText(/\/donoadm/, (msg) => donoAdm(bot, msg));
    bot.onText(/\/remdono/, (msg) => remDono(bot, msg));
    bot.onText(/\/adminsdono/, (msg) => adminsDono(bot, msg));
    
    // ============ MODERAÇÃO ============
    bot.onText(/\/ban/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda!');
        try {
            await bot.banChatMember(msg.chat.id, msg.reply_to_message.from.id);
            const db = getDB();
            db.prepare('INSERT INTO banidos (chat_id, user_id, motivo) VALUES (?,?,?)').run(String(msg.chat.id), String(msg.reply_to_message.from.id), 'Banido');
            bot.sendMessage(msg.chat.id, '🔨 *Banido!*', { parse_mode: 'Markdown' });
        } catch (e) {
            bot.sendMessage(msg.chat.id, '❌ Erro ao banir.');
        }
    });
    
    bot.onText(/\/mute/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda!');
        try {
            await bot.restrictChatMember(msg.chat.id, msg.reply_to_message.from.id, { can_send_messages: false });
            bot.sendMessage(msg.chat.id, '🔇 *Mutado!*', { parse_mode: 'Markdown' });
        } catch (e) {
            bot.sendMessage(msg.chat.id, '❌ Erro.');
        }
    });
    
    bot.onText(/\/unmute/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda!');
        try {
            await bot.restrictChatMember(msg.chat.id, msg.reply_to_message.from.id, {
                can_send_messages: true, can_send_media_messages: true, can_send_other_messages: true
            });
            bot.sendMessage(msg.chat.id, '🔊 *Desmutado!*', { parse_mode: 'Markdown' });
        } catch (e) {
            bot.sendMessage(msg.chat.id, '❌ Erro.');
        }
    });
    
    bot.onText(/\/adv/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda!');
        const db = getDB();
        const uid = String(msg.reply_to_message.from.id);
        const av = db.prepare('SELECT quantidade FROM avisos WHERE chat_id=? AND user_id=?').get(String(msg.chat.id), uid);
        const qtd = (av?.quantidade || 0) + 1;
        db.prepare('INSERT OR REPLACE INTO avisos (chat_id, user_id, quantidade) VALUES (?,?,?)').run(String(msg.chat.id), uid, qtd);
        bot.sendMessage(msg.chat.id, `⚠️ *Advertência ${qtd}/3!*`, { parse_mode: 'Markdown' });
        if (qtd >= 3) {
            try { await bot.banChatMember(msg.chat.id, parseInt(uid)); } catch (e) {}
            bot.sendMessage(msg.chat.id, '🔨 *Banido por 3 advertências!*', { parse_mode: 'Markdown' });
        }
    });
    
    bot.onText(/\/unban/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda!');
        try {
            await bot.unbanChatMember(msg.chat.id, msg.reply_to_message.from.id);
            bot.sendMessage(msg.chat.id, '✅ *Desbanido!*', { parse_mode: 'Markdown' });
        } catch (e) {
            bot.sendMessage(msg.chat.id, '❌ Erro.');
        }
    });
    
    bot.onText(/\/listanegra/, async (msg) => {
        const db = getDB();
        const bans = db.prepare('SELECT * FROM banidos WHERE chat_id=?').all(String(msg.chat.id));
        let texto = '☠️ *LISTA NEGRA*\n\n';
        bans.forEach(b => texto += `🚫 ${b.user_id}\n`);
        bot.sendMessage(msg.chat.id, texto || 'Nenhum.', { parse_mode: 'Markdown' });
    });
    
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
    bot.onText(/\/setads (\d+) \| (.+)/, async (msg, match) => {
        if (!await isAdmin(msg)) return;
        const db = getDB();
        db.prepare('INSERT INTO anuncios (chat_id, mensagem, intervalo) VALUES (?,?,?)').run(String(msg.chat.id), match[2], parseInt(match[1]));
        bot.sendMessage(msg.chat.id, '⏱️ *Anúncio configurado!*', { parse_mode: 'Markdown' });
    });
    
    bot.onText(/\/listads/, async (msg) => {
        const db = getDB();
        const ads = db.prepare('SELECT * FROM anuncios WHERE chat_id=?').all(String(msg.chat.id));
        let texto = '📋 *ANÚNCIOS*\n\n';
        ads.forEach((a, i) => texto += `${i+1}. ${a.mensagem} (${a.intervalo}min)\n`);
        bot.sendMessage(msg.chat.id, texto || 'Nenhum.', { parse_mode: 'Markdown' });
    });
    
    bot.onText(/\/rmads (\d+)/, async (msg, match) => {
        if (!await isAdmin(msg)) return;
        const db = getDB();
        const ads = db.prepare('SELECT * FROM anuncios WHERE chat_id=?').all(String(msg.chat.id));
        const idx = parseInt(match[1]) - 1;
        if (ads[idx]) { db.prepare('DELETE FROM anuncios WHERE id=?').run(ads[idx].id); bot.sendMessage(msg.chat.id, '🗑️ Removido!'); }
    });
    
    bot.onText(/\/startads/, (msg) => startAds(bot, msg));
    bot.onText(/\/stopads/, (msg) => stopAds(bot, msg));
    
    // ============ GRUPO ============
    bot.onText(/\/fechar/, async (msg) => {
        if (!await isAdmin(msg)) return;
        await bot.setChatPermissions(msg.chat.id, { can_send_messages: false });
        bot.sendMessage(msg.chat.id, '🔒 *Fechado!*', { parse_mode: 'Markdown' });
    });
    
    bot.onText(/\/abrir/, async (msg) => {
        if (!await isAdmin(msg)) return;
        await bot.setChatPermissions(msg.chat.id, { can_send_messages: true, can_send_media_messages: true, can_send_other_messages: true });
        bot.sendMessage(msg.chat.id, '🔓 *Aberto!*', { parse_mode: 'Markdown' });
    });
    
    bot.onText(/\/link/, async (msg) => {
        if (!await isAdmin(msg)) return;
        try {
            const link = await bot.exportChatInviteLink(msg.chat.id);
            bot.sendMessage(msg.chat.id, `🔗 ${link}`);
        } catch (e) {
            bot.sendMessage(msg.chat.id, '❌ Erro.');
        }
    });
    
    bot.onText(/\/hidetag (.+)/, async (msg, match) => {
        if (!await isAdmin(msg)) return;
        await bot.sendMessage(msg.chat.id, match[1], { disable_notification: true });
    });
    
    bot.onText(/\/totag (.+)/, async (msg, match) => {
        if (!await isAdmin(msg)) return;
        const membros = await bot.getChatAdministrators(msg.chat.id);
        let menc = '';
        membros.forEach(m => menc += `[\u200B](tg://user?id=${m.user.id})`);
        bot.sendMessage(msg.chat.id, `${match[1]}\n${menc}`, { parse_mode: 'Markdown' });
    });
    
    bot.onText(/\/d/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return;
        try { await bot.deleteMessage(msg.chat.id, msg.reply_to_message.message_id); await bot.deleteMessage(msg.chat.id, msg.message_id); } catch (e) {}
    });
    
    bot.onText(/\/afk (.+)/, async (msg, match) => {
        const db = getDB();
        db.prepare('INSERT OR REPLACE INTO afk_users (user_id, motivo, data) VALUES (?,?,?)').run(String(msg.from.id), match[1], new Date().toISOString());
        bot.sendMessage(msg.chat.id, `💤 *${msg.from.first_name} está AFK*\n📝 ${match[1]}`, { parse_mode: 'Markdown' });
    });
    
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
    bot.onText(/\/figadv/, (msg) => figAdv(bot, msg));
    bot.onText(/\/delfigadv/, (msg) => delFigAdv(bot, msg));
    bot.onText(/\/figdel/, (msg) => figDel(bot, msg));
    bot.onText(/\/delfigdel/, (msg) => delFigDel(bot, msg));
    
    // ============ BANNER E STATUS ============
    bot.onText(/\/bannerbv (.+)/, (msg, m) => bannerBv(bot, msg, m));
    bot.onText(/\/gpstts/, (msg) => gpStatus(bot, msg));
    
    // ============ BOAS-VINDAS ============
    bot.on('new_chat_members', async (msg) => {
        const db = getDB();
        const g = db.prepare('SELECT bemvindo, banner FROM grupos WHERE chat_id=?').get(String(msg.chat.id));
        msg.new_chat_members.forEach(async (m) => {
            const txt = (g?.bemvindo || 'Bem-vindo(a) {nome}!').replace('{nome}', m.first_name).replace('{grupo}', msg.chat.title);
            if (g?.banner) {
                bot.sendPhoto(msg.chat.id, g.banner, { caption: txt });
            } else {
                bot.sendMessage(msg.chat.id, txt);
            }
        });
    });
    
    // ============ DETECTORES AUTOMÁTICOS ============
    bot.on('message', async (msg) => {
        if (!msg.chat || msg.chat.type === 'private') return;
        if (!msg.from) return;
        
        const db = getDB();
        const g = db.prepare('SELECT * FROM grupos WHERE chat_id=?').get(String(msg.chat.id));
        
        // Anti-flood
        if (g?.antiflood > 0) {
            const msgs = db.prepare('SELECT quantidade FROM mensagens_contador WHERE chat_id=? AND user_id=?').get(String(msg.chat.id), String(msg.from.id));
            const qtd = (msgs?.quantidade || 0) + 1;
            if (qtd > g.antiflood) {
                try { await bot.restrictChatMember(msg.chat.id, msg.from.id, { can_send_messages: false }); } catch (e) {}
                bot.sendMessage(msg.chat.id, `🌊 *${msg.from.first_name} mutado por flood!*`, { parse_mode: 'Markdown' });
            }
            db.prepare('INSERT OR REPLACE INTO mensagens_contador (chat_id, user_id, quantidade) VALUES (?,?,?)').run(String(msg.chat.id), String(msg.from.id), qtd);
            setTimeout(() => {
                db.prepare('UPDATE mensagens_contador SET quantidade=0 WHERE chat_id=? AND user_id=?').run(String(msg.chat.id), String(msg.from.id));
            }, 10000);
        }
        
        // Limite caracteres
        if (g?.limite_caractere > 0 && msg.text && msg.text.length > g.limite_caractere) {
            try { await bot.deleteMessage(msg.chat.id, msg.message_id); } catch (e) {}
        }
        
        // Palavras proibidas
        if (msg.text) {
            const palavras = db.prepare('SELECT palavra FROM palavras_proibidas WHERE chat_id=?').all(String(msg.chat.id));
            for (const p of palavras) {
                if (msg.text.toLowerCase().includes(p.palavra)) {
                    try { await bot.deleteMessage(msg.chat.id, msg.message_id); } catch (e) {}
                    bot.sendMessage(msg.chat.id, `🤬 Palavra proibida detectada!`);
                    return;
                }
            }
        }
        
        // Figurinhas
        if (msg.sticker) {
            const hash = msg.sticker.file_unique_id;
            
            const proibida = db.prepare('SELECT * FROM figurinhas_proibidas WHERE grupo_id=? AND hash=?').get(String(msg.chat.id), hash);
            if (proibida) { try { await bot.deleteMessage(msg.chat.id, msg.message_id); } catch (e) {} return; }
            
            const adv = db.prepare('SELECT * FROM fig_adv WHERE grupo_id=? AND hash=?').get(String(msg.chat.id), hash);
            if (adv) {
                const uid = String(msg.from.id);
                const av = db.prepare('SELECT quantidade FROM avisos WHERE chat_id=? AND user_id=?').get(String(msg.chat.id), uid);
                const qtd = (av?.quantidade || 0) + 1;
                db.prepare('INSERT OR REPLACE INTO avisos (chat_id, user_id, quantidade) VALUES (?,?,?)').run(String(msg.chat.id), uid, qtd);
                if (qtd >= 3) { try { await bot.banChatMember(msg.chat.id, msg.from.id); } catch (e) {} }
                return;
            }
            
            const del = db.prepare('SELECT * FROM fig_del WHERE grupo_id=? AND hash=?').get(String(msg.chat.id), hash);
            if (del) { try { await bot.deleteMessage(msg.chat.id, msg.message_id); } catch (e) {} return; }
        }
        
        // AFK reply
        if (msg.reply_to_message) {
            const afk = db.prepare('SELECT * FROM afk_users WHERE user_id=?').get(String(msg.reply_to_message.from.id));
            if (afk) {
                bot.sendMessage(msg.chat.id, `💤 ${msg.reply_to_message.from.first_name} está AFK desde ${moment(afk.data).fromNow()}\n📝 ${afk.motivo}`, { parse_mode: 'Markdown' });
            }
        }
        
        // Remove AFK
        db.prepare('DELETE FROM afk_users WHERE user_id=?').run(String(msg.from.id));
    });
    
    console.log('✅ DINI\'Z BOT 100% configurado!');
}

async function isAdmin(msg) {
    try {
        const admins = process.env.ADMIN_IDS.split(',').map(Number);
        if (admins.includes(msg.from.id)) return true;
        return false;
    } catch (e) { return false; }
}

module.exports = { startBot };
