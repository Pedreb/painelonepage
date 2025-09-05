import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Painel de Capacidade Produtiva",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS customizado com as cores da empresa
st.markdown("""
<style>
    /* Importar fonte */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    /* Reset e configurações gerais */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Fonte global */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, #F7931E 0%, #e8821a 100%);
        padding: 2rem 2rem 2rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(247, 147, 30, 0.3);
    }

    .main-title {
        color: #000000;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    .main-subtitle {
        color: #000000;
        font-size: 1.1rem;
        font-weight: 400;
        margin: 0.5rem 0 0 0;
        text-align: center;
        opacity: 0.8;
    }

    /* Cards KPI */
    .kpi-container {
        display: flex;
        gap: 1.5rem;
        margin: 2rem 0;
        flex-wrap: wrap;
    }

    .kpi-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 5px solid #F7931E;
        flex: 1;
        min-width: 200px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }

    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #F7931E;
        margin: 0;
        line-height: 1;
    }

    .kpi-label {
        font-size: 0.9rem;
        color: #000000;
        font-weight: 600;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Seções regionais */
    .regional-section {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-top: 4px solid #F7931E;
    }

    .regional-title {
        color: #000000;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #F7931E;
    }

    /* Cards das equipes */
    .team-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }

    .team-card {
        background: white;
        border: 2px solid #f0f0f0;
        border-radius: 10px;
        padding: 1rem;
        transition: all 0.2s ease;
    }

    .team-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0,0,0,0.1);
    }

    .team-card.success {
        border-left: 5px solid #28a745;
        background: linear-gradient(135deg, #f8fff9 0%, #ffffff 100%);
    }

    .team-card.warning {
        border-left: 5px solid #F7931E;
        background: linear-gradient(135deg, #fffbf3 0%, #ffffff 100%);
    }

    .team-card.danger {
        border-left: 5px solid #dc3545;
        background: linear-gradient(135deg, #fff8f8 0%, #ffffff 100%);
    }

    .team-name {
        font-weight: 700;
        font-size: 1rem;
        color: #000000;
        margin-bottom: 0.5rem;
    }

    .team-performance {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }

    .performance.success { color: #28a745; }
    .performance.warning { color: #F7931E; }
    .performance.danger { color: #dc3545; }

    .team-details {
        font-size: 0.85rem;
        color: #666;
        margin-top: 0.5rem;
        line-height: 1.4;
    }

    /* Upload area */
    .upload-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border: 2px dashed #F7931E;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }

    /* Alertas */
    .alert {
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
    }

    .alert.warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 5px solid #F7931E;
        color: #000000;
    }

    /* Responsividade */
    @media (max-width: 768px) {
        .main-title { font-size: 2rem; }
        .kpi-container { flex-direction: column; }
        .team-grid { grid-template-columns: 1fr; }
    }

    /* Esconder elementos do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# Função para determinar o status da equipe
def get_team_status(percentual):
    if percentual >= 1.0:
        return "success", "✅"
    elif percentual >= 0.8:
        return "warning", "⚠️"
    else:
        return "danger", "🔴"


# Função para criar gauge chart
def create_gauge_chart(value, title, max_value=120):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'color': '#000000', 'size': 16}},
        delta={'reference': 100},
        gauge={
            'axis': {'range': [None, max_value], 'tickcolor': '#000000'},
            'bar': {'color': '#F7931E'},
            'steps': [
                {'range': [0, 80], 'color': 'rgba(220, 53, 69, 0.3)'},
                {'range': [80, 100], 'color': 'rgba(247, 147, 30, 0.3)'},
                {'range': [100, max_value], 'color': 'rgba(40, 167, 69, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#000000', 'family': 'Inter'}
    )

    return fig


# Função para criar gráfico de barras por equipe
def create_performance_chart(df, regional_title):
    df_sorted = df.sort_values('Percentual', ascending=True)

    colors = []
    for perc in df_sorted['Percentual']:
        if perc >= 1.0:
            colors.append('#28a745')
        elif perc >= 0.8:
            colors.append('#F7931E')
        else:
            colors.append('#dc3545')

    fig = go.Figure(data=[
        go.Bar(
            y=df_sorted['Equipe'],
            x=df_sorted['Percentual'] * 100,
            orientation='h',
            marker_color=colors,
            text=[f"{p:.1f}%" for p in df_sorted['Percentual'] * 100],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Performance: %{x:.1f}%<br>Meta: R$ %{customdata[0]:,.2f}<br>Faturado: R$ %{customdata[1]:,.2f}<extra></extra>',
            customdata=df_sorted[['Valor da Meta', 'Valor Faturado']].values
        )
    ])

    fig.update_layout(
        title=f'Performance por Equipe - {regional_title}',
        xaxis_title='Performance (%)',
        yaxis_title='',
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#000000', 'family': 'Inter'},
        title_font={'size': 16, 'color': '#000000'}
    )

    fig.add_vline(x=100, line_dash="dash", line_color="#000000", opacity=0.7)
    fig.add_annotation(x=100, y=len(df_sorted) - 1, text="Meta 100%", showarrow=False, xanchor="left")

    return fig


# Header principal
st.markdown("""
<div class="main-header">
    <h1 class="main-title">📊 PAINEL DE CAPACIDADE PRODUTIVA</h1>
    <p class="main-subtitle">Monitoramento de Performance das Equipes por Regional</p>
</div>
""", unsafe_allow_html=True)

# Upload do arquivo
st.markdown("""
<div class="upload-section">
    <h3 style="color: #F7931E; margin-bottom: 1rem;">📎 Carregar Planilha de Dados</h3>
    <p style="color: #666; margin-bottom: 1.5rem;">Faça upload do arquivo Excel com os dados de capacidade produtiva</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Selecione o arquivo Excel",
    type=['xlsx', 'xls'],
    help="Arquivo deve conter as colunas: Equipe, Valor Faturado, Valor da Meta, Percentual, Tipo de equipe, Regional, Principais Atividades, Dificuldades"
)

