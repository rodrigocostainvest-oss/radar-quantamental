import streamlit as st
import requests

# ==========================================
# CONFIGURAÇÃO DE ACESSO (SUA CHAVE DE VENDA)
# ==========================================
# Altere esta senha quando quiser mudar o acesso dos seus clientes
SENHA_MESTRE = "Vanguard2026" 

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Radar Quantamental VIP", layout="centered")

# Interface de Login
st.sidebar.title("🔐 Acesso Restrito")
senha_digitada = st.sidebar.text_input("Digite sua chave de acesso:", type="password")

if senha_digitada != SENHA_MESTRE:
    st.title("🛡️ Radar de Risco Quantamental")
    st.warning("Aguardando Chave de Acesso VIP...")
    st.info("Este é um monitoramento institucional de alta precisão. Se você já é assinante, insira sua chave na barra lateral.")
    st.stop() # Interrompe o código aqui se a senha estiver errada

# ==========================================
# SE A SENHA ESTIVER CORRETA, O CÓDIGO ABAIXO É EXECUTADO
# ==========================================
st.title("🛡️ Radar de Risco Quantamental [VIP]")
st.markdown("**Modelo Institucional:** A.D. Roy (Safety-First) + Oráculos Pyth Network")
st.divider()

# MOTOR DE BUSCA DINÂMICO
@st.cache_data(ttl=3600) 
def buscar_ativos_oficiais():
    fallback = {"🔥 BTC/USD": "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43"}
    try:
        response = requests.get("https://hermes.pyth.network/v2/price_feeds").json()
        catalogo = {}
        top_20 = ["BTC", "ETH", "SOL", "DOGE", "PEPE", "WIF", "BONK", "ARB", "OP", "LINK", "MATIC", "AVAX", "XRP", "ADA", "BNB", "SUI", "APT", "INJ", "NEAR", "FET"]
        for item in response:
            attrs = item.get("attributes", {})
            if attrs.get("asset_type") == "Crypto" and "USD" in attrs.get("description", "").upper():
                base = attrs.get("base", "").upper() or attrs.get("description", "").split("/")[0].strip()
                catalogo[base] = {"id": item.get("id"), "nome": attrs.get("description")}
        
        lista_final = {}
        for ativo in top_20:
            if ativo in catalogo:
                lista_final[f"🔥 {ativo}/USD"] = catalogo[ativo]["id"]
        for base, info in catalogo.items():
            if base not in top_20:
                lista_final[f"💎 {base}/USD"] = info["id"]
        return lista_final
    except: return fallback

ativos = buscar_ativos_oficiais()
ativo_escolhido = st.selectbox("Selecione o ativo:", list(ativos.keys()))
ativo_id = ativos[ativo_escolhido].replace("0x", "")

url = f"https://hermes.pyth.network/v2/updates/price/latest?ids[]={ativo_id}"

if st.button("🔄 Atualizar Radar Agora"):
    with st.spinner("Puxando dados on-chain..."):
        try:
            res = requests.get(url).json()
            p_raw = int(res['parsed'][0]['price']['price'])
            c_raw = int(res['parsed'][0]['price']['conf'])
            expo = int(res['parsed'][0]['price']['expo'])
            p_real = p_raw * (10**expo)
            conf = c_raw * (10**expo)
            risco = (conf / p_real) * 100
            
            st.subheader("📊 Leitura de Mercado Real-Time")
            c1, c2, c3 = st.columns(3)
            nome_limpo = ativo_escolhido.replace("🔥 ", "").replace("💎 ", "")
            
            # Formatação Dinâmica
            fmt = ":,.8f" if p_real < 0.01 else ":,.4f" if p_real < 1 else ":,.2f"
            c1.metric("Ativo", nome_limpo)
            c2.metric("Preço Global", f"${p_real{fmt}}")
            c3.metric("Margem de Erro", f"± ${conf{fmt}}")
            
            st.divider()
            st.subheader("🧠 Decisão Algorítmica:")
            if risco <= 0.15: st.success(f"✅ STATUS VERDE ({risco:.3f}%): Liquidez normal.")
            elif risco <= 0.50: st.warning(f"⚠️ STATUS AMARELO ({risco:.3f}%): Reduza alavancagem.")
            else: st.error(f"🚨 STATUS VERMELHO ({risco:.3f}%): PERIGO! Colapso de liquidez.")
        except: st.error("Erro na rede Pyth.")