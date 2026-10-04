import time
import requests
import pandas as pd
import streamlit as st
from binance.spot import Spot

# Configuração da página web limpa e centralizada
st.set_page_config(page_title="Painel VIP - Monitor Cripto", page_icon="📊")

# --- CONFIGURAÇÕES DO TELEGRAM ---
TELEGRAM_TOKEN = "8953605979:AAFC71l9tvXkb-iFJZWeRo5Ga3rWB2DhAoo"
TELEGRAM_CHAT_ID = "5402664067"

MOEDAS_MONITORADAS = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'PEPEUSDT',
    'SOLUSDT', 'LTCUSDT', 'BCHUSDT', 'DOGEUSDT', 'ZECUSDT'
]

# Deixamos o limite super sensível para você ver os alertas pipocarem no celular a cada minuto
LIMITE_ALERTA_PERCENTUAL = 0.001

# Inicializa as memórias de histórico e controle de conexões do Streamlit
if 'precos_anteriores' not in st.session_state:
    st.session_state.precos_anteriores = {}
if 'sistema_iniciado' not in st.session_state:
    st.session_state.sistema_iniciado = False

def enviar_mensagem_telegram(mensagem):
    """Envia as notificações de forma direta e independente do loop visual."""
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": str(TELEGRAM_CHAT_ID),
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    try:
        # Usamos uma requisição rápida para o Telegram não travar a renderização do site
        resposta = requests.post(url, json=payload, timeout=5)
        return resposta.status_code == 200
    except Exception:
        return False

def puxar_dados_binance():
    """Conecta com a Binance para obter os dados de mercado limpos e formatados."""
    try:
        cliente = Spot()
        dados = cliente.ticker_24hr()
        
        linhas = []
        precos_dict = {}
        
        for item in dados:
            simbolo = item['symbol']
            if simbolo in MOEDAS_MONITORADAS:
                preco_atual = float(item['lastPrice'])
                variacao_24h = float(item['priceChangePercent'])
                volume = float(item['volume'])
                
                precos_dict[simbolo] = preco_atual
                
                if preco_atual < 0.001:
                    preco_exibicao = f"{preco_atual:,.8f}"
                elif preco_atual < 1.0:
                    preco_exibicao = f"{preco_atual:,.4f}"
                else:
                    preco_exibicao = f"{preco_atual:,.2f}"
                
                linhas.append({
                    "Criptomoeda": simbolo.replace("USDT", ""),
                    "Preço Atual (USD)": preco_exibicao,
                    "Variação (24h)": variacao_24h,
                    "Volume (24h)": volume
                })
                    
        return pd.DataFrame(linhas), precos_dict
    except Exception:
        return None, None

# --- DESIGN DO PAINEL WEB COMERCIAL ---
st.title("⚡ Painel de Monitoramento VIP")
st.markdown("Cotações em tempo real com alertas automáticos enviados para o Telegram.")
st.markdown("---")

# CORREÇÃO: Dispara a mensagem de teste de forma isolada na inicialização do servidor
if not st.session_state.sistema_iniciado:
    sucesso = enviar_mensagem_telegram("🚀 *Sistema Tudo-em-Um Conectado!* \nSeu robô está monitorando o mercado e o envio em segundo plano está ativo.")
    if sucesso:
        st.session_state.sistema_iniciado = True

placeholder = st.empty()

df_cripto, dados_precos = puxar_dados_binance()

if dados_precos and df_cripto is not None:
    with placeholder.container():
        # Indicadores de topo compactos
        col1, col2, col3 = st.columns(3)
        col1.metric("Ativos Monitorados", f"{len(MOEDAS_MONITORADAS)} Moedas")
        col2.metric("Status do Bot", "Conectado e Ativo 🤖")
        col3.metric("Última Atualização", time.strftime('%H:%M:%S'))
        
        st.markdown("###")
        
        # PROCESSAMENTO E DISPARO REAL DE ALERTAS PARA O TELEGRAM
        for moeda, preco_atual in dados_precos.items():
            if moeda in st.session_state.precos_anteriores:
                preco_antigo = st.session_state.precos_anteriores[moeda]
                if preco_antigo > 0:
                    variacao_minuto = ((preco_atual - preco_antigo) / preco_antigo) * 100
                    
                    if abs(variacao_minuto) >= LIMITE_ALERTA_PERCENTUAL:
                        fmt = "{:,.8f}" if preco_atual < 0.01 else "{:,.2f}"
                        alerta_msg = (
                            f"🚨 *MOVIMENTAÇÃO DETECTADA!* 🚨\n\n"
                            f"🪙 *Moeda:* {moeda.replace('USDT', '')}\n"
                            f"📊 *Variação:* `{variacao_minuto:.4f}%` no minuto\n"
                            f"💰 *Preço Atual:* \$ {fmt.format(preco_atual)}\n"
                            f"📉 *Preço Anterior:* \$ {fmt.format(preco_antigo)}"
                        )
                        enviar_mensagem_telegram(alerta_msg)
            
            # Alimenta a memória a cada minuto para rastrear o próximo movimento
            st.session_state.precos_anteriores[moeda] = preco_atual

        # TABELA COMERCIAL SIMPLIFICADA E ALINHADA CENTRADA
        if not df_cripto.empty:
            def aplicar_cores(val):
                if val > 0:
                    return 'color: #00cc66; font-weight: bold;'
                elif val < 0:
                    return 'color: #ff3333; font-weight: bold;'
                return 'color: white;'

            col_esq, col_centro, col_dir = st.columns([1, 4, 1])
            
            with col_centro:
                st.dataframe(
                    df_cripto.style.applymap(aplicar_cores, subset=['Variação (24h)']),
                    column_config={
                        "Criptomoeda": st.column_config.TextColumn("Criptomoeda"),
                        "Preço Atual (USD)": st.column_config.TextColumn("Preço Atual (USD)"),
                        "Variação (24h)": st.column_config.NumberColumn("Variação (24h)", format="%.2f%%"),
                        "Volume (24h)": st.column_config.NumberColumn("Volume (24h)", format="%,.0f")
                    },
                    use_container_width=True,
                    hide_index=True
                )

# Atualização contínua a cada 60 segundos
time.sleep(60)
st.rerun()