if uploaded_file is not None:
    try:
        # Ler o arquivo Excel
        df = pd.read_excel(uploaded_file)

        # Validar colunas necessárias
        required_columns = ['Equipe', 'Valor Faturado', 'Valor da Meta', 'Percentual', 'Regional']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"❌ Colunas obrigatórias ausentes: {', '.join(missing_columns)}")
        else:
            # Processar dados
            total_equipes = len(df)
            performance_media = df['Percentual'].mean() * 100
            equipes_acima_meta = len(df[df['Percentual'] > 1])
            equipes_criticas = len(df[df['Percentual'] < 0.8])
            faturamento_total = df['Valor Faturado'].sum()
            meta_total = df['Valor da Meta'].sum()

            # KPIs Principais
            st.markdown("""
            <div class="kpi-container">
                <div class="kpi-card">
                    <div class="kpi-value">{:.1f}%</div>
                    <div class="kpi-label">Performance Média</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{}</div>
                    <div class="kpi-label">Total de Equipes</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{}</div>
                    <div class="kpi-label">Acima da Meta</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{}</div>
                    <div class="kpi-label">Equipes Críticas</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">R$ {:.1f}M</div>
                    <div class="kpi-label">Faturamento Total</div>
                </div>
            </div>
            """.format(
                performance_media,
                total_equipes,
                equipes_acima_meta,
                equipes_criticas,
                faturamento_total / 1_000_000
            ), unsafe_allow_html=True)

            # Gauge de Performance Geral
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                gauge_fig = create_gauge_chart(performance_media, "Performance Geral da Organização")
                st.plotly_chart(gauge_fig, use_container_width=True)

            # Análise por Regional
            regionais = df['Regional'].unique()

            for regional in regionais:
                df_regional = df[df['Regional'] == regional]
                performance_regional = df_regional['Percentual'].mean() * 100

                st.markdown(f"""
                <div class="regional-section">
                    <h2 class="regional-title">🏢 {regional}</h2>
                </div>
                """, unsafe_allow_html=True)

                # Métricas da Regional
                col1, col2 = st.columns([1, 2])

                with col1:
                    equipes_reg = len(df_regional)
                    acima_meta_reg = len(df_regional[df_regional['Percentual'] > 1])
                    criticas_reg = len(df_regional[df_regional['Percentual'] < 0.8])

                    st.markdown(f"""
                    <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h4 style="color: #000000; margin-bottom: 1rem;">📈 Resumo da Regional</h4>
                        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                            <div><strong>Equipes:</strong> {equipes_reg}</div>
                            <div><strong>Performance:</strong> <span style="color: #F7931E; font-weight: 700;">{performance_regional:.1f}%</span></div>
                            <div><strong>Acima da Meta:</strong> <span style="color: #28a745;">{acima_meta_reg}</span></div>
                            <div><strong>Críticas:</strong> <span style="color: #dc3545;">{criticas_reg}</span></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    # Gráfico de performance por equipe
                    chart_fig = create_performance_chart(df_regional, regional)
                    st.plotly_chart(chart_fig, use_container_width=True)

                # Grid das equipes
                st.markdown('<div class="team-grid">', unsafe_allow_html=True)

                cols = st.columns(3)
                for idx, (_, equipe) in enumerate(df_regional.iterrows()):
                    col_idx = idx % 3

                    with cols[col_idx]:
                        status, icon = get_team_status(equipe['Percentual'])
                        performance_perc = equipe['Percentual'] * 100

                        # Preparar atividades e dificuldades
                        atividades = equipe.get('Principais Atividades', 'N/A')
                        if pd.isna(atividades):
                            atividades = 'N/A'

                        dificuldades = equipe.get('Dificuldades', 'Nenhuma relatada')
                        if pd.isna(dificuldades):
                            dificuldades = 'Nenhuma relatada'

                        st.markdown(f"""
                        <div class="team-card {status}">
                            <div class="team-name">{icon} {equipe['Equipe']}</div>
                            <div class="team-performance performance {status}">{performance_perc:.1f}%</div>
                            <div class="team-details">
                                <strong>Meta:</strong> R$ {equipe['Valor da Meta']:,.2f}<br>
                                <strong>Faturado:</strong> R$ {equipe['Valor Faturado']:,.2f}<br>
                                <strong>Tipo:</strong> {equipe.get('Tipo de equipe', 'N/A')}<br>
                                <strong>Atividades:</strong> {atividades[:100]}{'...' if len(str(atividades)) > 100 else ''}<br>
                                <strong>Dificuldades:</strong> {str(dificuldades)[:100]}{'...' if len(str(dificuldades)) > 100 else ''}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

            # Alertas e Insights
            if equipes_criticas > 0:
                st.markdown(f"""
                <div class="alert warning">
                    <strong>⚠️ Atenção:</strong> {equipes_criticas} equipe(s) com performance crítica (abaixo de 80%). 
                    Recomenda-se análise detalhada das dificuldades reportadas e plano de ação para melhoria.
                </div>
                """, unsafe_allow_html=True)

            # Footer com timestamp
            from datetime import datetime

            st.markdown(f"""
            <div style="text-align: center; color: #666; font-size: 0.8rem; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #eee;">
                📅 Última atualização: {datetime.now().strftime('%d/%m/%Y às %H:%M')}
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
        st.info("🔧 Verifique se o arquivo está no formato correto e tente novamente.")

else:
    st.markdown("""
    <div class="alert warning">
        <strong>📋 Instruções:</strong><br>
        1. Faça upload do arquivo Excel com os dados das equipes<br>
        2. O arquivo deve conter as colunas: Equipe, Valor Faturado, Valor da Meta, Percentual, Regional, etc.<br>
        3. O painel será gerado automaticamente após o upload
    </div>
    """, unsafe_allow_html=True)

# Sidebar com informações
with st.sidebar:
    st.markdown("""
    ### 📊 Painel de Capacidade

    **Cores utilizadas:**
    - 🟠 Laranja: Cor principal da empresa
    - ⚫ Preto: Textos e detalhes
    - 🟢 Verde: Equipes acima da meta
    - 🟡 Amarelo: Equipes em atenção
    - 🔴 Vermelho: Equipes críticas

    **Critérios de Performance:**
    - ✅ **Sucesso:** ≥ 100% da meta
    - ⚠️ **Atenção:** 80-99% da meta  
    - 🔴 **Crítico:** < 80% da meta
    """)