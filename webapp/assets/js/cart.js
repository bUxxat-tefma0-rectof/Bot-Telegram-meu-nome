class CartManager {
    constructor(userId) {
        this.userId = userId;
        this.items = [];
        this.listeners = [];
    }
    
    async load() {
        try {
            const resp = await fetch(`/api/carrinho?userId=${this.userId}`);
            const data = await resp.json();
            this.items = data.itens || [];
            this.notify();
        } catch(e) {
            console.error('Erro ao carregar carrinho:', e);
        }
    }
    
    async add(produtoId, quantidade = 1) {
        try {
            await fetch('/api/carrinho/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({userId: this.userId, produtoId, quantidade})
            });
            await this.load();
            return {sucesso: true};
        } catch(e) {
            return {sucesso: false, mensagem: 'Erro ao adicionar'};
        }
    }
    
    async remove(carrinhoId) {
        await fetch('/api/carrinho/remover', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({carrinhoId})
        });
        await this.load();
    }
    
    async updateQuantity(carrinhoId, quantidade) {
        if (quantidade <= 0) return this.remove(carrinhoId);
        await fetch('/api/carrinho/update', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({carrinhoId, quantidade})
        });
        await this.load();
    }
    
    async clear() {
        for (const item of this.items) {
            await this.remove(item.id);
        }
    }
    
    getTotal() {
        return this.items.reduce((sum, item) => {
            const preco = item.preco_promocional || item.preco;
            return sum + (preco * item.quantidade);
        }, 0);
    }
    
    getCount() {
        return this.items.reduce((sum, item) => sum + item.quantidade, 0);
    }
    
    onChange(callback) {
        this.listeners.push(callback);
    }
    
    notify() {
        this.listeners.forEach(cb => cb(this.items));
    }
}
