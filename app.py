import re
import unicodedata
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="CaptAI Leads | Feira",
    page_icon="🎯",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
    .hero {
        padding: 1.3rem 1.5rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #072a58, #075da8);
        color: white;
        margin-bottom: 1rem;
    }
    .hero h1 {margin: 0; font-size: 2.1rem;}
    .hero p {margin: .4rem 0 0 0; opacity: .94;}
    .card {
        padding: 1rem;
        border: 1px solid #e6edf5;
        border-radius: 14px;
        background: #ffffff;
        min-height: 124px;
    }
    .label {font-size: .82rem; color: #516276; font-weight: 600;}
    .value {font-size: 1.18rem; font-weight: 700; color: #082f59; margin-top: .35rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def carregar_catalogo():
    return pd.read_csv("dados/produtos.csv")

def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9\s]", " ", texto)

def classificar_lead(texto: str) -> tuple[str, str]:
    texto = normalizar(texto)
    prioritario = ["urgente", "fechar hoje", "contratar agora", "este mes", "essa semana", "implantacao imediata"]
    quente = ["preco", "valor", "proposta", "orcamento", "contratar", "implantar", "quanto custa", "demonstracao"]
    morno = ["preciso", "problema", "dificuldade", "gostaria", "buscando", "queremos", "necessito"]
    frio = ["so olhando", "apenas conhecendo", "curiosidade", "passeando"]

    if any(item in texto for item in prioritario):
        return "Prioritário", "Solicitar autorização para coletar contato e encaminhar ao comercial."
    if any(item in texto for item in quente):
        return "Quente", "Apresentar solução e solicitar autorização para envio de proposta."
    if any(item in texto for item in frio):
        return "Frio", "Apresentar brevemente a empresa e investigar necessidade."
    if any(item in texto for item in morno):
        return "Morno", "Fazer pergunta de diagnóstico para amadurecer a oportunidade."
    return "Exploratório", "Continuar a conversa para identificar uma necessidade real."

def detectar_receptividade(texto: str) -> str:
    texto = normalizar(texto)
    positivos = ["interessante", "gostei", "resolve", "otimo", "perfeito", "quero saber", "faz sentido"]
    frustracoes = ["insatisfeito", "ruim", "problema", "perdendo", "nao consigo", "demora", "falha"]
    if any(item in texto for item in positivos):
        return "Receptivo"
    if any(item in texto for item in frustracoes):
        return "Dor identificada"
    return "Neutro"

def recomendar_produto(texto: str, catalogo: pd.DataFrame) -> pd.Series:
    texto_norm = normalizar(texto)
    melhor_indice = None
    melhor_pontos = 0

    for indice, linha in catalogo.iterrows():
        palavras = [normalizar(p.strip()) for p in linha["palavras_chave"].split(",")]
        pontos = sum(1 for palavra in palavras if palavra and palavra in texto_norm)
        if pontos > melhor_pontos:
            melhor_pontos = pontos
            melhor_indice = indice

    if melhor_indice is None:
        return pd.Series(
            {
                "necessidade": "Necessidade ainda não identificada",
                "produto": "Apresentação geral das soluções",
                "pergunta": "Qual desafio de comunicação ou atendimento sua empresa enfrenta hoje?",
            }
        )
    return catalogo.loc[melhor_indice]

def registrar_analise(mensagem: str, recomendacao: pd.Series, lead: str, receptividade: str):
    registro = {
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "mensagem_visitante": mensagem,
        "necessidade": recomendacao["necessidade"],
        "produto_sugerido": recomendacao["produto"],
        "lead": lead,
        "receptividade": receptividade,
    }
    st.session_state.historico.append(registro)

catalogo = carregar_catalogo()
if "historico" not in st.session_state:
    st.session_state.historico = []

st.markdown(
    """
    <div class="hero">
        <h1>🎯 CaptAI Leads</h1>
        <p>Copiloto comercial para qualificação de visitantes em feiras</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "MVP demonstrativo: a recomendação atual usa regras comerciais e catálogo configurável. "
    "Não registre telefone, e-mail ou dados pessoais nesta tela."
)

aba_analise, aba_dashboard, aba_catalogo = st.tabs(
    ["Analisar conversa", "Dashboard da feira", "Catálogo usado"]
)

with aba_analise:
    esquerda, direita = st.columns([1.08, 0.92], gap="large")

    with esquerda:
        st.subheader("Fala do visitante")
        with st.form("form_conversa", clear_on_submit=False):
            mensagem = st.text_area(
                "Digite a principal mensagem do potencial cliente:",
                height=155,
                placeholder="Exemplo: Tenho 12 vendedores usando celular próprio e preciso controlar as ligações. Vocês enviam proposta?",
            )
            analisar = st.form_submit_button("Analisar oportunidade", type="primary", use_container_width=True)

    with direita:
        st.subheader("Orientação ao atendente")
        if analisar:
            if not mensagem.strip():
                st.warning("Digite uma mensagem do visitante para analisar.")
            else:
                recomendacao = recomendar_produto(mensagem, catalogo)
                lead, acao = classificar_lead(mensagem)
                receptividade = detectar_receptividade(mensagem)
                registrar_analise(mensagem, recomendacao, lead, receptividade)

                a, b = st.columns(2)
                with a:
                    st.markdown(
                        f'<div class="card"><div class="label">Potencial do lead</div>'
                        f'<div class="value">{lead}</div></div>',
                        unsafe_allow_html=True,
                    )
                with b:
                    st.markdown(
                        f'<div class="card"><div class="label">Sinal da conversa</div>'
                        f'<div class="value">{receptividade}</div></div>',
                        unsafe_allow_html=True,
                    )

                st.markdown("#### Produto sugerido")
                st.success(recomendacao["produto"])
                st.markdown("**Necessidade identificada:** " + recomendacao["necessidade"])
                st.info("**Pergunta sugerida:** " + recomendacao["pergunta"])
                st.markdown("**Próxima ação:** " + acao)
        else:
            st.info("O resultado aparecerá aqui após a análise.")

with aba_dashboard:
    st.subheader("Indicadores da demonstração")
    if not st.session_state.historico:
        st.info("Nenhuma conversa analisada nesta sessão.")
    else:
        historico = pd.DataFrame(st.session_state.historico)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Conversas", len(historico))
        c2.metric("Leads quentes", int((historico["lead"] == "Quente").sum()))
        c3.metric("Prioritários", int((historico["lead"] == "Prioritário").sum()))
        c4.metric("Produtos indicados", historico["produto_sugerido"].nunique())

        st.markdown("#### Produtos mais sugeridos")
        st.bar_chart(historico["produto_sugerido"].value_counts())

        st.markdown("#### Histórico da sessão")
        st.dataframe(historico, use_container_width=True, hide_index=True)

        st.download_button(
            "Baixar resultados da sessão em CSV",
            data=historico.to_csv(index=False).encode("utf-8-sig"),
            file_name="captai_resultados_feira.csv",
            mime="text/csv",
        )

with aba_catalogo:
    st.subheader("Produtos demonstrativos")
    st.warning("Substitua este catálogo pelos produtos reais aprovados pela empresa antes da feira.")
    st.dataframe(
        catalogo[["produto", "necessidade", "pergunta"]],
        use_container_width=True,
        hide_index=True,
    )
