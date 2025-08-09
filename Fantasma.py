import streamlit as st
import collections
import json
import math
from typing import List, Tuple, Dict
import statistics

# --------------------------------------

# Football Studio — Tipo de Baralho + Estratégia

# Streamlit app (single-file)

# Como usar: salvar como Football_Studio_Detector_Streamlit.py

# executar: streamlit run Football_Studio_Detector_Streamlit.py

# --------------------------------------

st.set_page_config(page_title="Detector de Baralho & Estratégia - Football Studio", layout="wide", page_icon="🎯")

# -----------------------------

# Helpers

# -----------------------------

EMOJI = {'V': '🔴', 'A': '🔵', 'E': '🟡'}  # V = Vermelho, A = Azul, E = Empate
MAX_HISTORY = 200
DEFAULT_WINDOW = 50
MIN_WINDOW = 12  # mínimo recomendado para análise

@st.cache_data
def empty_state():
    return {'history': []}

# Persistent state in session
if 'state' not in st.session_state:
    st.session_state.state = empty_state()

# Add result to history
def add_result(code: str):
    hist = st.session_state.state['history']
    hist.insert(0, code)  # mais recente à esquerda
    if len(hist) > MAX_HISTORY:
        hist.pop()
    st.session_state.state['history'] = hist

def undo():
    hist = st.session_state.state['history']
    if hist:
        hist.pop(0)
    st.session_state.state['history'] = hist

def reset_history():
    st.session_state.state['history'] = []

# Metrics

def windowed_list(history: List[str], window: int) -> List[str]:
    return history[:window]

def compute_runs(history: List[str]) -> List[int]:
    # runs lengths ignoring ties (E) optionally
    runs = []
    if not history:
        return runs
    cur = history[0]
    count = 1
    for r in history[1:]:
        if r == cur:
            count += 1
        else:
            runs.append(count)
            cur = r
            count = 1
    runs.append(count)
    return runs

def frequency_counts(history: List[str]) -> Dict[str, int]:
    return {k: history.count(k) for k in ['V', 'A', 'E']}

def alternation_score(history: List[str]) -> float:
    # measure how often sequence alternates (V->A or A->V) ignoring empates
    pairs = 0
    alt = 0
    prev = None
    for r in history:
        if r == 'E':
            prev = r
            continue
        if prev is None or prev == 'E':
            prev = r
            continue
        pairs += 1
        if r != prev:
            alt += 1
        prev = r
    return (alt / pairs) if pairs > 0 else 0.0

def avg_run_length(history: List[str]) -> float:
    runs = compute_runs([x for x in history if x != 'E'])
    return statistics.mean(runs) if runs else 0.0

def tie_positions(history: List[str], window:int) -> List[int]:
    # positions (index) where ties appear in the window (0 = most recent)
    return [i for i, r in enumerate(windowed_list(history, window)) if r == 'E']

# Classification of baralho types

def classify_baralho(history: List[str], window:int) -> Tuple[str, float]:
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

    # heurísticas simples com score de confiança (0..1)
    if avg_run >= 3.0 and e_ratio < 0.05:
        # repetição forçada
        conf = min(1.0, (avg_run - 2.0) / 4.0 + (max(v_ratio,a_ratio) - 0.5))
        return "Repetição Forçada", max(0.15, conf)
    if alt_score >= 0.6 and avg_run <= 1.5 and e_ratio < 0.1:
        conf = alt_score
        return "Alternância Equilibrada", conf
    if e_ratio >= 0.06 and any(i < 8 for i in tie_positions(w, window)):
        conf = min(1.0, e_ratio * 5 + (1 - alt_score)*0.3)
        return "Ancoragem por Empate", conf
    if avg_run >= 3.0 and e_ratio >= 0.05 and alt_score < 0.4:
        conf = 0.5 + (avg_run - 3) * 0.1
        return "Inversão Psicológica", min(1.0, conf)
    # fallback - baralho balanceado
    balance_conf = 1 - abs(v_ratio - a_ratio)
    return "Balanceado / Indefinido", max(0.1, balance_conf * 0.9)

# Detect strategy

