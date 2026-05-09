import streamlit as st
import requests

# ==========================================
# CONFIGURAÇÃO DE ACESSO (SUA TRAVA DE SEGURANÇA)
# ==========================================
CODIGO_CORRETO = "MaranhaoQuant_2026" 

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Radar Quantamental | VIP", layout="centered")

# --- BARRA LATERAL DE LOGIN ---
st.sidebar.header("🔑 Acesso Restrito")
senha_digitada = st.sidebar.text_input("Insira seu Código VIP:", type="password")

if senha_digitada != CODIGO_CORRETO:
    st.error("🚨 ACESSO BLOQUEADO")
    st.info("Este radar é exclusivo para assinantes. Se você já é assinante, insira o código na barra lateral esquerda. Se ainda não tem acesso, adquira sua licença no Gumroad.")
    st.stop()

# --- CÓDIGO PRINCIPAL ---
st.title("🛡️ Radar de Risco Quantamental")
st.markdown("**Modelo Institucional:** A.D. Roy (Safety-First) + Oráculos Pyth Network")
st.write("Monitoramento 24/7 de distorções e incerteza no mercado de criptoativos.")
st.divider()

@st.cache_data(ttl=3600) 
def buscar_ativos_oficiais():
    fallback = {"🔥 BTC/USD (Modo de Segurança)": "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43"}
    try:
        response = requests.get("https://hermes.pyth.network/v2/price_feeds").json()
        catalogo = {}
        top_20 = ["BTC", "ETH", "SOL", "DOGE", "PEPE", "WIF", "BONK", "ARB", "OP", "LINK", "MATIC", "AVAX", "XRP", "ADA", "BNB", "SUI", "APT", "INJ", "NEAR", "FET"]
        for item in response:
            attrs = item.get("attributes", {})
            feed_id = item.get("id")
            asset_type = attrs.get("asset_type", "")
            base = attrs.get("base", "").upper()
            desc = attrs.get("description", "").upper()
            quote = attrs.get("quote_currency", "").upper()
            eh_dolar = (quote == "USD") or ("USD" in desc) or ("US DOLLAR" in desc)
            if asset_type == "Crypto" and eh_dolar:
                if not base:
                    simbolo = attrs.get("symbol", "")
                    base = simbolo.upper().replace("CRYPTO.", "").split("/")[0] if "CRYPTO." in simbolo.upper() else desc.split("/")[0].strip()
                if base not in catalogo:
                    catalogo[base] = {"id": feed_id, "nome": desc}
        lista_final = {}
        for ativo in top_20:
            if ativo in catalogo:
                info = catalogo[ativo]
                lista_final[f"🔥 {ativo}/USD ({info['nome']})"] = info['id']
        for base, info in catalogo.items():
            if base not in top_20:
                lista_final[f"💎 {base}/USD ({info['nome']})"] = info['id']
        return lista_final if len(lista_final) > 0 else fallback
    except Exception:
        return fallback

ativos = buscar_ativos_oficiais()

ativo_escolhido = st.selectbox("Selecione o ativo que deseja analisar:", list(ativos.keys()))
ativo_id = ativos[ativo_escolhido]
if ativo_id.startswith("0x"): ativo_id = ativo_id[2:]
url = f"https://hermes.pyth.network/v2/updates/price/latest?ids[]={ativo_id}"

if st.button("🔄 Atualizar Radar Agora"):
    with st.spinner(f"Conectando aos nós da Pyth..."):
        try:
            response = requests.get(url).json()
            if not response.get('parsed'):
                st.error("A rede Pyth não retornou dados para este ID no momento.")
            else:
                p = response['parsed'][0]['price']
                preco_real = int(p['price']) * (10 ** int(p['expo']))
                incerteza = int(p['conf']) * (10 ** int(p['expo']))
                risco_percentual = (incerteza / preco_real) * 100 if preco_real != 0 else 0
                
                st.subheader("📊 Leitura de Mercado Real-Time")
                col1, col2, col3 = st.columns(3)
                nome_limpo = ativo_escolhido.split("(")[0].replace("🔥 ", "").replace("💎 ", "").strip()
                
                # Formatação Dinâmica Segura (A correção do erro)
                if preco_real < 0.01:
                    f_p = f"${preco_real:,.8f}"
                    f_e = f"± ${incerteza:,.8f}"
                elif preco_real < 1:
                    f_p = f"${preco_real:,.4f}"
                    f_e = f"± ${incerteza:,.4f}"
                else:
                    f_p = f"${preco_real:,.2f}"
                    f_e = f"± ${incerteza:,.2f}"
                
                col1.metric("Ativo", nome_limpo)
                col2.metric("Preço Global", f_p)
                col3.metric("Margem de Erro", f_e)
                st.divider()
                st.subheader("🧠 Decisão Algorítmica (Safety-First):")
                if risco_percentual <= 0.15:
                    st.success(f"✅ **STATUS VERDE ({risco_percentual:.3f}%):** Liquidez normal. Seguro para posições.")
                elif risco_percentual <= 0.50:
                    st.warning(f"⚠️ **STATUS AMARELO ({risco_percentual:.3f}%):** Atenção. Divergência nos oráculos. Reduza alavancagem.")
                else:
                    st.error(f"🚨 **STATUS VERMELHO ({risco_percentual:.3f}%):** PERIGO! Colapso de liquidez. Proteja o capital.")
        except Exception:
            st.error("Erro interno na comunicação blockchain.")
else:
    st.info("👆 Clique no botão acima para puxar os dados.")