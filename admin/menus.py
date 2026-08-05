from database.connection import get_db

class MenusAdmin:
    
    @staticmethod
    def listar() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT DISTINCT menu, COUNT(*) as total_botoes FROM botoes_menu GROUP BY menu ORDER BY menu'
        ).fetchall()]
    
    @staticmethod
    def criar_menu(nome: str) -> dict:
        db = get_db()
        existe = db.execute('SELECT DISTINCT menu FROM botoes_menu WHERE menu = ?', (nome,)).fetchone()
        if existe:
            return {'sucesso': False, 'mensagem': 'Menu já existe'}
        
        # Cria botão voltar padrão
        db.execute('''
            INSERT INTO botoes_menu (menu, texto, emoji, callback_data, ordem, linha)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nome, 'Voltar', '⬅️', 'menu_principal', 99, 1))
        db.commit()
        return {'sucesso': True, 'mensagem': f'Menu {nome} criado!'}
    
    @staticmethod
    def excluir_menu(nome: str) -> dict:
        if nome == 'principal':
            return {'sucesso': False, 'mensagem': 'Não pode excluir o menu principal'}
        db = get_db()
        db.execute('DELETE FROM botoes_menu WHERE menu = ?', (nome,))
        db.commit()
        return {'sucesso': True, 'mensagem': f'Menu {nome} excluído!'}
    
    @staticmethod
    def get_botoes_menu(nome: str) -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            'SELECT * FROM botoes_menu WHERE menu = ? AND ativo = 1 ORDER BY linha, ordem', (nome,)
        ).fetchall()]
