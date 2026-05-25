# CaptAI Leads — Copiloto Comercial para Feiras

MVP em Streamlit para registrar a fala de um visitante, identificar sua necessidade comercial e sugerir um produto ao atendente.

## Funções da versão inicial

- Campo para digitar a fala do visitante.
- Recomendação de produto com catálogo configurável.
- Classificação simples do lead: frio, morno, quente ou prioritário.
- Dashboard da sessão.
- Exportação dos resultados para CSV.

> Esta primeira versão usa regras comerciais transparentes, sem banco de dados e sem API. Antes de usar em situação real, substitua o catálogo demonstrativo por soluções aprovadas pela empresa e defina regras de privacidade/LGPD.

## Estrutura

```text
captai-leads-feira/
├── app.py
├── requirements.txt
└── dados/
    └── produtos.csv
```

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar no Streamlit Community Cloud

1. Envie estes arquivos para um repositório no GitHub.
2. Entre no Streamlit Community Cloud usando sua conta GitHub.
3. Clique em **Create app**.
4. Escolha o repositório e informe `app.py` como arquivo principal.
5. Clique em **Deploy**.
