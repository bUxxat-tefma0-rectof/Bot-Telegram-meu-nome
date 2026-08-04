// /notag - Marca sem notificar
async function noTag(bot, msg, match) {
    if (!await isAdmin(msg)) return;
    const texto = match[1];
    await bot.sendMessage(msg.chat.id, texto, { disable_notification: true });
}

// /notag2 - Marca invisível
async function noTag2(bot, msg, match) {
    if (!await isAdmin(msg)) return;
    const texto = match[1];
    await bot.sendMessage(msg.chat.id, `${texto}\n\u200B`, { disable_notification: true });
}

async function isAdmin(msg) {
    try {
        const admins = process.env.ADMIN_IDS.split(',').map(Number);
        return admins.includes(msg.from.id);
    } catch (e) { return false; }
}

module.exports = { noTag, noTag2 };
