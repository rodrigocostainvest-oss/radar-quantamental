import streamlit as st
import requests

# ==========================================
# ACCESS CONFIGURATION (SECURITY LOCK)
# ==========================================
CODIGO_CORRETO = "MaranhaoQuant_2026" 

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Quantamental Radar | VIP", layout="centered")

# --- LOGIN SIDEBAR ---
st.sidebar.header("🔑 Restricted Access")
senha_digitada = st.sidebar.text_input("Enter your VIP Access Key:", type="password")

if senha_digitada != CODIGO_CORRETO:
    st.error("🚨 ACCESS DENIED")
    st.info("This radar is exclusive to subscribers. If you have an active subscription, enter your key in the left sidebar. If not, get your license on Gumroad.")
    st.stop()

# --- MAIN CODE ---
st.title("🛡️ Quantamental Risk Radar")
st.markdown("**Institutional Model:** A.D. Roy (Safety-First) + Pyth Network Oracles")
st.write("24/7 monitoring of market distortions and uncertainty in crypto assets.")
st.divider()

@st.cache_data(ttl=3600) 
def buscar_ativos_oficiais():
    fallback = {"🔥 BTC/USD (Safe Mode)": "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43"}
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

ativo_escolhido = st.selectbox("Select the asset you want to analyze:", list(ativos.keys()))
ativo_id = ativos[ativo_escolhido]
if ativo_id.startswith("0x"): ativo_id = ativo_id[2:]
url = f"https://hermes.pyth.network/v2/updates/price/latest?ids[]={ativo_id}"

if st.button("🔄 Update Radar Now"):
    with st.spinner(f"Connecting to Pyth nodes..."):
        try:
            response = requests.get(url).json()
            if not response.get('parsed'):
                st.error("The Pyth network did not return data for this ID right now.")
            else:
                p = response['parsed'][0]['price']
                preco_real = int(p['price']) * (10 ** int(p['expo']))
                incerteza = int(p['conf']) * (10 ** int(p['expo']))
                risco_percentual = (incerteza / preco_real) * 100 if preco_real != 0 else 0
                
                st.subheader("📊 Real-Time Market Reading")
                col1, col2, col3 = st.columns(3)
                nome_limpo = ativo_escolhido.split("(")[0].replace("🔥 ", "").replace("💎 ", "").strip()
                
                # Dynamic Safe Formatting
                if preco_real < 0.01:
                    f_p = f"${preco_real:,.8f}"
                    f_e = f"± ${incerteza:,.8f}"
                elif preco_real < 1:
                    f_p = f"${preco_real:,.4f}"
                    f_e = f"± ${incerteza:,.4f}"
                else:
                    f_p = f"${preco_real:,.2f}"
                    f_e = f"± ${incerteza:,.2f}"
                
                col1.metric("Asset", nome_limpo)
                col2.metric("Global Price", f_p)
                col3.metric("Margin of Error", f_e)
                st.divider()
                st.subheader("🧠 Algorithmic Decision (Safety-First):")
                if risco_percentual <= 0.15:
                    st.success(f"✅ **GREEN STATUS ({risco_percentual:.3f}%):** Normal liquidity. Safe to hold positions.")
                elif risco_percentual <= 0.50:
                    st.warning(f"⚠️ **YELLOW STATUS ({risco_percentual:.3f}%):** Oracle divergence alert. Reduce leverage.")
                else:
                    st.error(f"🚨 **RED STATUS ({risco_percentual:.3f}%):** DANGER! Liquidity collapse. Protect capital.")
        except Exception:
            st.error("Internal error. The market might be facing extreme latency.")
else:
    st.info("👆 Click the button above to pull live on-chain data.")