import csv
import json
from database.connection import get_db
from utils.helpers import safe_float, safe_int
import logging

logger = logging.getLogger(__name__)

class ImportacaoService:
    
    @staticmethod
    def importar_produtos_csv(caminho_arquivo: str) -> dict:
        try:
            db = get_db()
            inseridos = 0
            erros = 0
            
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        db.execute('''
                            INSERT INTO produtos (categoria_id, nome, descricao, preco, estoque, marca, codigo_barras)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            safe_int(row.get('categoria_id', 0)),
                            row.get('nome', 'Sem nome'),
                            row.get('descricao', ''),
                            safe_float(row.get('preco', 0)),
                            safe_int(row.get('estoque', 0)),
                            row.get('marca', ''),
                            row.get('codigo_barras', '')
                        ))
                        inseridos += 1
                    except Exception as e:
                        erros += 1
                        logger.error(f'Erro ao importar linha: {e}')
            
            db.commit()
            return {'sucesso': True, 'inseridos': inseridos, 'erros': erros}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
    
    @staticmethod
    def importar_produtos_json(dados_json: str) -> dict:
        try:
            dados = json.loads(dados_json)
            db = get_db()
            inseridos = 0
            
            for item in dados:
                db.execute('''
                    INSERT INTO produtos (categoria_id, nome, descricao, preco, estoque, foto)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    safe_int(item.get('categoria_id', 0)),
                    item.get('nome', 'Sem nome'),
                    item.get('descricao', ''),
                    safe_float(item.get('preco', 0)),
                    safe_int(item.get('estoque', 0)),
                    item.get('foto', '')
                ))
                inseridos += 1
            
            db.commit()
            return {'sucesso': True, 'inseridos': inseridos}
        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}
