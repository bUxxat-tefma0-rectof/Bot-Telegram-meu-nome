const API = '/api/admin';
let currentPage = 'dashboard';
let currentTheme = localStorage.getItem('theme') || 'light';

// ============ NAVEGAÇÃO ============
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

function loadPage(page) {
    currentPage = page;
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const pageEl = document.getElementById(`page-${page}`);
    if (pageEl) pageEl.classList.add('active');
    
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelector(`[data-page="${page}"]`)?.classList.add('active');
    
    document.getElementById('pageTitle').textContent = 
        page.charAt(0).toUpperCase() + page.slice(1);
    
    if (window.innerWidth < 768) toggleSidebar();
    
    loadPageData(page);
}

function loadPageData(page) {
    switch(page) {
        case 'dashboard': loadDashboard(); break;
        case 'produtos': loadProdutos(); break;
        case 'categorias': loadCategorias(); break;
        case 'pedidos': loadPedidos(); break;
        case 'clientes': loadClientes(); break;
        case 'financeiro': loadFinanceiro(); break;
        case 'cupons': loadCupons(); break;
        case 'afiliados': loadAfiliados(); break;
        case 'mensagens': loadMensagens(); break;
        case 'botoes': loadBotoes(); break;
        case 'banners': loadBanners(); break;
        case 'aparencia': loadAparencia(); break;
        case 'configuracoes': loadConfiguracoes(); break;
    }
}

// ============ DASHBOARD ============
async function loadDashboard() {
    try {
        const resp = await fetch(`${API}/dashboard`);
        const data = await resp.json();
        
        document.getElementById('statClientes').textContent = data.clientes?.total || 0;
        document.getElementById('statPedidos').textContent = data.pedidos?.hoje || 0;
        document.getElementById('statFaturamento').textContent = data.faturamento?.mes || 'R$ 0';
        document.getElementById('statPendentes').textContent = data.pedidos?.pendentes || 0;
        
        if (data.top_produtos) {
            document.getElementById('topProdutos').innerHTML = data.top_produtos.map((p, i) => 
                `<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border)">
                    <span>${i+1}. ${p.produto_nome}</span>
                    <span>${p.vendas}x</span>
                </div>`
            ).join('');
        }
    } catch(e) {
        console.error('Erro dashboard:', e);
    }
}

// ============ PRODUTOS ============
async function loadProdutos() {
    const resp = await fetch(`${API}/produtos`);
    const data = await resp.json();
    const prods = data.produtos || [];
    
    document.getElementById('tabelaProdutos').innerHTML = prods.map(p => `
        <tr>
            <td>${p.id}</td>
            <td>${p.nome}</td>
            <td>${p.categoria_nome || 'N/A'}</td>
            <td>R$ ${(p.preco || 0).toFixed(2)}</td>
            <td>${p.estoque}</td>
            <td><span class="badge ${p.disponivel ? 'badge-success' : 'badge-danger'}">${p.disponivel ? 'Ativo' : 'Inativo'}</span></td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editarProduto(${p.id})">✏️</button>
                <button class="btn btn-sm btn-danger" onclick="excluirProduto(${p.id})">🗑</button>
            </td>
        </tr>
    `).join('');
}

async function editarProduto(id) {
    const resp = await fetch(`${API}/produtos?id=${id}`);
    const p = await resp.json();
    
    document.getElementById('modalTitle').textContent = 'Editar Produto';
    document.getElementById('modalBody').innerHTML = `
        <div class="form-group"><label>Nome</label><input type="text" id="editNome" value="${p.nome || ''}"></div>
        <div class="form-group"><label>Preço</label><input type="number" id="editPreco" value="${p.preco || 0}" step="0.01"></div>
        <div class="form-group"><label>Estoque</label><input type="number" id="editEstoque" value="${p.estoque || 0}"></div>
        <button class="btn btn-primary" onclick="salvarProduto(${id})">Salvar</button>
    `;
    document.getElementById('modalOverlay').classList.add('active');
}

