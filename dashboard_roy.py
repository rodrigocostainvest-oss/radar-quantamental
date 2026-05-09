import streamlit as st
import requests

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Radar Quantamental | Pyth", layout="centered")

st.title("🛡️ Radar de Risco Quantamental")
st.markdown("**Modelo Institucional:** A.D. Roy (Safety-First) + Oráculos Pyth Network")
st.write("Monitoramento 24/7 de distorções e incerteza no mercado de criptoativos.")
st.divider()

# ==========================================
# MOTOR DE BUSCA DINÂMICO BLINDADO (SÓ CRIPTO)
# ==========================================
@st.cache_data(ttl=3600) 
def buscar_ativos_oficiais():
    fallback = {"🔥 BTC/USD (Modo de Segurança)": "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43"}
    
    try:
        response = requests.get("https://hermes.pyth.network/v2/price_feeds").json()
        catalogo = {}
        
        top_20 = [
            "BTC", "ETH", "SOL", "DOGE", "PEPE", 
            "WIF", "BONK", "ARB", "OP", "LINK", 
            "MATIC", "AVAX", "XRP", "ADA", "BNB", 
            "SUI", "APT", "INJ", "NEAR", "FET"
        ]
        
        for item in response:
            attrs = item.get("attributes", {})
            feed_id = item.get("id")
            asset_type = attrs.get("asset_type", "")
            
            base = attrs.get("base", "").upper()
            desc = attrs.get("description", "").upper()
            quote = attrs.get("quote_currency", "").upper()
            
            # A CORREÇÃO: Aceita "USD" ou "US DOLLAR" para não perder os Gigantes
            eh_dolar = (quote == "USD") or ("USD" in desc) or ("US DOLLAR" in desc)
            
            if asset_type == "Crypto" and eh_dolar:
                # Se a Pyth não mandar a sigla separada, extraímos do campo 'symbol' oficial
                if not base:
                    simbolo = attrs.get("symbol", "")
                    if "CRYPTO." in simbolo.upper():
                        base = simbolo.upper().replace("CRYPTO.", "").split("/")[0]
                    else:
                        base = desc.split("/")[0].strip()
                
                # Guarda no nosso catálogo inteligente
                if base not in catalogo:
                    catalogo[base] = {"id": feed_id, "nome": desc}
                
        lista_final = {}
        
        # 1. Puxa os Gigantes e queima o fogo 🔥
        for ativo in top_20:
            if ativo in catalogo:
                info = catalogo[ativo]
                lista_final[f"🔥 {ativo}/USD ({info['nome']})"] = info['id']
                
        # 2. Puxa os Diamantes 💎
        for base, info in catalogo.items():
            if base not in top_20:
                lista_final[f"💎 {base}/USD ({info['nome']})"] = info['id']
                
        if len(lista_final) == 0:
            return fallback
            
        return lista_final
        
    except Exception as e:
        return fallback

ativos = buscar_ativos_oficiais()

# ==========================================
# INTERFACE DO USUÁRIO
# ==========================================

if not ativos:
    st.warning("Inicializando comunicação com a rede blockchain...")
    st.stop()

ativo_escolhido = st.selectbox("Selecione o ativo que deseja analisar:", list(ativos.keys()))

if ativo_escolhido is None:
    st.stop()

ativo_id = ativos[ativo_escolhido]
if ativo_id.startswith("0x"):
    ativo_id = ativo_id[2:]

url = f"https://hermes.pyth.network/v2/updates/price/latest?ids[]={ativo_id}"

if st.button("🔄 Atualizar Radar Agora"):
    with st.spinner(f"Conectando aos nós da Pyth..."):
        try:
            response = requests.get(url).json()
            
            if not response.get('parsed'):
                st.error("A rede Pyth não retornou dados para este ID no momento.")
            else:
                preco_bruto = int(response['parsed'][0]['price']['price'])
                conf_bruto = int(response['parsed'][0]['price']['conf'])
                expo = int(response['parsed'][0]['price']['expo'])
                
                preco_real = preco_bruto * (10 ** expo)
                incerteza = conf_bruto * (10 ** expo)
                
                risco_percentual = (incerteza / preco_real) * 100 if preco_real != 0 else 0
                
                st.subheader("📊 Leitura de Mercado Real-Time")
                col1, col2, col3 = st.columns(3)
                
                # Limpa a string para ficar elegante
                nome_limpo = ativo_escolhido.split("(")[0].replace("🔥 ", "").replace("💎 ", "").strip()
                
                # Formatação Dinâmica (O Ajuste do PEPE)
                if preco_real < 0.01:
                    str_preco = f"${preco_real:,.8f}"
                    str_erro = f"± ${incerteza:,.8f}"
                elif preco_real < 1.0:
                    str_preco = f"${preco_real:,.4f}"
                    str_erro = f"± ${incerteza:,.4f}"
                else:
                    str_preco = f"${preco_real:,.2f}"
                    str_erro = f"± ${incerteza:,.2f}"
                
                col1.metric(label="Ativo", value=nome_limpo)
                col2.metric(label="Preço Global", value=str_preco)
                col3.metric(label="Margem de Erro", value=str_erro)
                
                st.divider()
                
                # Calibragem da Régua de Risco para Altcoins
                st.subheader("🧠 Decisão Algorítmica (Safety-First):")
                if risco_percentual <= 0.15:
                    st.success(f"✅ **STATUS VERDE ({risco_percentual:.3f}% de incerteza):** Liquidez normal para este ativo. Seguro para posições.")
                elif risco_percentual <= 0.50:
                    st.warning(f"⚠️ **STATUS AMARELO ({risco_percentual:.3f}% de incerteza):** Atenção. Divergência acima da média nos oráculos. Reduza alavancagem.")
                else:
                    st.error(f"🚨 **STATUS VERMELHO ({risco_percentual:.3f}% de incerteza):** PERIGO INSTITUCIONAL! Colapso de liquidez. Proteja o capital.")
                    
        except Exception as e:
            st.error("Erro interno. O mercado pode estar enfrentando latência extrema.")
else:
    st.info("👆 Clique no botão acima para puxar os dados reais da blockchain neste exato milissegundo.")