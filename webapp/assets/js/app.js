const API = '/api';
const tg = window.Telegram?.WebApp;

const state = {
    page: 'home',
    categorias: [],
    produtos: [],
    carrinho: [],
    pedidos: [],
    perfil: null,
    categoriaAtiva: null,
    metodoPagamento: 'pix',
    userId: tg?.initDataUnsafe?.user?.id || 1
};

// ============ INICIALIZAÇÃO ============
document.addEventListener('DOMContentLoaded', async () => {
    if (tg) { tg.expand(); tg.ready(); tg.MainButton.hide(); }
    await Promise.all([loadCategorias(), loadProdutos(), loadCarrinho(), loadPerfil()]);
    showPage('home');
});

// ============ NAVEGAÇÃO ============
function showPage(pageName) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    
    const page = document.getElementById(`page-${pageName}`);
    if (page) page.classList.add('active');
    
    const nav = document.querySelector(`[data-page="${pageName}"]`);
    if (nav) nav.classList.add('active');
    
    state.page = pageName;
    
    if (pageName === 'carrinho') renderCarrinho();
    if (pageName === 'pedidos') loadPedidos();
    if (pageName === 'perfil') renderPerfil();
    if (pageName === 'checkout') renderCheckout();
    
    window.scrollTo(0, 0);
}

// ============ API ============
async function apiGet(endpoint) {
    try { const r = await fetch(`${API}${endpoint}`); return await r.json(); }
    catch (e) { return {}; }
}

