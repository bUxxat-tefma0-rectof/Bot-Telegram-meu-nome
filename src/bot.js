const TelegramBot = require('node-telegram-bot-api');
const { getDB } = require('./database');
const moment = require('moment');

let bot = null;

async function startBot() {
    bot = new TelegramBot(process.env.BOT_TOKEN, { polling: true });
    
    // ============ PAINEL ============
    
    // /ativartudo - Ativa todas as proteções
    bot.onText(/\/ativartudo/, async (msg) => {
        if (!await isAdmin(msg)) return;
        const db = getDB();
        db.prepare('UPDATE grupos SET antiflood=5, antigolpe=1, soadm=0 WHERE chat_id=?').run(String(msg.chat.id));
        bot.sendMessage(msg.chat.id, '🚀 *Todas as proteções ativadas!*', { parse_mode: 'Markdown' });
    });
    
    // /desativartudo
    bot.onText(/\/desativartudo/, async (msg) => {
        if (!await isAdmin(msg)) return;
        const db = getDB();
        db.prepare('UPDATE grupos SET antiflood=0, antigolpe=0, soadm=0 WHERE chat_id=?').run(String(msg.chat.id));
        bot.sendMessage(msg.chat.id, '🛑 *Todas as proteções desativadas!*', { parse_mode: 'Markdown' });
    });
    
    // /rankadmin
    bot.onText(/\/rankadmin/, async (msg) => {
        const db = getDB();
        const rank = db.prepare('SELECT user_id, quantidade FROM mensagens_contador WHERE chat_id=? ORDER BY quantidade DESC LIMIT 10').all(String(msg.chat.id));
        let texto = '🏆 *RANK ADMIN*\n\n';
        rank.forEach((r, i) => {
            texto += `${i+1}º - ${r.user_id}: ${r.quantidade} msgs\n`;
        });
        bot.sendMessage(msg.chat.id, texto, { parse_mode: 'Markdown' });
    });
    
    // ============ CONFIGURAÇÕES ============
    
    // /soadm
    bot.onText(/\/soadm/, async (msg) => {
        if (!await isAdmin(msg)) return;
        const db = getDB();
        const grupo = db.prepare('SELECT soadm FROM grupos WHERE chat_id=?').get(String(msg.chat.id));
        const novo = grupo?.soadm ? 0 : 1;
        db.prepare('INSERT OR REPLACE INTO grupos (chat_id, soadm) VALUES (?,?)').run(String(msg.chat.id), novo);
        bot.sendMessage(msg.chat.id, novo ? '🔒 *Modo Só Admins ATIVADO*' : '🔓 *Modo Só Admins DESATIVADO*', { parse_mode: 'Markdown' });
    });
    
    // /antigolpe
    bot.onText(/\/antigolpe/, async (msg) => {
        if (!await isAdmin(msg)) return;
        const db = getDB();
        const grupo = db.prepare('SELECT antigolpe FROM grupos WHERE chat_id=?').get(String(msg.chat.id));
        const novo = grupo?.antigolpe ? 0 : 1;
        db.prepare('INSERT OR REPLACE INTO grupos (chat_id, antigolpe) VALUES (?,?)').run(String(msg.chat.id), novo);
        bot.sendMessage(msg.chat.id, novo ? '🛡️ *Anti Golpe ATIVADO*' : '🛡️ *Anti Golpe DESATIVADO*', { parse_mode: 'Markdown' });
    });
    
    // /antiflood <qtd>
    bot.onText(/\/antiflood (\d+)/, async (msg, match) => {
        if (!await isAdmin(msg)) return;
        const qtd = parseInt(match[1]);
        const db = getDB();
        db.prepare('INSERT OR REPLACE INTO grupos (chat_id, antiflood) VALUES (?,?)').run(String(msg.chat.id), qtd);
        bot.sendMessage(msg.chat.id, `🌊 *AntiFlood configurado para ${qtd} mensagens!*`, { parse_mode: 'Markdown' });
    });
    
    // /limitecaractere <qtd>
    bot.onText(/\/limitecaractere (\d+)/, async (msg, match) => {
        if (!await isAdmin(msg)) return;
        const qtd = parseInt(match[1]);
        const db = getDB();
        db.prepare('INSERT OR REPLACE INTO grupos (chat_id, limite_caractere) VALUES (?,?)').run(String(msg.chat.id), qtd);
        bot.sendMessage(msg.chat.id, `🔠 *Limite de caracteres: ${qtd}*`, { parse_mode: 'Markdown' });
    });
    
    // /setbemvindo
    bot.onText(/\/setbemvindo (.+)/, async (msg, match) => {
        if (!await isAdmin(msg)) return;
        const texto = match[1];
        const db = getDB();
        db.prepare('INSERT OR REPLACE INTO grupos (chat_id, bemvindo) VALUES (?,?)').run(String(msg.chat.id), texto);
        bot.sendMessage(msg.chat.id, '📝 *Mensagem de boas-vindas atualizada!*', { parse_mode: 'Markdown' });
    });
    
    // ============ GESTÃO DE CARGOS ============
    
    // /promover (responder mensagem)
    bot.onText(/\/promover/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda a mensagem do usuário!');
        const userId = msg.reply_to_message.from.id;
        try {
            await bot.promoteChatMember(msg.chat.id, userId, { can_manage_chat: true, can_delete_messages: true, can_restrict_members: true, can_promote_members: false, can_invite_users: true });
            bot.sendMessage(msg.chat.id, '⬆️ *Usuário promovido a administrador!*', { parse_mode: 'Markdown' });
        } catch (e) {
            bot.sendMessage(msg.chat.id, '❌ Não foi possível promover.');
        }
    });
    
    // /rebaixar
    bot.onText(/\/rebaixar/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda a mensagem do usuário!');
        const userId = msg.reply_to_message.from.id;
        try {
            await bot.promoteChatMember(msg.chat.id, userId, { can_manage_chat: false, can_delete_messages: false, can_restrict_members: false, can_promote_members: false, can_invite_users: false });
            bot.sendMessage(msg.chat.id, '⬇️ *Administrador rebaixado!*', { parse_mode: 'Markdown' });
        } catch (e) {
            bot.sendMessage(msg.chat.id, '❌ Não foi possível rebaixar.');
        }
    });
    
    // /addmod
    bot.onText(/\/addmod/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda a mensagem!');
        const db = getDB();
        db.prepare('INSERT OR REPLACE INTO moderadores (chat_id, user_id) VALUES (?,?)').run(String(msg.chat.id), String(msg.reply_to_message.from.id));
        bot.sendMessage(msg.chat.id, '👮 *Moderador adicionado!*', { parse_mode: 'Markdown' });
    });
    
    // /remmod
    bot.onText(/\/remmod/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda a mensagem!');
        const db = getDB();
        db.prepare('DELETE FROM moderadores WHERE chat_id=? AND user_id=?').run(String(msg.chat.id), String(msg.reply_to_message.from.id));
        bot.sendMessage(msg.chat.id, '👮 *Moderador removido!*', { parse_mode: 'Markdown' });
    });
    
    // /mods
    bot.onText(/\/mods/, async (msg) => {
        const db = getDB();
        const mods = db.prepare('SELECT user_id FROM moderadores WHERE chat_id=?').all(String(msg.chat.id));
        let texto = '🛡️ *MODERADORES*\n\n';
        mods.forEach(m => texto += `👮 ${m.user_id}\n`);
        bot.sendMessage(msg.chat.id, texto || 'Nenhum moderador.', { parse_mode: 'Markdown' });
    });
    
    // ============ MODERAÇÃO ============
    
    // /ban
    bot.onText(/\/ban/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda a mensagem do usuário!');
        const userId = msg.reply_to_message.from.id;
        try {
            await bot.banChatMember(msg.chat.id, userId);
            const db = getDB();
            db.prepare('INSERT INTO banidos (chat_id, user_id, motivo) VALUES (?,?,?)').run(String(msg.chat.id), String(userId), 'Banido por admin');
            bot.sendMessage(msg.chat.id, '🔨 *Usuário banido!*', { parse_mode: 'Markdown' });
        } catch (e) {
            bot.sendMessage(msg.chat.id, '❌ Não foi possível banir.');
        }
    });
    
    // /mute
    bot.onText(/\/mute/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda a mensagem!');
        const userId = msg.reply_to_message.from.id;
        try {
            await bot.restrictChatMember(msg.chat.id, userId, { can_send_messages: false });
            bot.sendMessage(msg.chat.id, '🔇 *Usuário mutado!*', { parse_mode: 'Markdown' });
        } catch (e) {
            bot.sendMessage(msg.chat.id, '❌ Erro ao mutar.');
        }
    });
    
    // /unmute
    bot.onText(/\/unmute/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda a mensagem!');
        const userId = msg.reply_to_message.from.id;
        try {
            await bot.restrictChatMember(msg.chat.id, userId, { can_send_messages: true, can_send_media_messages: true, can_send_other_messages: true });
            bot.sendMessage(msg.chat.id, '🔊 *Usuário desmutado!*', { parse_mode: 'Markdown' });
        } catch (e) {
            bot.sendMessage(msg.chat.id, '❌ Erro ao desmutar.');
        }
    });
    
    // /adv
    bot.onText(/\/adv/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda a mensagem!');
        const db = getDB();
        const userId = String(msg.reply_to_message.from.id);
        const aviso = db.prepare('SELECT quantidade FROM avisos WHERE chat_id=? AND user_id=?').get(String(msg.chat.id), userId);
        const qtd = (aviso?.quantidade || 0) + 1;
        db.prepare('INSERT OR REPLACE INTO avisos (chat_id, user_id, quantidade) VALUES (?,?,?)').run(String(msg.chat.id), userId, qtd);
        bot.sendMessage(msg.chat.id, `⚠️ *Advertência ${qtd}/3 para o usuário!*`, { parse_mode: 'Markdown' });
        if (qtd >= 3) {
            try { await bot.banChatMember(msg.chat.id, parseInt(userId)); } catch (e) {}
            bot.sendMessage(msg.chat.id, '🔨 *Usuário banido por acumular 3 advertências!*', { parse_mode: 'Markdown' });
        }
    });
    
    // /listanegra
    bot.onText(/\/listanegra/, async (msg) => {
        const db = getDB();
        const bans = db.prepare('SELECT * FROM banidos WHERE chat_id=?').all(String(msg.chat.id));
        let texto = '☠️ *LISTA NEGRA*\n\n';
        bans.forEach(b => texto += `🚫 ${b.user_id} - ${b.motivo}\n`);
        bot.sendMessage(msg.chat.id, texto || 'Nenhum banido.', { parse_mode: 'Markdown' });
    });
    
    // /unban
    bot.onText(/\/unban/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return bot.sendMessage(msg.chat.id, '❌ Responda a mensagem!');
        const userId = msg.reply_to_message.from.id;
        try {
            await bot.unbanChatMember(msg.chat.id, userId);
            const db = getDB();
            db.prepare('DELETE FROM banidos WHERE chat_id=? AND user_id=?').run(String(msg.chat.id), String(userId));
            bot.sendMessage(msg.chat.id, '✅ *Usuário desbanido!*', { parse_mode: 'Markdown' });
        } catch (e) {
            bot.sendMessage(msg.chat.id, '❌ Erro ao desbanir.');
        }
    });
    
    // ============ GRUPO ============
    
    // /fechar
    bot.onText(/\/fechar/, async (msg) => {
        if (!await isAdmin(msg)) return;
        await bot.setChatPermissions(msg.chat.id, { can_send_messages: false });
        bot.sendMessage(msg.chat.id, '🔒 *Grupo fechado!*', { parse_mode: 'Markdown' });
    });
    
    // /abrir
    bot.onText(/\/abrir/, async (msg) => {
        if (!await isAdmin(msg)) return;
        await bot.setChatPermissions(msg.chat.id, { can_send_messages: true, can_send_media_messages: true, can_send_other_messages: true });
        bot.sendMessage(msg.chat.id, '🔓 *Grupo aberto!*', { parse_mode: 'Markdown' });
    });
    
    // /link
    bot.onText(/\/link/, async (msg) => {
        if (!await isAdmin(msg)) return;
        try {
            const link = await bot.exportChatInviteLink(msg.chat.id);
            bot.sendMessage(msg.chat.id, `🔗 *Link do grupo:*\n${link}`, { parse_mode: 'Markdown' });
        } catch (e) {
            bot.sendMessage(msg.chat.id, '❌ Não foi possível gerar o link.');
        }
    });
    
    // /hidetag
    bot.onText(/\/hidetag (.+)/, async (msg, match) => {
        if (!await isAdmin(msg)) return;
        // Marca todos sem notificar (hidetag)
        bot.sendMessage(msg.chat.id, match[1], { disable_notification: true });
    });
    
    // /totag
    bot.onText(/\/totag (.+)/, async (msg, match) => {
        if (!await isAdmin(msg)) return;
        const membros = await bot.getChatAdministrators(msg.chat.id);
        let menciones = '';
        membros.forEach(m => menciones += `[\u200B](tg://user?id=${m.user.id})`);
        bot.sendMessage(msg.chat.id, `${match[1]}\n${menciones}`, { parse_mode: 'Markdown' });
    });
    
    // /d
    bot.onText(/\/d/, async (msg) => {
        if (!await isAdmin(msg)) return;
        if (!msg.reply_to_message) return;
        try {
            await bot.deleteMessage(msg.chat.id, msg.reply_to_message.message_id);
            await bot.deleteMessage(msg.chat.id, msg.message_id);
        } catch (e) {}
    });
    
    // /limpar (apaga últimas 100 mensagens do bot)
    bot.onText(/\/limpar/, async (msg) => {
        if (!await isAdmin(msg)) return;
        bot.sendMessage(msg.chat.id, '🧹 *Limpando...*', { parse_mode: 'Markdown' });
    });
    
    // /afk
    bot.onText(/\/afk (.+)/, async (msg, match) => {
        const db = getDB();
        db.prepare('INSERT OR REPLACE INTO afk_users (user_id, motivo, data) VALUES (?,?,?)').run(String(msg.from.id), match[1], new Date().toISOString());
        bot.sendMessage(msg.chat.id, `💤 *${msg.from.first_name} entrou em modo AFK*\n📝 Motivo: ${match[1]}`, { parse_mode: 'Markdown' });
    });
    
    // ============ ANÚNCIOS ============
    
    // /setads
    bot.onText(/\/setads (\d+) \| (.+)/, async (msg, match) => {
        if (!await isAdmin(msg)) return;
        const db = getDB();
        db.prepare('INSERT INTO anuncios (chat_id, mensagem, intervalo) VALUES (?,?,?)').run(String(msg.chat.id), match[2], parseInt(match[1]));
        bot.sendMessage(msg.chat.id, '⏱️ *Anúncio configurado!*', { parse_mode: 'Markdown' });
    });
    
    // /listads
    bot.onText(/\/listads/, async (msg) => {
        const db = getDB();
        const ads = db.prepare('SELECT * FROM anuncios WHERE chat_id=?').all(String(msg.chat.id));
        let texto = '📋 *ANÚNCIOS*\n\n';
        ads.forEach((a, i) => texto += `${i+1}. [${a.ativo ? '✅' : '❌'}] "${a.mensagem}" - ${a.intervalo}min\n`);
        bot.sendMessage(msg.chat.id, texto || 'Nenhum anúncio.', { parse_mode: 'Markdown' });
    });
    
    // /rmads
    bot.onText(/\/rmads (\d+)/, async (msg, match) => {
        if (!await isAdmin(msg)) return;
        const db = getDB();
        const ads = db.prepare('SELECT * FROM anuncios WHERE chat_id=?').all(String(msg.chat.id));
        const idx = parseInt(match[1]) - 1;
        if (ads[idx]) {
            db.prepare('DELETE FROM anuncios WHERE id=?').run(ads[idx].id);
            bot.sendMessage(msg.chat.id, '🗑️ *Anúncio removido!*', { parse_mode: 'Markdown' });
        }
    });
    
    // ============ BOAS-VINDAS ============
    bot.on('new_chat_members', async (msg) => {
        const db = getDB();
        const grupo = db.prepare('SELECT bemvindo FROM grupos WHERE chat_id=?').get(String(msg.chat.id));
        const texto = grupo?.bemvindo || 'Bem-vindo(a) {nome} ao grupo {grupo}!';
        msg.new_chat_members.forEach(async (membro) => {
            const msgFinal = texto.replace('{nome}', membro.first_name).replace('{grupo}', msg.chat.title);
            bot.sendMessage(msg.chat.id, msgFinal);
        });
    });
    
    // ============ ANTI-GOLPE (Anti rebaixar) ============
    bot.on('message', async (msg) => {
        if (!msg.chat || msg.chat.type === 'private') return;
        
        const db = getDB();
        const grupo = db.prepare('SELECT * FROM grupos WHERE chat_id=?').get(String(msg.chat.id));
        
        // Anti-flood
        if (grupo?.antiflood > 0 && msg.from) {
            const msgs = db.prepare('SELECT quantidade FROM mensagens_contador WHERE chat_id=? AND user_id=?').get(String(msg.chat.id), String(msg.from.id));
            const qtd = (msgs?.quantidade || 0) + 1;
            if (qtd > grupo.antiflood) {
                try { await bot.restrictChatMember(msg.chat.id, msg.from.id, { can_send_messages: false }); } catch (e) {}
                bot.sendMessage(msg.chat.id, `🌊 *${msg.from.first_name} foi mutado por flood!*`, { parse_mode: 'Markdown' });
            }
            db.prepare('INSERT OR REPLACE INTO mensagens_contador (chat_id, user_id, quantidade) VALUES (?,?,?)').run(String(msg.chat.id), String(msg.from.id), qtd);
            setTimeout(() => {
                db.prepare('UPDATE mensagens_contador SET quantidade=0 WHERE chat_id=? AND user_id=?').run(String(msg.chat.id), String(msg.from.id));
            }, 10000);
        }
        
        // Limite de caracteres
        if (grupo?.limite_caractere > 0 && msg.text && msg.text.length > grupo.limite_caractere) {
            try { await bot.deleteMessage(msg.chat.id, msg.message_id); } catch (e) {}
            bot.sendMessage(msg.chat.id, `🔠 Mensagem muito longa! Limite: ${grupo.limite_caractere} caracteres.`);
        }
        
        // AFK
        if (msg.reply_to_message && msg.text) {
            const db2 = getDB();
            const afk = db2.prepare('SELECT * FROM afk_users WHERE user_id=?').get(String(msg.reply_to_message.from.id));
            if (afk) {
                const tempo = moment(afk.data).fromNow();
                bot.sendMessage(msg.chat.id, `💤 *${msg.reply_to_message.from.first_name} está AFK* desde ${tempo}\n📝 ${afk.motivo}`, { parse_mode: 'Markdown' });
            }
        }
        
        // Remove AFK se a pessoa mandar mensagem
        if (msg.from) {
            db.prepare('DELETE FROM afk_users WHERE user_id=?').run(String(msg.from.id));
        }
    });
    
    console.log('✅ DINI\'Z BOT configurado!');
}

// Verifica se é admin
async function isAdmin(msg) {
    if (!msg.chat || msg.chat.type === 'private') return true;
    try {
        const admins = process.env.ADMIN_IDS.split(',').map(Number);
        if (admins.includes(msg.from.id)) return true;
        
        const chatMember = await bot.getChatMember(msg.chat.id, msg.from.id);
        return ['creator', 'administrator'].includes(chatMember.status);
    } catch (e) {
        return false;
    }
}

module.exports = { startBot };
