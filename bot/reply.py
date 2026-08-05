from telegram import ForceReply
from typing import Optional

class ReplyService:
    
    @staticmethod
    def criar_reply(texto: str, placeholder: str = None) -> ForceReply:
        """Cria um ForceReply para o Telegram"""
        return ForceReply(selective=True, input_field_placeholder=placeholder or texto)
    
    @staticmethod
    def get_mensagem_solicitacao(tipo: str) -> str:
        """Retorna a mensagem de solicitação adequada"""
        mensagens = {
            'nome': '📝 Digite seu nome completo:',
            'telefone': '📱 Digite seu telefone com DDD:',
            'email': '📧 Digite seu email:',
            'cpf': '🔢 Digite seu CPF (apenas números):',
            'cnpj': '🏢 Digite seu CNPJ (apenas números):',
            'cep': '📍 Digite seu CEP:',
            'endereco': '🏠 Digite seu endereço completo:',
            'numero': '🔢 Digite o número:',
            'complemento': '📝 Digite o complemento:',
            'bairro': '🏘️ Digite o bairro:',
            'cidade': '🏙️ Digite a cidade:',
            'estado': '🗺️ Digite o estado (sigla):',
            'quantidade': '🔢 Digite a quantidade:',
            'valor': '💰 Digite o valor:',
            'cupom': '🎟 Digite o código do cupom:',
            'codigo': '🔐 Digite o código de verificação:',
            'pesquisa': '🔍 Digite o que deseja buscar:',
            'comentario': '📝 Digite um comentário (opcional):',
        }
        return mensagens.get(tipo, 'Digite a informação solicitada:')