def detect_strategy(history: List[str], window:int) -> Tuple[str, float]:
    w = windowed_list(history, window)
    if not w:
        return "Indefinido", 0.0
    avg_run = avg_run_length(w)
    alt = alternation_score(w)
    ties = frequency_counts(w)['E']
    last6 = w[:6]

    # isco-reversao: sequência curta seguida de quebra súbita
    runs_last6 = compute_runs(last6)
    if avg_run >= 2.5 and len(last6) >= 4 and runs_last6 and runs_last6[0] >= 3:
        return "Isco-Reversão", 0.7
    # ruído controlado: muita alternância e ties
    if alt >= 0.55 and ties/len(w) > 0.03:
        conf = 0.4 + alt*0.5
        return "Ruído Controlado", min(1.0, conf)
    # ciclo escalonado
    if avg_run > 1.8 and alt > 0.3:
        return "Ciclo Escalonado", 0.5
    # padrão fantasma (parece lógico mas está próximo da aleatoriedade)
    if abs(frequency_counts(w)['V'] - frequency_counts(w)['A']) <= 3 and alt > 0.35:
        return "Padrão Fantasma", 0.45
    return "Estratégia Indefinida", 0.2

# Prediction: prever chance de quebra (empate ou inversão)

def predict_next(history: List[str], window:int) -> Dict[str, float]:
    w = windowed_list(history, window)
    counts = frequency_counts(w)
    total = len(w) if len(w) > 0 else 1
    base = {k: counts.get(k,0)/total for k in ['V','A','E']}
    avg_run = avg_run_length(w)
    alt = alternation_score(w)
    last = w[0] if w else None
    p = base.copy()

    # Ajustes heurísticos:
    if last in ('V','A') and avg_run >= 3.0:
        # penaliza continuação; favorece inversão e empate
        opp = 'A' if last == 'V' else 'V'
        fator = min(1.0, (avg_run-2)/4)
        p[opp] += 0.20 * fator
        p['E'] += 0.10 * fator
        p[last] -= 0.25 * fator

    if alt >= 0.6:
        # alternância sugere continuação do alternar
        p_switch = 0.08
        p['V'] += p_switch/2
        p['A'] += p_switch/2

    # Normalizar e garantir não-negatividade
    for k in p:
        if p[k] < 0:
            p[k] = 0.0
    s = sum(p.values())
    if s == 0:
        p = {'V':0.48,'A':0.48,'E':0.04}
        s = 1
    for k in p:
        p[k] = round(p[k]/s, 3)

    return p

# Confidence scoring for suggestion

def compute_confidence(baralho_conf: float, strat_conf: float, history_len:int) -> float:
    base = 0.6*baralho_conf + 0.4*strat_conf
    penalty = 0.0
    if history_len < MIN_WINDOW:
        penalty = (MIN_WINDOW - history_len) / 30
    conf = max(0.0, min(1.0, base - penalty))
    return round(conf, 3)

# Suggestion engine

def suggest_action(history: List[str], window:int) -> Tuple[str, Dict[str,float], float]:
    baralho, bar_conf = classify_baralho(history, window)
    strat, strat_conf = detect_strategy(history, window)
    preds = predict_next(history, window)
    conf = compute_confidence(bar_conf, strat_conf, len(history))

    last = history[0] if history else None

    if conf < 0.35:
        return ("Evitar aposta — confiança baixa", preds, conf)

    if baralho == "Repetição Forçada" and last in ('V','A'):
        opp = 'A' if last == 'V' else 'V'
        return (f"Sugerir apostar em {EMOJI[opp]} (contra a sequência)", preds, conf)

    if baralho == "Ancoragem por Empate" and preds['E'] > 0.06:
        return ("Sugerir: atenção ao Empate 🟡 — possível interrupção", preds, conf)

    if baralho == "Alternância Equilibrada":
        opp = 'A' if last == 'V' else 'V'
        return (f"Sugerir apostar em {EMOJI[opp]} (espera alternância)", preds, conf)

    return ("Observar — sem sugestão forte", preds, conf)

# -----------------------------

# Streamlit UI

# -----------------------------

st.title("Detector de Baralho & Estratégia — Football Studio")
col1, col2 = st.columns([1,2])

