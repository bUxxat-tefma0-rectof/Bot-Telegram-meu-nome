from database.connection import get_db
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class CupomModel:
    
    @staticmethod
    def get_by_codigo(codigo: str) -> Optional[Dict]:
        db = get_db()
        row = db.execute('SELECT * FROM cupons WHERE codigo = ?', (codigo.upper(),)).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_id(cupom_id: int) -> Optional[Dict]:
        db = get_db()
        row = db.execute('SELECT * FROM cupons WHERE id = ?', (cupom_id,)).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def criar(dados: Dict) -> Dict:
        db = get_db()
        try:
            valido_ate = None
            if dados.get('dias_validade'):
                valido_ate = (datetime.now() + timedelta(days=int(dados['dias_validade']))).isoformat()
            
            cursor = db.execute('''
                INSERT INTO cupons (codigo, tipo, valor, valor_minimo, uso_maximo, uso_atual, valido_ate, ativo)
                VALUES (?, ?, ?, ?, ?, 0, ?, 1)
            ''', (
                dados['codigo'].upper(),
                dados.get('tipo', 'percentual'),
                float(dados['valor']),
                float(dados.get('valor_minimo', 0)),
                int(dados.get('uso_maximo', 100)),
                valido_ate
            ))
            db.commit()
            return {'sucesso': True, 'id': cursor.lastrowid, 'mensagem': f'Cupom {dados["codigo"].upper()} criado!'}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def validar(codigo: str, valor_compra: float = 0) -> Dict:
        cupom = CupomModel.get_by_codigo(codigo)
        
        if not cupom:
            return {'valido': False, 'mensagem': 'Cupom não encontrado'}
        if not cupom['ativo']:
            return {'valido': False, 'mensagem': 'Cupom desativado'}
        if cupom['uso_atual'] >= cupom['uso_maximo']:
            return {'valido': False, 'mensagem': 'Cupom esgotado'}
        if cupom['valido_ate'] and datetime.fromisoformat(cupom['valido_ate']) < datetime.now():
            return {'valido': False, 'mensagem': 'Cupom vencido'}
        if valor_compra < cupom['valor_minimo']:
            return {'valido': False, 'mensagem': f'Valor mínimo de compra: R$ {cupom["valor_minimo"]:.2f}'}
        
        return {'valido': True, 'cupom': cupom}
    
    @staticmethod
    def calcular_desconto(cupom: Dict, valor_compra: float) -> float:
        if cupom['tipo'] == 'percentual':
            desconto = valor_compra * (cupom['valor'] / 100)
        else:
            desconto = min(cupom['valor'], valor_compra)
        return round(desconto, 2)
    
    @staticmethod
    def usar(cupom_id: int, cliente_id: int, pedido_id: int = None) -> bool:
        db = get_db()
        db.execute('UPDATE cupons SET uso_atual = uso_atual + 1 WHERE id = ? AND uso_atual < uso_maximo',
                   (cupom_id,))
        db.execute('''
            INSERT INTO cupons_usados (cliente_id, cupom_id, pedido_id, data)
            VALUES (?, ?, ?, datetime('now'))
        ''', (cliente_id, cupom_id, pedido_id))
        db.commit()
        return True
    
    @staticmethod
    def toggle(cupom_id: int) -> bool:
        db = get_db()
        c = db.execute('SELECT ativo FROM cupons WHERE id = ?', (cupom_id,)).fetchone()
        if not c:
            return False
        novo = 0 if c['ativo'] else 1
        db.execute('UPDATE cupons SET ativo = ? WHERE id = ?', (novo, cupom_id))
        db.commit()
        return True
    
    @staticmethod
    def excluir(cupom_id: int) -> bool:
        db = get_db()
        db.execute('DELETE FROM cupons WHERE id = ?', (cupom_id,))
        db.commit()
        return True
    
    @staticmethod
    def listar_ativos() -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute(
            "SELECT * FROM cupons WHERE ativo = 1 AND uso_atual < uso_maximo AND (valido_ate IS NULL OR valido_ate > datetime('now')) ORDER BY id DESC"
        ).fetchall()]
    
    @staticmethod
    def listar_todos() -> List[Dict]:
        db = get_db()
        return [dict(r) for r in db.execute('SELECT * FROM cupons ORDER BY id DESC').fetchall()]
    
    @staticmethod
    def gerar_lote(prefixo: str, quantidade: int, tipo: str, valor: float, 
                   uso_maximo: int = 1, dias_validade: int = 30) -> List[str]:
        db = get_db()
        cupons_gerados = []
        valido_ate = (datetime.now() + timedelta(days=dias_validade)).isoformat()
        
        for i in range(quantidade):
            codigo = f"{prefixo.upper()}{str(i+1).zfill(4)}"
            try:
                db.execute('''
                    INSERT INTO cupons (codigo, tipo, valor, uso_maximo, valido_ate)
                    VALUES (?, ?, ?, ?, ?)
                ''', (codigo, tipo, valor, uso_maximo, valido_ate))
                cupons_gerados.append(codigo)
            except:
                continue
        
        db.commit()
        return cupons_gerados
