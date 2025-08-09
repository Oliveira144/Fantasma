import streamlit as st
import json
import statistics
from typing import List, Dict, Tuple

# --------------------------------------
# Configuração da Aplicação Streamlit
# --------------------------------------

st.set_page_config(
    page_title="Detector de Padrões - Football Studio",
    layout="wide",
    page_icon="🎯"
)

# --------------------------------------
# Constantes e Estado da Sessão
# --------------------------------------

EMOJIS = {'V': '🔴', 'A': '🔵', 'E': '🟡'}
MAX_HISTORY = 200
DEFAULT_WINDOW = 50

# Inicializa o estado da sessão para armazenar o histórico
if 'history' not in st.session_state:
    st.session_state.history = []

# --------------------------------------
# Funções de Gerenciamento de Histórico
# --------------------------------------

def add_result(code: str):
    """Adiciona um resultado ao histórico."""
    st.session_state.history.insert(0, code)
    if len(st.session_state.history) > MAX_HISTORY:
        st.session_state.history.pop()

def undo():
    """Remove o último resultado do histórico."""
    if st.session_state.history:
        st.session_state.history.pop(0)

def reset_history():
    """Limpa todo o histórico."""
    st.session_state.history = []

# --------------------------------------
# Funções de Análise e Métricas
# --------------------------------------

def windowed_list(history: List[str], window: int) -> List[str]:
    """Retorna uma sublista do histórico com base na janela."""
    return history[:window]

def compute_runs(history: List[str]) -> List[int]:
    """Calcula o comprimento das sequências (runs) ignorando empates."""
    runs = []
    if not history:
        return runs
    
    # Filtra empates para análise de runs
    filtered_history = [r for r in history if r != 'E']
    if not filtered_history:
        return []

    current_run_length = 1
    for i in range(1, len(filtered_history)):
        if filtered_history[i] == filtered_history[i-1]:
            current_run_length += 1
        else:
            runs.append(current_run_length)
            current_run_length = 1
    runs.append(current_run_length)
    return runs

def frequency_counts(history: List[str]) -> Dict[str, int]:
    """Retorna a contagem de cada resultado (V, A, E)."""
    counts = {'V': 0, 'A': 0, 'E': 0}
    for result in history:
        counts[result] += 1
    return counts

def alternation_score(history: List[str]) -> float:
    """Calcula a pontuação de alternância entre V e A."""
    alternations = 0
    total_pairs = 0
    
    # Filtra empates
    filtered_history = [r for r in history if r != 'E']
    if len(filtered_history) < 2:
        return 0.0

    for i in range(1, len(filtered_history)):
        total_pairs += 1
        if filtered_history[i] != filtered_history[i-1]:
            alternations += 1
            
    return alternations / total_pairs if total_pairs > 0 else 0.0

def avg_run_length(history: List[str]) -> float:
    """Calcula o comprimento médio das sequências (runs)."""
    runs = compute_runs(history)
    return statistics.mean(runs) if runs else 0.0

def tie_positions(history: List[str], window: int) -> List[int]:
    """Encontra as posições dos empates na janela."""
    return [i for i, r in enumerate(windowed_list(history, window)) if r == 'E']

# --------------------------------------
# Funções de Classificação e Sugestão
# --------------------------------------

def classify_patterns(history: List[str], window: int) -> Tuple[str, float]:
    """Analisa o histórico e classifica o padrão do jogo."""
    w = windowed_list(history, window)
    if not w:
        return "Indefinido", 0.0

    freq = frequency_counts(w)
    total = len(w)
    v_ratio = freq['V'] / total
    a_ratio = freq['A'] / total
    e_ratio = freq['E'] / total

    alt_score = alternation_score(w)
    avg_run = avg_run_length(w)
    
    # Regras e Heurísticas
    if avg_run >= 3.0 and e_ratio < 0.05:
        conf = min(1.0, (avg_run - 2.0) / 4.0 + (max(v_ratio, a_ratio) - 0.5))
        return "Sequência Forçada", max(0.15, conf)
    
    if alt_score >= 0.6 and avg_run <= 1.5 and e_ratio < 0.1:
        return "Alternância Equilibrada", alt_score
    
    if e_ratio >= 0.06 and any(i < 8 for i in tie_positions(w, window)):
        conf = min(1.0, e_ratio * 5 + (1 - alt_score) * 0.3)
        return "Ancoragem por Empate", conf
    
    if avg_run >= 3.0 and e_ratio >= 0.05 and alt_score < 0.4:
        conf = 0.5 + (avg_run - 3) * 0.1
        return "Inversão Psicológica", min(1.0, conf)
        
    balance_conf = 1 - abs(v_ratio - a_ratio)
    return "Balanceado / Aleatório", max(0.1, balance_conf * 0.9)

def predict_next(history: List[str], window: int) -> Dict[str, float]:
    """Prevê as probabilidades do próximo resultado com base em heurísticas."""
    w = windowed_list(history, window)
    if not w:
        return {'V': 0.48, 'A': 0.48, 'E': 0.04}

    counts = frequency_counts(w)
    total = len(w)
    p = {k: counts.get(k, 0) / total for k in EMOJIS.keys()}
    
    avg_run = avg_run_length(w)
    alt = alternation_score(w)
    last = w[0] if w else None
    
    # Ajustes heurísticos
    if last in ('V', 'A') and avg_run >= 3.0:
        opp = 'A' if last == 'V' else 'V'
        adjustment = 0.25 * min(1.0, (avg_run - 2) / 4)
        p[opp] += adjustment
        p['E'] += adjustment / 2
        p[last] -= adjustment * 1.5
        
    if alt >= 0.6:
        switch_prob = 0.08
        p['V'] += switch_prob / 2
        p['A'] += switch_prob / 2
        
    # Normaliza e garante que os valores sejam válidos
    for k in p:
        p[k] = max(0.0, p[k])
    
    total_prob = sum(p.values())
    if total_prob == 0:
        return {'V': 0.48, 'A': 0.48, 'E': 0.04}
    
    return {k: round(v / total_prob, 3) for k, v in p.items()}

