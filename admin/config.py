from database.connection import get_db

class ConfigAdmin:
    
    @staticmethod
    def get_todas() -> dict:
        db = get_db()
        configs = db.execute('SELECT * FROM configuracoes ORDER BY categoria, chave').fetchall()
        resultado = {}
        for c in configs:
            if c['categoria'] not in resultado:
                resultado[c['categoria']] = {}
            resultado[c['categoria']][c['chave']] = {
                'valor': c['valor'],
                'tipo': c['tipo'],
                'descricao': c['descricao']
            }
        return resultado
    
    @staticmethod
    def get_por_categoria(categoria: str) -> dict:
        db = get_db()
        configs = db.execute('SELECT * FROM configuracoes WHERE categoria = ?', (categoria,)).fetchall()
        return {c['chave']: c['valor'] for c in configs}
    
    @staticmethod
    def salvar(chave: str, valor: str) -> dict:
        db = get_db()
        existe = db.execute('SELECT * FROM configuracoes WHERE chave = ?', (chave,)).fetchone()
        if existe:
            db.execute('UPDATE configuracoes SET valor = ?, data_modificacao = datetime("now") WHERE chave = ?',
                       (str(valor), chave))
        else:
            db.execute('INSERT INTO configuracoes (chave, valor) VALUES (?, ?)', (chave, str(valor)))
        db.commit()
        return {'sucesso': True, 'mensagem': 'Configuração salva!'}
    
    @staticmethod
    def salvar_varias(configs: dict) -> dict:
        for chave, valor in configs.items():
            ConfigAdmin.salvar(chave, valor)
        return {'sucesso': True, 'mensagem': f'{len(configs)} configurações salvas!'}
    
    @staticmethod
    def get_valor(chave: str, default: str = '') -> str:
        db = get_db()
        row = db.execute('SELECT valor FROM configuracoes WHERE chave = ?', (chave,)).fetchone()
        return row['valor'] if row else default
    
    @staticmethod
    def resetar_padrao() -> dict:
        db = get_db()
        db.execute('DELETE FROM configuracoes')
        
        from database.seed import inserir_dados_padrao
        inserir_dados_padrao()
        
        return {'sucesso': True, 'mensagem': 'Configurações restauradas para o padrão!'}
