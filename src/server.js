require('dotenv').config();
const express = require('express');
const { initDB } = require('./database');
const { startBot } = require('./bot');

const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
    res.json({ status: 'online', bot: '🤖 DINI\'Z BOT' });
});

async function main() {
    initDB();
    console.log('🤖 Iniciando DINI\'Z BOT...');
    await startBot();
    
    app.listen(PORT, () => {
        console.log(`🌐 Porta ${PORT}`);
        console.log('✅ DINI\'Z BOT pronto!');
    });
}

main().catch(console.error);