def get_suggestion(history: List[str], window: int) -> Tuple[str, Dict[str, float], float]:
    """Combina as análises para fornecer uma sugestão de aposta."""
    baralho, bar_conf = classify_patterns(history, window)
    preds = predict_next(history, window)
    
    # Uma confiança baseada apenas na análise de padrão já é suficiente e menos complexa
    conf = bar_conf
    
    last = history[0] if history else None
    
    if conf < 0.35:
        return "Evitar aposta — confiança baixa na análise.", preds, conf
        
    if baralho == "Sequência Forçada" and last in ('V', 'A'):
        opp = 'A' if last == 'V' else 'V'
        if preds[opp] > preds[last]:
            return f"Sugerir aposta em {EMOJIS[opp]} — possível quebra de sequência.", preds, conf
            
    if baralho == "Ancoragem por Empate" and preds['E'] > 0.1:
        return "Sugerir atenção ao Empate 🟡 — pode ser o próximo resultado.", preds, conf
        
    if baralho == "Alternância Equilibrada" and last in ('V', 'A'):
        opp = 'A' if last == 'V' else 'V'
        if preds[opp] > preds[last]:
            return f"Sugerir aposta em {EMOJIS[opp]} — esperar alternância.", preds, conf
            
    return "Observar — padrão sem sugestão forte.", preds, conf

# --------------------------------------
# Interface do Usuário (UI) Streamlit
# --------------------------------------

def render_ui():
    """Renderiza a interface principal do aplicativo."""
    st.title("Detector de Padrões - Football Studio")
    
    col_input, col_display = st.columns([1, 2])
    
    with col_input:
        st.subheader("Inserir Resultado")
        c1, c2, c3 = st.columns(3)
        c1.button(f"{EMOJIS['V']} Vermelho (V)", on_click=add_result, args=['V'])
        c2.button(f"{EMOJIS['A']} Azul (A)", on_click=add_result, args=['A'])
        c3.button(f"{EMOJIS['E']} Empate (E)", on_click=add_result, args=['E'])

        st.markdown("---")
        st.button("Desfazer último", on_click=undo)
        st.button("Resetar histórico", on_click=reset_history)

        st.markdown("---")
        st.subheader("Importar / Exportar")
        hist_json = json.dumps(st.session_state.history)
        st.download_button("Exportar histórico (JSON)", hist_json, file_name="history_football_studio.json")

        uploaded = st.file_uploader("Importar histórico (JSON)", type=['json'])
        if uploaded:
            try:
                data = json.load(uploaded)
                if isinstance(data, list):
                    st.session_state.history = data[:MAX_HISTORY]
                    st.success("Histórico importado com sucesso!")
                else:
                    st.error("Formato inválido. O arquivo JSON deve ser uma lista.")
            except Exception as e:
                st.error(f"Erro ao importar: {e}")

    with col_display:
        st.subheader("Histórico (Mais Recente à Esquerda)")
        if not st.session_state.history:
            st.info("Nenhum resultado ainda. Use os botões ao lado para começar a análise.")
        else:
            # Exibe o histórico em formato de linhas
            per_row = 9
            history_display = st.session_state.history[:per_row * 10]
            for i in range(0, len(history_display), per_row):
                row_cols = st.columns(per_row)
                for j, result in enumerate(history_display[i:i + per_row]):
                    row_cols[j].markdown(f"### {EMOJIS[result]}")

            st.markdown("---")
            st.subheader("Análise & Diagnóstico")
            window = st.slider(
                "Janela de análise (rodadas mais recentes)",
                min_value=12,
                max_value=MAX_HISTORY,
                value=DEFAULT_WINDOW
            )
            
            baralho, bar_conf = classify_patterns(st.session_state.history, window)
            suggestion, preds, conf = get_suggestion(st.session_state.history, window)

            st.metric("Padrão de Jogo", baralho, delta=f"Confiança: {int(bar_conf * 100)}%")
            
            st.markdown("**Probabilidade Prevista (Próxima Rodada)**")
            cols_prob = st.columns(3)
            for i, (key, value) in enumerate(preds.items()):
                cols_prob[i].progress(int(value * 100))
                cols_prob[i].write(f"{EMOJIS[key]} {key} — {value * 100:.1f}%")

            st.markdown("---")
            st.markdown(f"**Sugestão:** {suggestion}")
            st.info(f"**Confiança global da análise:** {int(conf * 100)}%")

            st.markdown("---")
            st.write("**Métricas Técnicas**")
            w_list = windowed_list(st.session_state.history, window)
            st.json({
                'Janela': window,
                'Tamanho histórico': len(st.session_state.history),
                'Frequência na janela': frequency_counts(w_list),
                'Alternância': round(alternation_score(w_list), 3),
                'Média de runs (sem empates)': round(avg_run_length(w_list), 3),
                'Posições de empate (0=mais recente)': tie_positions(w_list, window)
            })

    st.sidebar.title("Sobre este Detector")
    st.sidebar.markdown(
        "Esta é uma ferramenta para **estudo de padrões** no jogo Football Studio. "
        "Ela usa heurísticas simples para classificar o comportamento do baralho "
        "e sugerir possíveis cenários futuros. As sugestões são baseadas em regras e "
        "não garantem resultados. Aumente a janela de análise para obter "
        "resultados mais confiáveis."
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("Feito com Python e Streamlit.")

if __name__ == "__main__":
    render_ui()