with col1:
    st.subheader("Inserir Resultado")
    c1, c2, c3 = st.columns(3)
    if c1.button(f"{EMOJI['V']} Vermelho (V)"):
        add_result('V')
    if c2.button(f"{EMOJI['A']} Azul (A)"):
        add_result('A')
    if c3.button(f"{EMOJI['E']} Empate (E)"):
        add_result('E')

    st.write("")

    if st.button("Desfazer último"):
        undo()
    if st.button("Resetar histórico"):
        reset_history()

    st.markdown("---")

    st.subheader("Importar / Exportar")
    hist_json = json.dumps(st.session_state.state['history'])
    st.download_button("Exportar histórico (JSON)", hist_json, file_name="history_football_studio.json")

    uploaded = st.file_uploader("Importar histórico (JSON)", type=['json'])
    if uploaded is not None:
        try:
            data = json.load(uploaded)
            if isinstance(data, list):
                st.session_state.state['history'] = data[:MAX_HISTORY]
                st.success("Histórico importado com sucesso")
            else:
                st.error("Formato inválido — precisa ser lista JSON")
        except Exception as e:
            st.error(f"Erro ao importar: {e}")

with col2:
    st.subheader("Histórico (mais recente à esquerda)")
    history = st.session_state.state['history']

    # show up to 9 results per row, up to 10 rows
    per_row = 9
    rows = []
    for i in range(0, min(len(history), per_row*10), per_row):
        rows.append(history[i:i+per_row])

    for row in rows:
        cols = st.columns(len(row))
        for c, val in zip(cols, row):
            c.markdown(f"### {EMOJI[val]}\n`{val}`")

    st.markdown("---")
    st.subheader("Análise & Diagnóstico")

    window = st.slider("Janela de análise (rodadas mais recentes)", min_value=MIN_WINDOW, max_value=DEFAULT_WINDOW, value=DEFAULT_WINDOW)

    if not history:
        st.info("Nenhum resultado ainda. Insira resultados para começar a análise.")
    else:
        w = windowed_list(history, window)
        baralho, bar_conf = classify_baralho(history, window)
        strat, strat_conf = detect_strategy(history, window)
        preds = predict_next(history, window)
        suggestion, preds, conf = suggest_action(history, window)

        st.metric("Tipo de Baralho", baralho, delta=f"Confiança: {int(bar_conf*100)}%")
        st.metric("Estratégia detectada", strat, delta=f"Confiança: {int(strat_conf*100)}%")

        st.markdown("**Probabilidade prevista (próxima rodada)**")
        cols = st.columns(3)
        cols[0].progress(int(preds['V']*100))
        cols[0].write(f"{EMOJI['V']} Vermelho — {preds['V']*100:.1f}%")
        cols[1].progress(int(preds['A']*100))
        cols[1].write(f"{EMOJI['A']} Azul — {preds['A']*100:.1f}%")
        cols[2].progress(int(preds['E']*100))
        cols[2].write(f"{EMOJI['E']} Empate — {preds['E']*100:.1f}%")

        st.markdown("**Sugestão**")
        st.info(suggestion)
        st.markdown(f"**Confiança global da leitura:** {int(conf*100)}%")

        st.markdown("---")
        st.write("**Métricas técnicas**")
        st.write({
            'Janela': window,
            'Tamanho histórico': len(history),
            'Frequência': frequency_counts(w),
            'Alternância': round(alternation_score(w),3),
            'Média de runs (sem empates)': round(avg_run_length(w),3),
            'Posições de empate (0=mais recente)': tie_positions(w, window)
        })

st.sidebar.title("Sobre")
st.sidebar.markdown(
    "Detector simples que classifica heurísticamente tipos de baralho e estratégias a partir do histórico.\n\n"
    "É uma base para você ir afinando os pesos, as regras e integrar modelos ML/IA mais avançados.\n\n"
    "Use a opção de exportar/importar para persistir histórico localmente."
)

st.sidebar.markdown("---")
st.sidebar.markdown("Feito para estudo — Ajuste heurísticas conforme necessário.")

# -----------------------------

# Fim do app

# -----------------------------
