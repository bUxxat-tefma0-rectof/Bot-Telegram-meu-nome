import requests
import logging

logger = logging.getLogger(__name__)

class CepService:
    
    @staticmethod
    def consultar(cep: str) -> dict:
        cep_limpo = ''.join(filter(str.isdigit, str(cep)))
        
        if len(cep_limpo) != 8:
            return {'sucesso': False, 'mensagem': 'CEP deve ter 8 dígitos'}
        
        try:
            resp = requests.get(f'https://viacep.com.br/ws/{cep_limpo}/json/', timeout=5)
            data = resp.json()
            
            if 'erro' in data:
                return {'sucesso': False, 'mensagem': 'CEP não encontrado'}
            
            return {
                'sucesso': True,
                'dados': {
                    'cep': cep_limpo,
                    'logradouro': data.get('logradouro', ''),
                    'bairro': data.get('bairro', ''),
                    'cidade': data.get('localidade', ''),
                    'estado': data.get('uf', ''),
                    'complemento': data.get('complemento', '')
                }
            }
        except Exception as e:
            logger.error(f'Erro CEP: {e}')
            return {'sucesso': False, 'mensagem': 'Erro ao consultar CEP'}
    
    @staticmethod
    def formatar(cep: str) -> str:
        cep = ''.join(filter(str.isdigit, str(cep)))
        return f"{cep[:5]}-{cep[3:]}" if len(cep) == 8 else cep
