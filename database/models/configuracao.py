from database.connection import get_db
from typing import Dict, Optional, Any
import json

class ConfiguracaoModel:
    
    @staticmethod
    def get(chave: str, default: Any = None) -> Optional[str]:
        db = get_db()
        row = db.execute('SELECT valor FROM configuracoes WHERE chave = ?', (chave,)).fetchone()
        return row['valor'] if row else default
    
    @staticmethod
    def get_int(chave: str, default: int = 0) -> int:
        valor = ConfiguracaoModel.get(chave)
        return int(valor) if valor and valor.isdigit() else default
    
    @staticmethod
    def get_float(chave: str, default: float = 0.0) -> float:
        valor = ConfiguracaoModel.get(chave)
        try:
            return float(valor) if valor else default
        except:
            return default
    
    @staticmethod
    def get_bool(chave: str, default: bool = False) -> bool:
        valor = ConfiguracaoModel.get(chave)
        return valor == '1' or valor == 'true' if valor else default
    
    @staticmethod
    def set(chave: str, valor: Any) -> bool:
        db = get_db()
        valor_str = str(valor)
        
        existe = db.execute('SELECT * FROM configuracoes WHERE chave = ?', (chave,)).fetchone()
        if existe:
            db.execute('UPDATE configuracoes SET valor = ?, data_modificacao = datetime("now") WHERE chave = ?',
                       (valor_str, chave))
        else:
            db.execute('INSERT INTO configuracoes (chave, valor, data_modificacao) VALUES (?, ?, datetime("now"))',
                       (chave, valor_str))
        db.commit()
        return True
    
    @staticmethod
    def set_varias(configs: Dict[str, Any]) -> bool:
        for chave, valor in configs.items():
            ConfiguracaoModel.set(chave, valor)
        return True
    
    @staticmethod
    def get_todas() -> Dict[str, Dict]:
        db = get_db()
        rows = db.execute('SELECT * FROM configuracoes ORDER BY categoria, chave').fetchall()
        resultado = {}
        for r in rows:
            cat = r['categoria'] or 'geral'
            if cat not in resultado:
                resultado[cat] = {}
            resultado[cat][r['chave']] = {
                'valor': r['valor'],
                'tipo': r['tipo'] or 'texto',
                'descricao': r['descricao'] or ''
            }
        return resultado
    
    @staticmethod
    def get_por_categoria(categoria: str) -> Dict[str, str]:
        db = get_db()
        rows = db.execute('SELECT * FROM configuracoes WHERE categoria = ?', (categoria,)).fetchall()
        return {r['chave']: r['valor'] for r in rows}
    
    @staticmethod
    def get_tema() -> Dict:
        return {
            'tema': ConfiguracaoModel.get('tema', 'light'),
            'cores': {
                'primaria': ConfiguracaoModel.get('cor_primaria', '#6366f1'),
                'secundaria': ConfiguracaoModel.get('cor_secundaria', '#ec4899'),
                'fundo': ConfiguracaoModel.get('cor_fundo', '#f8fafc'),
                'texto': ConfiguracaoModel.get('cor_texto', '#1e293b'),
                'texto_claro': ConfiguracaoModel.get('cor_texto_claro', '#64748b'),
                'borda': ConfiguracaoModel.get('cor_borda', '#e2e8f0'),
                'sucesso': ConfiguracaoModel.get('cor_sucesso', '#10b981'),
                'erro': ConfiguracaoModel.get('cor_erro', '#ef4444'),
                'aviso': ConfiguracaoModel.get('cor_aviso', '#f59e0b')
            }
        }
    
    @staticmethod
    def get_pagamentos() -> Dict:
        return {
            'pedido_minimo': ConfiguracaoModel.get_float('pedido_minimo', 10),
            'taxa_entrega': ConfiguracaoModel.get_float('taxa_entrega', 5),
            'tempo_expiracao_pix': ConfiguracaoModel.get_int('tempo_expiracao_pix', 30),
            'gateway_ativo': ConfiguracaoModel.get('gateway_ativo', 'mercadopago'),
            'aprovacao_automatica': ConfiguracaoModel.get_bool('aprovacao_automatica', True)
        }
    
    @staticmethod
    def get_afiliados() -> Dict:
        return {
            'comissao_padrao': ConfiguracaoModel.get_float('comissao_padrao', 5),
            'minimo_saque': ConfiguracaoModel.get_float('minimo_saque', 50),
            'prazo_saque': ConfiguracaoModel.get_int('prazo_saque', 7)
        }
    
    @staticmethod
    def get_loja() -> Dict:
        return {
            'nome': ConfiguracaoModel.get('nome_loja', 'Loja Digital'),
            'logo': ConfiguracaoModel.get('logo', ''),
            'banner': ConfiguracaoModel.get('banner', ''),
            'emoji': ConfiguracaoModel.get('emoji_loja', '🛒'),
            'descricao': ConfiguracaoModel.get('sobre_loja', '')
        }
    
    @staticmethod
    def deletar(chave: str) -> bool:
        db = get_db()
        db.execute('DELETE FROM configuracoes WHERE chave = ?', (chave,))
        db.commit()
        return True
    
    @staticmethod
    def resetar_padrao() -> bool:
        db = get_db()
        db.execute('DELETE FROM configuracoes')
        from database.seed import inserir_dados_padrao
        inserir_dados_padrao()
        return True
