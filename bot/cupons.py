from database.connection import get_db
from datetime import datetime

class CuponsService:
    
    @staticmethod
    def listar_disponiveis() -> list:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT * FROM cupons WHERE ativo = 1 AND uso_atual < uso_maximo AND (valido_ate IS NULL OR valido_ate > datetime('now')) ORDER BY id DESC"
        ).fetchall()]
    
    @staticmethod
    def validar(codigo: str) -> dict:
        db = get_db()
        cupom = db.execute('SELECT * FROM cupons WHERE codigo = ? AND ativo = 1', (codigo.upper(),)).fetchone()
        
        if not cupom:
            return {'valido': False, 'mensagem': 'Cupom não encontrado'}
        if cupom['uso_atual'] >= cupom['uso_maximo']:
            return {'valido': False, 'mensagem': 'Cupom esgotado'}
        if cupom['valido_ate'] and datetime.fromisoformat(cupom['valido_ate']) < datetime.now():
            return {'valido': False, 'mensagem': 'Cupom vencido'}
        
        return {'valido': True, 'cupom': dict(cupom)}
    
    @staticmethod
    def aplicar(user_id: int, codigo: str) -> dict:
        validacao = CuponsService.validar(codigo)
        if not validacao['valido']:
            return {'sucesso': False, 'mensagem': validacao['mensagem']}
        
        cupom = validacao['cupom']
        tipo = 'percentual' if cupom['tipo'] == 'percentual' else 'fixo'
        valor = f"{cupom['valor']}%" if tipo == 'percentual' else f"R$ {cupom['valor']}"
        
        return {
            'sucesso': True,
            'cupom': cupom,
            'mensagem': f'Cupom {cupom["codigo"]} aplicado! Desconto: {valor}'
        }
