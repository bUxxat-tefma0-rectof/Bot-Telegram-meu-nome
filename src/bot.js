const { addPrefix, listPrefixes, remPrefix } = require('./comandos/multiprefixo');
const { figAdv, delFigAdv, figDel, delFigDel } = require('./comandos/fig_adv_del');

// No startBot(), adiciona:

// ============ MULTIPREFIXO ============
bot.onText(/\/addprefix (.+)/, (msg, m) => addPrefix(bot, msg, m));
bot.onText(/\/multiprefixo/, (msg) => listPrefixes(bot, msg));
bot.onText(/\/remprefix (.+)/, (msg, m) => remPrefix(bot, msg, m));

// ============ FIG ADV/DEL ============
bot.onText(/\/figadv/, (msg) => figAdv(bot, msg));
bot.onText(/\/delfigadv/, (msg) => delFigAdv(bot, msg));
bot.onText(/\/figdel/, (msg) => figDel(bot, msg));
bot.onText(/\/delfigdel/, (msg) => delFigDel(bot, msg));

// ============ DETECTOR DE FIGURINHAS ============
bot.on('message', async (msg) => {
    if (msg.sticker && msg.chat.type !== 'private') {
        const db = getDB();
        const hash = msg.sticker.file_unique_id;
        
        // Verifica se é figurinha proibida
        const proibida = db.prepare('SELECT * FROM figurinhas_proibidas WHERE grupo_id=? AND hash=?').get(String(msg.chat.id), hash);
        if (proibida) {
            try { await bot.deleteMessage(msg.chat.id, msg.message_id); } catch (e) {}
            return;
        }
        
        // Verifica se é figurinha de advertência
        const adv = db.prepare('SELECT * FROM fig_adv WHERE grupo_id=? AND hash=?').get(String(msg.chat.id), hash);
        if (adv) {
            const userId = String(msg.from.id);
            const aviso = db.prepare('SELECT quantidade FROM avisos WHERE chat_id=? AND user_id=?').get(String(msg.chat.id), userId);
            const qtd = (aviso?.quantidade || 0) + 1;
            db.prepare('INSERT OR REPLACE INTO avisos (chat_id, user_id, quantidade) VALUES (?,?,?)').run(String(msg.chat.id), userId, qtd);
            bot.sendMessage(msg.chat.id, `⚠️ *${msg.from.first_name} advertido por figurinha! (${qtd}/3)*`, { parse_mode: 'Markdown' });
            if (qtd >= 3) {
                try { await bot.banChatMember(msg.chat.id, msg.from.id); } catch (e) {}
            }
            return;
        }
        
        // Verifica se é figurinha de deletar
        const del = db.prepare('SELECT * FROM fig_del WHERE grupo_id=? AND hash=?').get(String(msg.chat.id), hash);
        if (del) {
            try { await bot.deleteMessage(msg.chat.id, msg.message_id); } catch (e) {}
            return;
        }
    }
});
