# -*- coding: utf-8 -*-
import os
import streamlit as st
import requests
import pandas as pd
import time

# Configuração da página para o Streamlit rodar lindo no Render
st.set_page_config(page_title="Painel VIP - Monitor Cripto", page_icon="📊")
st.title("📊 Painel Master de Monitoramento Cripto")
st.write("🤖 O robô do Edson está ativo na nuvem e monitorando o mercado...")

# ====== CONFIGURAÇÕES FIXAS E SEGURAS DO EDSON ======
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = "5402664067"

# Se o token não estiver cadastrado no Render, ele usa o seu token fixo de segurança
if not TELEGRAM_TOKEN:
    TELEGRAM_TOKEN = "8677343522:AAHjRanh8vdmQ4-FTZtEqDe2KvaolsAEMkE"

# Limites ultra sensíveis de teste para forçar o envio imediato
limite_forte_venda = 5.0      
limite_venda = 0.01            
limite_compra = -0.01          
limite_forte_compra = -4.0    

if 'historico' not in st.session_state:
    st.session_state.historico = {}

def enviar_mensagem_telegram(texto):
    try:
        url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": texto,
            "parse_mode": "Markdown"
        }
        headers = {"Connection": "close"}
        requests.post(url, json=payload, headers=headers, timeout=5)
    except Exception:
        pass

# GRADE FILTRADA APENAS COM AS MAIS POPULARES DO MERCADO EDSON
moedas = {
    "BTC-USD": "Bitcoin (BTC)",
    "ETH-USD": "Ethereum (ETH)",
    "XRP-USD": "XRP (XRP)",
    "SOL-USD": "Solana (SOL)",
    "LTC-USD": "Litecoin (LTC)",
    "BCH-USD": "Bitcoin Cash (BCH)",
    "DOGE-USD": "Dogecoin (DOGE)",
    "ADA-USD": "Cardano (ADA)"
}

# Laço principal de checagem
try:
    for ticker, nome_moeda in moedas.items():
        url = f"https://awesomeapi.com.br{ticker}"
        headers = {"Connection": "close"}
        resposta = requests.get(url, headers=headers, timeout=5)
        dados = resposta.json()
        
        chave_resposta = ticker.replace("-", "")
        
        if chave_resposta in dados:
            preco = float(dados[chave_resposta]['bid'])
            variacao = float(dados[chave_resposta]['pctChange'])
            
            sinal, msg_tele = "AGUARDAR 🟡", ""
            preco_txt = f"US$ {preco:,.4f}" if preco < 1.0 else f"US$ {preco:,.2f}"
            
            if variacao <= limite_forte_compra:
                sinal = "FORTE COMPRA 🔥"
                msg_tele = f"🚨 *ALERTA DA IA:* Edson, hora de *COMPRAR* {nome_moeda}!\n💰 Preço: {preco_txt}\n📉 Variação: {variacao:.2f}%"
            elif limite_forte_compra < variacao <= limite_compra:
                sinal = "COMPRAR 🟢"
                msg_tele = f"🟢 *ALERTA DA IA:* Oportunidade de *COMPRA* em {nome_moeda}.\n💰 Preço: {preco_txt}\n📉 Variação: {variacao:.2f}%"
            elif limite_venda <= variacao < limite_forte_venda:
                sinal = "VENDER 🔴"
                msg_tele = f"⚠️ *ALERTA DA IA:* Hora de lucro! *VENDA* {nome_moeda}.\n💰 Preço: {preco_txt}\n📈 Variação: +{variacao:.2f}%"
            elif variacao >= limite_forte_venda:
                sinal = "FORTE VENDA 🚨"
                msg_tele = f"🔥 *ALERTA URGENTE:* Subiu muito! Venda *TUDO* de {nome_moeda}!\n💰 Preço: {preco_txt}\n📈 Variação: +{variacao:.2f}%"
            
            if msg_tele:
                ultimo_sinal = st.session_state.historico.get(nome_moeda, "")
                if ultimo_sinal != sinal:
                    enviar_mensagem_telegram(msg_tele)
                    st.session_state.historico[nome_moeda] = sinal
            else:
                st.session_state.historico[nome_moeda] = "AGUARDAR 🟡"
except Exception:
    pass

st.write("✅ Verificação de moedas concluída com sucesso.")
