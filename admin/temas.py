from database.connection import get_db

class TemasAdmin:
    
    @staticmethod
    def get_tema_atual() -> dict:
        db = get_db()
        configs = db.execute("SELECT * FROM configuracoes WHERE categoria = 'aparencia'").fetchall()
        tema = {c['chave']: c['valor'] for c in configs}
        
        return {
            'tema': tema.get('tema', 'light'),
            'cores': {
                'primaria': tema.get('cor_primaria', '#6366f1'),
                'secundaria': tema.get('cor_secundaria', '#ec4899'),
                'fundo': tema.get('cor_fundo', '#f8fafc'),
                'texto': tema.get('cor_texto', '#1e293b'),
                'texto_claro': tema.get('cor_texto_claro', '#64748b'),
                'borda': tema.get('cor_borda', '#e2e8f0'),
                'sucesso': tema.get('cor_sucesso', '#10b981'),
                'erro': tema.get('cor_erro', '#ef4444'),
                'aviso': tema.get('cor_aviso', '#f59e0b')
            }
        }
    
    @staticmethod
    def salvar_tema(dados: dict) -> dict:
        db = get_db()
        
        for chave, valor in dados.items():
            existe = db.execute('SELECT * FROM configuracoes WHERE chave = ?', (chave,)).fetchone()
            if existe:
                db.execute('UPDATE configuracoes SET valor = ? WHERE chave = ?', (str(valor), chave))
            else:
                db.execute("INSERT INTO configuracoes (chave, valor, categoria) VALUES (?, ?, 'aparencia')",
                          (chave, str(valor)))
        db.commit()
        return {'sucesso': True, 'mensagem': 'Tema atualizado!'}
    
    @staticmethod
    def get_temas_predefinidos() -> list:
        return [
            {
                'id': 'default',
                'nome': 'Padrão',
                'cores': {
                    'primaria': '#6366f1', 'secundaria': '#ec4899',
                    'fundo': '#f8fafc', 'texto': '#1e293b'
                }
            },
            {
                'id': 'dark',
                'nome': 'Escuro',
                'cores': {
                    'primaria': '#818cf8', 'secundaria': '#f472b6',
                    'fundo': '#0f172a', 'texto': '#e2e8f0'
                }
            },
            {
                'id': 'ocean',
                'nome': 'Oceano',
                'cores': {
                    'primaria': '#0ea5e9', 'secundaria': '#06b6d4',
                    'fundo': '#f0f9ff', 'texto': '#0c4a6e'
                }
            },
            {
                'id': 'forest',
                'nome': 'Floresta',
                'cores': {
                    'primaria': '#10b981', 'secundaria': '#34d399',
                    'fundo': '#f0fdf4', 'texto': '#14532d'
                }
            },
            {
                'id': 'sunset',
                'nome': 'Pôr do Sol',
                'cores': {
                    'primaria': '#f59e0b', 'secundaria': '#ef4444',
                    'fundo': '#fffbeb', 'texto': '#78350f'
                }
            }
        ]