async function salvarProduto(id) {
    const dados = {
        nome: document.getElementById('editNome').value,
        preco: parseFloat(document.getElementById('editPreco').value),
        estoque: parseInt(document.getElementById('editEstoque').value)
    };
    
    await fetch(`${API}/produtos/${id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(dados)
    });
    
    closeModal();
    loadProdutos();
}

async function excluirProduto(id) {
    if (confirm('Excluir este produto?')) {
        await fetch(`${API}/produtos/${id}`, {method: 'DELETE'});
        loadProdutos();
    }
}

// ============ PEDIDOS ============
async function loadPedidos() {
    const resp = await fetch(`${API}/pedidos`);
    const data = await resp.json();
    const peds = data.pedidos || [];
    
    const statusEmoji = {recebido:'📥', confirmado:'✅', separando:'📦', entrega:'🛵', entregue:'🏠', cancelado:'❌'};
    
    document.getElementById('tabelaPedidos').innerHTML = peds.map(p => `
        <tr>
            <td>${p.numero}</td>
            <td>${p.cliente_nome || 'N/A'}</td>
            <td>R$ ${(p.total || 0).toFixed(2)}</td>
            <td>${statusEmoji[p.status] || '📋'} ${p.status}</td>
            <td>${new Date(p.data_pedido).toLocaleDateString()}</td>
            <td>
                <select onchange="alterarStatus(${p.id}, this.value)" style="padding:5px;border-radius:5px;border:1px solid var(--border)">
                    <option value="">Status...</option>
                    <option value="confirmado">✅ Confirmado</option>
                    <option value="separando">📦 Separando</option>
                    <option value="entrega">🛵 Entrega</option>
                    <option value="entregue">🏠 Entregue</option>
                    <option value="cancelado">❌ Cancelar</option>
                </select>
            </td>
        </tr>
    `).join('');
}

async function alterarStatus(id, status) {
    if (!status) return;
    await fetch(`${API}/pedidos/${id}/status`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({status})
    });
    loadPedidos();
}

// ============ CLIENTES ============
async function loadClientes() {
    const resp = await fetch(`${API}/clientes`);
    const data = await resp.json();
    
    document.getElementById('tabelaClientes').innerHTML = (data.clientes || []).map(c => `
        <tr>
            <td>${c.telegram_id}</td>
            <td>${c.nome || 'N/A'}</td>
            <td>${c.telefone || 'N/A'}</td>
            <td>R$ ${(c.total_gasto || 0).toFixed(2)}</td>
            <td>${c.bloqueado ? '🚫 Bloqueado' : '✅ Ativo'}</td>
            <td>
                <button class="btn btn-sm ${c.bloqueado ? 'btn-success' : 'btn-danger'}" onclick="toggleCliente(${c.id})">
                    ${c.bloqueado ? 'Desbloquear' : 'Bloquear'}
                </button>
            </td>
        </tr>
    `).join('');
}

async function toggleCliente(id) {
    await fetch(`${API}/clientes/${id}/toggle`, {method: 'POST'});
    loadClientes();
}

// ============ CUPONS ============
async function loadCupons() {
    const resp = await fetch(`${API}/cupons`);
    const data = await resp.json();
    
    document.getElementById('tabelaCupons').innerHTML = (data || []).map(c => `
        <tr>
            <td><code>${c.codigo}</code></td>
            <td>${c.tipo === 'percentual' ? '%' : 'R$'}</td>
            <td>${c.valor}</td>
            <td>${c.uso_atual}/${c.uso_maximo}</td>
            <td>${c.ativo ? '✅' : '❌'}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="toggleCupom(${c.id})">🔄</button>
                <button class="btn btn-sm btn-danger" onclick="excluirCupom(${c.id})">🗑</button>
            </td>
        </tr>
    `).join('');
}

async function toggleCupom(id) {
    await fetch(`${API}/cupons/${id}/toggle`, {method: 'POST'});
    loadCupons();
}

// ============ FINANCEIRO ============
async function loadFinanceiro() {
    const resp = await fetch(`${API}/financeiro`);
    const data = await resp.json();
    
    document.getElementById('finTotal').textContent = `R$ ${(data.faturamento_total || 0).toFixed(2)}`;
    document.getElementById('finMes').textContent = `R$ ${(data.faturamento_mes || 0).toFixed(2)}`;
    document.getElementById('finHoje').textContent = `R$ ${(data.faturamento_hoje || 0).toFixed(2)}`;
    document.getElementById('finDescontos').textContent = `R$ ${(data.total_descontos || 0).toFixed(2)}`;
}

// ============ AFILIADOS ============
async function loadAfiliados() {
    const resp = await fetch(`${API}/afiliados`);
    const data = await resp.json();
    
    document.getElementById('tabelaAfiliados').innerHTML = (data || []).map(a => `
        <tr>
            <td>${a.nome || 'N/A'}</td>
            <td><code>${a.codigo}</code></td>
            <td>${a.comissao_percentual}%</td>
            <td>${a.total_indicacoes}</td>
            <td>R$ ${(a.saldo_comissao || 0).toFixed(2)}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editarComissao(${a.id})">💰</button>
            </td>
        </tr>
    `).join('');
}

// ============ MENSAGENS ============
async function loadMensagens() {
    const resp = await fetch(`${API}/mensagens`);
    const data = await resp.json();
    
    document.getElementById('listaMensagens').innerHTML = (data || []).map(m => `
        <div class="card" style="margin-bottom:10px">
            <strong>${m.chave}</strong>
            <textarea id="msg_${m.chave}" style="width:100%;margin:10px 0;padding:10px;border-radius:8px;border:1px solid var(--border);min-height:60px">${m.conteudo || ''}</textarea>
            <button class="btn btn-sm btn-primary" onclick="salvarMensagem('${m.chave}')">Salvar</button>
        </div>
    `).join('');
}

async function salvarMensagem(chave) {
    const conteudo = document.getElementById(`msg_${chave}`).value;
    await fetch(`${API}/mensagens`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({chave, conteudo})
    });
    alert('Mensagem salva!');
}

// ============ BOTÕES ============
async function loadBotoes() {
    const resp = await fetch(`${API}/botoes`);
    const data = await resp.json();
    
    const menus = {};
    (data || []).forEach(b => {
        if (!menus[b.menu]) menus[b.menu] = [];
        menus[b.menu].push(b);
    });
    
    let html = '';
    for (const [menu, botoes] of Object.entries(menus)) {
        html += `<div class="card"><h3>📁 Menu: ${menu}</h3>`;
        botoes.forEach(b => {
            html += `<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--border)">
                <span>${b.emoji || ''} ${b.texto}</span>
                <span><code>${b.callback_data || b.url || ''}</code></span>
                <span>${b.ativo ? '✅' : '❌'}</span>
                <button class="btn btn-sm btn-primary" onclick="toggleBotao(${b.id})">🔄</button>
                <button class="btn btn-sm btn-danger" onclick="excluirBotao(${b.id})">🗑</button>
            </div>`;
        });
        html += '</div>';
    }
    document.getElementById('listaBotoes').innerHTML = html;
}

async function toggleBotao(id) {
    await fetch(`${API}/botoes/${id}/toggle`, {method: 'POST'});
    loadBotoes();
}

// ============ APARÊNCIA ============
async function loadAparencia() {
    const resp = await fetch(`${API}/aparencia`);
    const data = await resp.json();
    
    document.getElementById('selectTema').value = data.tema || 'light';
    document.getElementById('corPrimaria').value = data.cores?.primaria || '#6366f1';
    document.getElementById('corSecundaria').value = data.cores?.secundaria || '#ec4899';
    document.getElementById('nomeLoja').value = data.nome_loja || '';
    document.getElementById('logoLoja').value = data.logo || '';
}

function mudarTema(tema) {
    localStorage.setItem('theme', tema);
    const stylesheet = document.getElementById('themeStylesheet');
    stylesheet.href = `assets/css/themes/${tema}.css`;
}

async function salvarCor(chave, valor) {
    await fetch(`${API}/aparencia`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({[chave]: valor})
    });
}

async function salvarConfig(chave, valor) {
    await fetch(`${API}/config`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({[chave]: valor})
    });
}

// ============ CONFIGURAÇÕES ============
async function loadConfiguracoes() {
    const resp = await fetch(`${API}/config`);
    const data = await resp.json();
    
    document.getElementById('cfgPedidoMinimo').value = data.pedido_minimo || 10;
    document.getElementById('cfgTaxaEntrega').value = data.taxa_entrega || 5;
    document.getElementById('cfgExpiracaoPix').value = data.tempo_expiracao_pix || 30;
    document.getElementById('cfgComissao').value = data.comissao_afiliado || 5;
}

async function criarBackup() {
    const resp = await fetch(`${API}/backup`, {method: 'POST'});
    const data = await resp.json();
    alert(data.mensagem || 'Backup criado!');
}

// ============ MODAL ============
function showModal(id) {
    document.getElementById('modalOverlay').classList.add('active');
}

function closeModal() {
    document.getElementById('modalOverlay').classList.remove('active');
}

// ============ EXPORTAÇÃO ============
async function exportarCSV(tipo) {
    window.open(`${API}/exportar/${tipo}`, '_blank');
}

// ============ INIT ============
function refreshPage() { loadPageData(currentPage); }

function toggleTheme() {
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    currentTheme = newTheme;
    mudarTema(newTheme);
}

document.addEventListener('DOMContentLoaded', () => {
    mudarTema(currentTheme);
    loadDashboard();
});
