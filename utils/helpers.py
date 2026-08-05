import random
import re
import hashlib
from datetime import datetime
from typing import Optional, Any

def formatar_moeda(valor: float) -> str:
    """Formata valor para moeda brasileira"""
    if valor is None: return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_data(data: Any, formato: str = "%d/%m/%Y %H:%M") -> str:
    """Formata data para padrão brasileiro"""
    if data is None: return ""
    if isinstance(data, str):
        try:
            data = datetime.fromisoformat(data.replace('Z', '+00:00'))
        except:
            return data
    return data.strftime(formato)

def formatar_data_curta(data: Any) -> str:
    """Formata data sem hora"""
    return formatar_data(data, "%d/%m/%Y")

def gerar_codigo() -> str:
    """Gera código de 6 dígitos"""
    return str(random.randint(100000, 999999))

def gerar_numero_pedido() -> str:
    """Gera número único de pedido"""
    return f"P{datetime.now().strftime('%y%m%d%H%M%S')}{random.randint(10, 99)}"

def gerar_codigo_afiliado(nome: str) -> str:
    """Gera código de afiliado baseado no nome"""
    base = re.sub(r'[^a-zA-Z0-9]', '', nome).upper()[:4]
    return f"{base}{random.randint(100, 999)}"

def gerar_hash(texto: str) -> str:
    """Gera hash SHA256"""
    return hashlib.sha256(texto.encode()).hexdigest()

def validar_cpf(cpf: str) -> bool:
    """Valida CPF"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11 or len(set(cpf)) == 1: return False
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10: resto = 0
    if resto != int(cpf[9]): return False
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10: resto = 0
    return resto == int(cpf[10])

def formatar_cpf(cpf: str) -> str:
    """Formata CPF com máscara"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}" if len(cpf) == 11 else cpf

def formatar_telefone(tel: str) -> str:
    """Formata telefone com máscara"""
    tel = re.sub(r'[^0-9]', '', tel)
    if len(tel) == 11: return f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
    if len(tel) == 10: return f"({tel[:2]}) {tel[2:6]}-{tel[6:]}"
    return tel

def validar_email(email: str) -> bool:
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validar_telefone(tel: str) -> bool:
    """Valida telefone brasileiro"""
    tel = re.sub(r'[^0-9]', '', tel)
    return len(tel) in [10, 11]

def truncar_texto(texto: str, limite: int = 100) -> str:
    """Trunca texto com reticências"""
    if not texto: return ""
    return texto[:limite-3] + "..." if len(texto) > limite else texto

def slugify(texto: str) -> str:
    """Converte texto para slug"""
    texto = texto.lower().strip()
    texto = re.sub(r'[àáâãäå]', 'a', texto)
    texto = re.sub(r'[èéêë]', 'e', texto)
    texto = re.sub(r'[ìíîï]', 'i', texto)
    texto = re.sub(r'[òóôõö]', 'o', texto)
    texto = re.sub(r'[ùúûü]', 'u', texto)
    texto = re.sub(r'[ç]', 'c', texto)
    texto = re.sub(r'[^a-z0-9\s-]', '', texto)
    texto = re.sub(r'[\s-]+', '-', texto)
    return texto.strip('-')

def safe_int(valor: Any, default: int = 0) -> int:
    """Converte para int com segurança"""
    try: return int(valor)
    except: return default

def safe_float(valor: Any, default: float = 0.0) -> float:
    """Converte para float com segurança"""
    try: return float(valor)
    except: return default
