class CheckoutManager {
    constructor(userId) {
        this.userId = userId;
        this.metodoPagamento = 'pix';
        this.tipoEntrega = 'entrega';
        this.enderecoId = null;
        this.cupom = null;
        this.observacao = '';
    }
    
    async finalizar() {
        try {
            const resp = await fetch('/api/pedidos/finalizar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    userId: this.userId,
                    metodoPagamento: this.metodoPagamento,
                    tipoEntrega: this.tipoEntrega,
                    enderecoId: this.enderecoId,
                    cupom: this.cupom,
                    comentario: this.observacao
                })
            });
            
            const data = await resp.json();
            return data;
        } catch(e) {
            return {sucesso: false, mensagem: 'Erro ao finalizar pedido'};
        }
    }
    
    async validarCupom(codigo) {
        try {
            const resp = await fetch(`/api/cupons/validar?codigo=${codigo}`);
            const data = await resp.json();
            if (data.valido) {
                this.cupom = codigo;
            }
            return data;
        } catch(e) {
            return {valido: false, mensagem: 'Erro ao validar cupom'};
        }
    }
    
    setPagamento(metodo) {
        this.metodoPagamento = metodo;
    }
    
    setEntrega(tipo, enderecoId = null) {
        this.tipoEntrega = tipo;
        this.enderecoId = enderecoId;
    }
    
    setObservacao(texto) {
        this.observacao = texto;
    }
}
