const Database = require('better-sqlite3');
const path = require('path');

const db = new Database(path.join(__dirname, '..', 'dinizbot.db'));
db.pragma('journal_mode = WAL');

function initDB() {
    db.exec(`
        CREATE TABLE IF NOT EXISTS grupos (
            chat_id TEXT PRIMARY KEY,
            nome TEXT,
            bemvindo TEXT DEFAULT 'Bem-vindo(a) {nome} ao grupo {grupo}!',
            antiflood INTEGER DEFAULT 5,
            limite_caractere INTEGER DEFAULT 0,
            fechado INTEGER DEFAULT 0,
            soadm INTEGER DEFAULT 0,
            antigolpe INTEGER DEFAULT 1,
            sistema_gold INTEGER DEFAULT 0,
            prefixo TEXT DEFAULT '/'
        );
        
        CREATE TABLE IF NOT EXISTS admins_dono (
            chat_id TEXT,
            user_id TEXT,
            PRIMARY KEY (chat_id, user_id)
        );
        
        CREATE TABLE IF NOT EXISTS moderadores (
            chat_id TEXT,
            user_id TEXT,
            PRIMARY KEY (chat_id, user_id)
        );
        
        CREATE TABLE IF NOT EXISTS banidos (
            chat_id TEXT,
            user_id TEXT,
            motivo TEXT,
            data DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS mutados (
            chat_id TEXT,
            user_id TEXT,
            data_fim DATETIME
        );
        
        CREATE TABLE IF NOT EXISTS avisos (
            chat_id TEXT,
            user_id TEXT,
            quantidade INTEGER DEFAULT 0
        );
        
        CREATE TABLE IF NOT EXISTS palavras_proibidas (
            chat_id TEXT,
            palavra TEXT
        );
        
        CREATE TABLE IF NOT EXISTS anuncios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            mensagem TEXT,
            intervalo INTEGER DEFAULT 30,
            ativo INTEGER DEFAULT 1
        );
        
        CREATE TABLE IF NOT EXISTS mensagens_contador (
            chat_id TEXT,
            user_id TEXT,
            quantidade INTEGER DEFAULT 0
        );
        
        CREATE TABLE IF NOT EXISTS afk_users (
            user_id TEXT,
            motivo TEXT,
            data DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    `);
    
    console.log('✅ Banco de dados pronto');
}

function getDB() { return db; }

module.exports = { initDB, getDB };
