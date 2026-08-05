from .connection import get_db

def criar_todas_tabelas():
    db = get_db()
    
    db.executescript('''
        -- CLIENTES
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            tipo TEXT DEFAULT 'PF',
            nome TEXT, sobrenome TEXT,
            cpf TEXT UNIQUE, cnpj TEXT UNIQUE,
            razao_social TEXT, nome_fantasia TEXT,
            inscricao_estadual TEXT, responsavel TEXT,
            data_nascimento TEXT, sexo TEXT,
            telefone TEXT, email TEXT, senha TEXT,
            saldo REAL DEFAULT 0,
            total_gasto REAL DEFAULT 0,
            pontos_fidelidade INTEGER DEFAULT 0,
            cashback REAL DEFAULT 0,
            afiliado_codigo TEXT UNIQUE,
            afiliado_id INTEGER,
            bloqueado INTEGER DEFAULT 0,
            etapa_cadastro TEXT DEFAULT 'inicio',
            codigo_verificacao TEXT,
            verificado INTEGER DEFAULT 0,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            ultimo_acesso DATETIME
        );

        -- ENDEREÇOS
        CREATE TABLE IF NOT EXISTS enderecos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            apelido TEXT DEFAULT 'Principal',
            cep TEXT, logradouro TEXT, numero TEXT,
            complemento TEXT, referencia TEXT,
            bairro TEXT, cidade TEXT, estado TEXT,
            latitude REAL, longitude REAL,
            principal INTEGER DEFAULT 0,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        );

        -- CATEGORIAS
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            emoji TEXT DEFAULT '📦',
            descricao TEXT,
            banner TEXT,
            cor TEXT DEFAULT '#6366f1',
            icone TEXT,
            ordem INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            destaque INTEGER DEFAULT 0,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- PRODUTOS
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria_id INTEGER,
            nome TEXT NOT NULL,
            descricao TEXT,
            marca TEXT,
            codigo_barras TEXT,
            sku TEXT,
            preco REAL NOT NULL,
            preco_promocional REAL,
            preco_clube REAL,
            estoque INTEGER DEFAULT 0,
            estoque_minimo INTEGER DEFAULT 5,
            unidade TEXT DEFAULT 'un',
            peso TEXT,
            foto TEXT,
            galeria TEXT,
            tipo TEXT DEFAULT 'fisico',
            destaque INTEGER DEFAULT 0,
            oculto INTEGER DEFAULT 0,
            disponivel INTEGER DEFAULT 1,
            limite_por_cliente INTEGER DEFAULT 0,
            ordem INTEGER DEFAULT 0,
            data_inicio_promocao DATETIME,
            data_fim_promocao DATETIME,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
        );

        -- CARRINHOS
        CREATE TABLE IF NOT EXISTS carrinhos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER DEFAULT 1,
            comentario TEXT,
            data_adicao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
            FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
        );

        -- FAVORITOS
        CREATE TABLE IF NOT EXISTS favoritos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            data DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(cliente_id, produto_id),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
            FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
        );

        -- PEDIDOS
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE NOT NULL,
            cliente_id INTEGER NOT NULL,
            endereco_id INTEGER,
            status TEXT DEFAULT 'recebido',
            subtotal REAL DEFAULT 0,
            taxa_entrega REAL DEFAULT 0,
            desconto REAL DEFAULT 0,
            total REAL DEFAULT 0,
            cupom TEXT,
            comentario TEXT,
            pagamento_metodo TEXT DEFAULT 'pix',
            pagamento_id TEXT,
            pagamento_status TEXT DEFAULT 'pendente',
            pagamento_qrcode TEXT,
            data_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_pagamento DATETIME,
            data_entrega DATETIME,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (endereco_id) REFERENCES enderecos(id)
        );

        -- ITENS DO PEDIDO
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            produto_id INTEGER,
            produto_nome TEXT NOT NULL,
            quantidade INTEGER DEFAULT 1,
            preco_unitario REAL NOT NULL,
            comentario TEXT,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
        );

        -- CUPONS
        CREATE TABLE IF NOT EXISTS cupons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            tipo TEXT DEFAULT 'percentual',
            valor REAL NOT NULL,
            valor_minimo REAL DEFAULT 0,
            uso_maximo INTEGER DEFAULT 100,
            uso_atual INTEGER DEFAULT 0,
            valido_ate DATETIME,
            ativo INTEGER DEFAULT 1,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- CUPONS USADOS
        CREATE TABLE IF NOT EXISTS cupons_usados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            cupom_id INTEGER NOT NULL,
            pedido_id INTEGER,
            data DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (cupom_id) REFERENCES cupons(id)
        );

        -- AFILIADOS
        CREATE TABLE IF NOT EXISTS afiliados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER UNIQUE,
            codigo TEXT UNIQUE NOT NULL,
            comissao_percentual REAL DEFAULT 5,
            total_indicacoes INTEGER DEFAULT 0,
            total_comissoes REAL DEFAULT 0,
            saldo_comissao REAL DEFAULT 0,
            nivel INTEGER DEFAULT 1,
            ativo INTEGER DEFAULT 1,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );

        -- COMISSÕES
        CREATE TABLE IF NOT EXISTS comissoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            afiliado_id INTEGER NOT NULL,
            pedido_id INTEGER,
            valor REAL NOT NULL,
            status TEXT DEFAULT 'pendente',
            data DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (afiliado_id) REFERENCES afiliados(id)
        );

        -- RECARGAS
        CREATE TABLE IF NOT EXISTS recargas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            valor REAL NOT NULL,
            payment_id TEXT,
            status TEXT DEFAULT 'pendente',
            data DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );

        -- NOTIFICAÇÕES
        CREATE TABLE IF NOT EXISTS notificacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            tipo TEXT DEFAULT 'info',
            titulo TEXT NOT NULL,
            mensagem TEXT,
            lida INTEGER DEFAULT 0,
            data DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        );

        -- ALERTAS DE ESTOQUE
        CREATE TABLE IF NOT EXISTS alertas_estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            notificado INTEGER DEFAULT 0,
            data DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(cliente_id, produto_id),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
            FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
        );

        -- CONFIGURAÇÕES
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT UNIQUE NOT NULL,
            valor TEXT,
            tipo TEXT DEFAULT 'texto',
            categoria TEXT DEFAULT 'geral',
            descricao TEXT,
            data_modificacao DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- BOTÕES DO MENU
        CREATE TABLE IF NOT EXISTS botoes_menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            menu TEXT NOT NULL,
            texto TEXT NOT NULL,
            emoji TEXT,
            callback_data TEXT,
            url TEXT,
            webapp_url TEXT,
            ordem INTEGER DEFAULT 0,
            linha INTEGER DEFAULT 1,
            admin_only INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            data_modificacao DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- MENSAGENS DO BOT
        CREATE TABLE IF NOT EXISTS mensagens_bot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT UNIQUE NOT NULL,
            tipo TEXT DEFAULT 'texto',
            conteudo TEXT NOT NULL,
            parse_mode TEXT DEFAULT 'Markdown',
            variaveis TEXT,
            data_modificacao DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- BANNERS
        CREATE TABLE IF NOT EXISTS banners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            imagem TEXT NOT NULL,
            url TEXT,
            ordem INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            data_inicio DATETIME,
            data_fim DATETIME
        );

        -- LOGS DO SISTEMA
        CREATE TABLE IF NOT EXISTS logs_sistema (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            acao TEXT NOT NULL,
            modulo TEXT,
            detalhes TEXT,
            valor_antigo TEXT,
            valor_novo TEXT,
            ip TEXT,
            data DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- ADMINISTRADORES
        CREATE TABLE IF NOT EXISTS administradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            nome TEXT,
            cargo TEXT DEFAULT 'admin',
            permissoes TEXT DEFAULT 'all',
            ativo INTEGER DEFAULT 1,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- AVALIAÇÕES
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            produto_id INTEGER,
            pedido_id INTEGER,
            nota INTEGER CHECK(nota >= 1 AND nota <= 5),
            comentario TEXT,
            data DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );

        -- DISPOSITIVOS
        CREATE TABLE IF NOT EXISTS dispositivos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            token TEXT,
            plataforma TEXT,
            ultimo_acesso DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        );
    ''')
    db.commit()
    print('✅ Todas as tabelas criadas')