async function apiPost(endpoint, data) {
    try {
        const r = await fetch(`${API}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await r.json();
    } catch (e) { return { sucesso: false }; }
}

// ============ CATEGORIAS ============
async function loadCategorias() {
    const data = await apiGet('/categorias');
    state.categorias = Array.isArray(data) ? data : [];
    renderCategorias();
}

function renderCategorias() {
    const c = document.getElementById('categoriesContainer');
    if (!c) return;
    c.innerHTML = state.categorias.map(cat => `
        <div class="category-chip ${cat.id === state.categoriaAtiva ? 'active' : ''}" 
             onclick="toggleCategoria(${cat.id})">
            <span class="emoji">${cat.emoji || '📦'}</span>
            <span>${cat.nome}</span>
        </div>`).join('');
}

function toggleCategoria(id) {
    state.categoriaAtiva = state.categoriaAtiva === id ? null : id;
    renderCategorias();
    loadProdutos(state.categoriaAtiva);
}

// ============ PRODUTOS ============
async function loadProdutos(catId = null, termo = null) {
    let url = '/produtos?limite=50';
    if (catId) url += `&categoria_id=${catId}`;
    if (termo) url = `/produtos/pesquisar?q=${encodeURIComponent(termo)}`;
    
    const data = await apiGet(url);
    state.produtos = data.produtos || [];
    renderProdutos();
}

function renderProdutos() {
    const c = document.getElementById('productsContainer');
    if (!c || state.produtos.length === 0) {
        if (c) c.innerHTML = '<div class="empty-state"><div class="empty-icon">📭</div><div class="empty-title">Nenhum produto</div></div>';
        return;
    }
    
    c.innerHTML = state.produtos.map(p => {
        const preco = p.preco_promocional || p.preco;
        const desc = p.preco_promocional ? Math.round((1 - p.preco_promocional / p.preco) * 100) : 0;
        return `<div class="product-card" onclick="abrirProduto(${p.id})">
            ${desc > 0 ? `<div class="discount-badge">-${desc}%</div>` : ''}
            <div class="product-image">${p.foto ? `<img src="${p.foto}" onerror="this.parentElement.innerHTML='📦'">` : '📦'}</div>
            <div class="product-info">
                <div class="product-name">${p.nome}</div>
                ${p.marca ? `<div class="product-brand">${p.marca}</div>` : ''}
                <span class="product-price">${fmt(preco)}</span>
                ${p.preco_promocional ? `<span class="product-old-price">${fmt(p.preco)}</span>` : ''}
            </div>
        </div>`;
    }).join('');
}

// ============ PESQUISA ============
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('searchInput');
    if (input) {
        let t;
        input.addEventListener('input', () => {
            clearTimeout(t);
            t = setTimeout(() => {
                const v = input.value.trim();
                if (v.length >= 2) loadProdutos(null, v);
                else if (v.length === 0) loadProdutos(state.categoriaAtiva);
            }, 500);
        });
    }
});

// ============ MODAL PRODUTO ============
function abrirProduto(id) {
    const p = state.produtos.find(pr => pr.id === id);
    if (!p) return;
    
    const preco = p.preco_promocional || p.preco;
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
    
    overlay.innerHTML = `<div class="modal-sheet" onclick="event.stopPropagation()">
        <div class="modal-handle"></div>
        <div class="modal-header"><h3>${p.nome}</h3><button class="modal-close" onclick="this.closest('.modal-overlay').remove()">✕</button></div>
        <div class="modal-body">
            <div class="product-image-large">${p.foto ? `<img src="${p.foto}">` : '📦'}</div>
            ${p.marca ? `<p style="color:#999">🏷 ${p.marca}</p>` : ''}
            <p>${p.descricao || ''}</p>
            <h2 style="color:var(--primary)">${fmt(preco)}</h2>
            ${p.preco_promocional ? `<p style="text-decoration:line-through;color:#999">${fmt(p.preco)}</p>` : ''}
            <p style="color:#999">📦 Estoque: ${p.estoque} ${p.unidade || 'un'}</p>
            <div class="qtd-control">
                <button class="qtd-btn" onclick="this.nextElementSibling.textContent = Math.max(1, parseInt(this.nextElementSibling.textContent) - 1)">➖</button>
                <span class="qtd-num">1</span>
                <button class="qtd-btn" onclick="this.previousElementSibling.textContent = parseInt(this.previousElementSibling.textContent) + 1">➕</button>
            </div>
            <button class="btn btn-primary" onclick="addCarrinho(${p.id}, parseInt(this.parentElement.querySelector('.qtd-num').textContent)); this.closest('.modal-overlay').remove()">
                🛒 Adicionar - ${fmt(preco)}
            </button>
        </div>
    </div>`;
    
    document.body.appendChild(overlay);
}

// ============ CARRINHO ============
async function loadCarrinho() {
    const data = await apiGet(`/carrinho?userId=${state.userId}`);
    state.carrinho = data.itens || [];
    updateBadge();
}

function updateBadge() {
    const badge = document.getElementById('cartBadge');
    if (badge) {
        const t = state.carrinho.reduce((s, i) => s + i.quantidade, 0);
        badge.textContent = t;
        badge.style.display = t > 0 ? 'flex' : 'none';
    }
}

async function addCarrinho(prodId, qtd = 1) {
    await apiPost('/carrinho/add', { userId: state.userId, produtoId: prodId, quantidade: qtd });
    await loadCarrinho();
    toast('✅ Adicionado!');
}

function renderCarrinho() {
    const items = document.getElementById('cartItems');
    const total = document.getElementById('cartTotal');
    const empty = document.getElementById('cartEmpty');
    
    if (state.carrinho.length === 0) {
        if (items) items.innerHTML = '';
        if (total) total.innerHTML = '';
        if (empty) empty.style.display = 'block';
        return;
    }
    if (empty) empty.style.display = 'none';
    
    let tot = 0;
    if (items) items.innerHTML = state.carrinho.map(i => {
        const p = i.preco_promocional || i.preco;
        tot += p * i.quantidade;
        return `<div class="cart-item">
            <div class="cart-item-img">📦</div>
            <div class="cart-item-info">
                <div class="cart-item-name">${i.nome}</div>
                <div class="cart-item-price">${fmt(p * i.quantidade)}</div>
                <div class="cart-item-controls">
                    <button class="qty-btn" onclick="updateQtd(${i.id}, ${i.quantidade - 1})">➖</button>
                    <span class="qty-value">${i.quantidade}</span>
                    <button class="qty-btn" onclick="updateQtd(${i.id}, ${i.quantidade + 1})">➕</button>
                    <button class="cart-item-remove" onclick="removeItem(${i.id})">🗑</button>
                </div>
            </div>
        </div>`;
    }).join('');
    
    if (total) total.innerHTML = `<div class="cart-total-bar">
        <div class="cart-total-row"><span>Total</span><span style="color:var(--primary)">${fmt(tot)}</span></div>
        <button class="btn btn-primary" onclick="showPage('checkout')">💳 Finalizar Pedido</button>
    </div>`;
}

async function updateQtd(id, qtd) {
    if (qtd <= 0) return removeItem(id);
    await apiPost('/carrinho/update', { carrinhoId: id, quantidade: qtd });
    await loadCarrinho();
    renderCarrinho();
}

async function removeItem(id) {
    await apiPost('/carrinho/remover', { carrinhoId: id });
    await loadCarrinho();
    renderCarrinho();
}

// ============ CHECKOUT ============
function renderCheckout() {
    const c = document.getElementById('checkoutContent');
    if (!c) return;
    if (state.carrinho.length === 0) {
        c.innerHTML = '<div class="empty-state"><div class="empty-icon">🛒</div><div class="empty-title">Carrinho vazio</div></div>';
        return;
    }
    
    const tot = state.carrinho.reduce((s, i) => s + (i.preco_promocional || i.preco) * i.quantidade, 0);
    
    c.innerHTML = `<div class="card"><div class="card-title">📦 Resumo</div>
        ${state.carrinho.map(i => `<div class="checkout-item"><span>${i.quantidade}x ${i.nome}</span><span>${fmt((i.preco_promocional||i.preco)*i.quantidade)}</span></div>`).join('')}
        <hr><div class="checkout-total"><span>Total</span><span style="color:var(--primary)">${fmt(tot)}</span></div>
    </div>
    <div class="card"><div class="card-title">💳 Pagamento</div>
        ${[{id:'pix',n:'PIX',i:'💳'},{id:'dinheiro',n:'Dinheiro',i:'💵'}].map(m => `
        <div class="payment-method ${state.metodoPagamento===m.id?'selected':''}" onclick="state.metodoPagamento='${m.id}';renderCheckout()">
            <span class="method-icon">${m.i}</span><div class="method-info"><div class="method-name">${m.n}</div></div>
            <div class="method-check">${state.metodoPagamento===m.id?'✓':''}</div>
        </div>`).join('')}
    </div>
    <button class="btn btn-primary" onclick="finalizar()">💳 Pagar ${fmt(tot)}</button>`;
}

async function finalizar() {
    toast('⏳ Processando...');
    const r = await apiPost('/pedidos/finalizar', {
        userId: state.userId,
        metodoPagamento: state.metodoPagamento,
        tipoEntrega: 'entrega'
    });
    
    if (r.sucesso) {
        state.carrinho = [];
        await loadCarrinho();
        toast('✅ Pedido realizado!', 'success');
        
        if (r.pagamento?.qr_code_base64) {
            const overlay = document.createElement('div');
            overlay.className = 'modal-overlay';
            overlay.onclick = () => overlay.remove();
            overlay.innerHTML = `<div class="modal-sheet" onclick="event.stopPropagation()">
                <div class="modal-handle"></div><div class="modal-body" style="text-align:center">
                <h3>💳 PIX</h3><img src="data:image/png;base64,${r.pagamento.qr_code_base64}" style="width:250px">
                <p style="margin:15px 0;word-break:break-all;font-size:11px">${r.pagamento.copia_cola||''}</p>
                <button class="btn btn-primary" onclick="this.closest('.modal-overlay').remove();showPage('pedidos')">✅ Já paguei</button>
            </div></div>`;
            document.body.appendChild(overlay);
        }
        showPage('pedidos');
    } else {
        toast('❌ ' + (r.mensagem || 'Erro'), 'error');
    }
}

// ============ PEDIDOS ============
async function loadPedidos() {
    const data = await apiGet(`/pedidos?userId=${state.userId}`);
    state.pedidos = data.pedidos || [];
    renderPedidos();
}

function renderPedidos() {
    const c = document.getElementById('ordersList');
    const e = document.getElementById('ordersEmpty');
    if (!c) return;
    
    if (state.pedidos.length === 0) { if (e) e.style.display = 'block'; c.innerHTML = ''; return; }
    if (e) e.style.display = 'none';
    
    const st = {recebido:'status-pending',confirmado:'status-confirmed',separando:'status-preparing',entrega:'status-delivering',entregue:'status-delivered',cancelado:'status-cancelled'};
    
    c.innerHTML = state.pedidos.map(p => `
        <div class="card"><div class="order-header"><strong>${p.numero}</strong><span class="status-badge ${st[p.status]||'status-pending'}">${p.status}</span></div>
        <div class="order-date">${p.data_pedido||''}</div><div class="order-total">${fmt(p.total)}</div></div>
    `).join('');
}

// ============ PERFIL ============
async function loadPerfil() {
    const data = await apiGet(`/perfil?userId=${state.userId}`);
    state.perfil = data;
}

function renderPerfil() {
    const c = document.getElementById('profileContent');
    if (!c) return;
    const p = state.perfil || {};
    
    c.innerHTML = `<div class="card profile-header">
        <div class="profile-avatar">👤</div>
        <h2>${p.nome||'Cliente'} ${p.sobrenome||''}</h2>
        <p>${p.email||'N/A'}</p>
    </div>
    <div class="card profile-stats">
        <div class="stat-row"><span>📦 Pedidos</span><span>${p.totalPedidos||0}</span></div>
        <div class="stat-row"><span>💰 Total Gasto</span><span style="color:var(--primary)">${fmt(p.total_gasto||0)}</span></div>
        <div class="stat-row"><span>⭐ Pontos</span><span>${p.pontos_fidelidade||0}</span></div>
    </div>`;
}

// ============ UTILS ============
function fmt(v) { return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v || 0); }

function toast(msg, type = '') {
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2500);
}
