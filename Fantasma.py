import streamlit as st
import json
import statistics
from typing import List, Tuple, Dict, Any

# --- Configurações e Estado Inicial ---

EMOJI = {'V': '🔴', 'A': '🔵', 'E': '🟡'}
MAX_HISTORY = 200
DEFAULT_WINDOW = 50

st.set_page_config(page_title="Detector de Padrões & Estratégia - Football Studio", layout="wide", page_icon="🎯")

@st.cache_data
def empty_state() -> Dict[str, List[str]]:
    """Inicializa um estado de sessão vazio."""
    return {'history': []}

if 'state' not in st.session_state:
    st.session_state.state = empty_state()

# --- Funções de Manipulação do Histórico ---

def add_result(code: str):
    """Adiciona um resultado ao histórico."""
    hist = st.session_state.state['history']
    hist.insert(0, code)
    if len(hist) > MAX_HISTORY:
        hist.pop()
    st.session_state.state['history'] = hist

def undo():
    """Desfaz o último resultado adicionado."""
    hist = st.session_state.state['history']
    if hist:
        hist.pop(0)
    st.session_state.state['history'] = hist

def reset_history():
    """Limpa todo o histórico."""
    st.session_state.state['history'] = []

def windowed_list(history: List[str], window: int) -> List[str]:
    """Retorna uma sublista do histórico, limitada pela janela."""
    return history[:window]

# --- Métricas Técnicas (Aprimoradas) ---

def compute_runs(history: List[str]) -> List[int]:
    """
    Calcula o tamanho de sequências de resultados consecutivos.
    Ignora empates para runs de V e A.
    """
    runs = []
    if not history:
        return runs
    
    clean_history = [x for x in history if x != 'E']
    if not clean_history:
        return []
    
    cur = clean_history[0]
    count = 1
    for r in clean_history[1:]:
        if r == cur:
            count += 1
        else:
            runs.append(count)
            cur = r
            count = 1
    runs.append(count)
    return runs

def frequency_counts(history: List[str]) -> Dict[str, float]:
    """Calcula a frequência percentual de cada resultado."""
    total = len(history)
    if total == 0:
        return {'V': 0.0, 'A': 0.0, 'E': 0.0}
    return {k: history.count(k) / total for k in ['V', 'A', 'E']}

def alternation_score(history: List[str]) -> float:
    """Calcula a pontuação de alternância entre V e A."""
    pairs = 0
    alt = 0
    prev = None
    for r in history:
        if r == 'E':
            continue
        if prev is not None and prev != 'E':
            pairs += 1
            if r != prev:
                alt += 1
        prev = r
    return (alt / pairs) if pairs > 0 else 0.0

def avg_run_length(history: List[str]) -> float:
    """Calcula o tamanho médio de uma sequência (run)."""
    runs = compute_runs([x for x in history if x != 'E'])
    return statistics.mean(runs) if runs else 0.0

def tie_positions(history: List[str], window: int) -> List[int]:
    """Retorna as posições dos empates na janela."""
    return [i for i, r in enumerate(windowed_list(history, window)) if r == 'E']

# --- Lógica de Análise (Aprimorada) ---

def classify_baralho(history: List[str], window: int) -> Dict[str, Any]:
    """Classifica o tipo de baralho e a confiança da detecção."""
    w = windowed_list(history, window)
    if len(w) < 10:
        return {"name": "Indefinido", "confidence": 0.0, "details": {}}
    
    freq = frequency_counts(w)
    alt_score = alternation_score(w)
    avg_run = avg_run_length(w)
    
    # Dicionário para armazenar a confiança de cada padrão
    patterns = {
        "Repetição Forçada": 0.0,
        "Alternância Equilibrada": 0.0,
        "Ancoragem por Empate": 0.0,
        "Inversão Psicológica": 0.0,
        "Balanceado": 0.0
    }
    
    # 1. Repetição Forçada
    if avg_run > 2.0 and freq['E'] < 0.05:
        # A confiança aumenta com runs mais longas
        confidence = min(1.0, (avg_run - 2.0) / 3.0)
        # Se a diferença entre V e A for grande, reforça a repetição
        confidence += max(0, abs(freq['V'] - freq['A']) - 0.2)
        patterns["Repetição Forçada"] = confidence

    # 2. Alternância Equilibrada
    if alt_score > 0.5 and avg_run < 2.0 and freq['E'] < 0.1:
        # Confiança baseada diretamente na pontuação de alternância
        patterns["Alternância Equilibrada"] = alt_score

    # 3. Ancoragem por Empate
    if freq['E'] > 0.06 and any(i < 12 for i in tie_positions(w, window)):
        # Confiança aumenta com a frequência de empates e a falta de alternância
        confidence = min(1.0, freq['E'] * 5 + (1 - alt_score) * 0.3)
        patterns["Ancoragem por Empate"] = confidence

    # 4. Inversão Psicológica (run longa + empates)
    if avg_run > 2.5 and freq['E'] > 0.05 and alt_score < 0.4:
        confidence = 0.4 + (avg_run - 2.5) * 0.1
        patterns["Inversão Psicológica"] = confidence

    # 5. Balanceado (padrão neutro)
    balance_conf = 1 - abs(freq['V'] - freq['A'])
    patterns["Balanceado"] = balance_conf * 0.8
    
    # Seleciona o padrão com a maior confiança
    max_pattern = max(patterns, key=patterns.get)
    max_conf = patterns[max_pattern]
    
    return {
        "name": max_pattern,
        "confidence": max_conf,
        "details": patterns
    }

def detect_strategy(history: List[str], window: int) -> Dict[str, Any]:
    """Detecta estratégias e a confiança da detecção."""
    w = windowed_list(history, window)
    if len(w) < 10:
        return {"name": "Indefinida", "confidence": 0.0}
    
    avg_run = avg_run_length(w)
    alt = alternation_score(w)
    freq = frequency_counts(w)
    last6 = w[:6]
    
    strategies = {
        "Isco-Reversão": 0.0,
        "Ruído Controlado": 0.0,
        "Ciclo Escalonado": 0.0,
        "Padrão Fantasma": 0.0
    }
    
    # 1. Isco-Reversão
    if len(last6) >= 4 and compute_runs(last6) and compute_runs(last6)[0] >= 3:
        strategies["Isco-Reversão"] = 0.7

    # 2. Ruído Controlado
    if alt > 0.55 and freq['E'] > 0.03:
        strategies["Ruído Controlado"] = 0.4 + alt * 0.5

    # 3. Ciclo Escalonado
    if avg_run > 1.8 and alt > 0.3:
        strategies["Ciclo Escalonado"] = 0.5
    
    # 4. Padrão Fantasma
    if abs(freq['V'] - freq['A']) <= 0.1 and alt > 0.35:
        strategies["Padrão Fantasma"] = 0.45
        
    # Seleciona a estratégia com maior confiança
    max_strat = max(strategies, key=strategies.get)
    max_conf = strategies[max_strat]
    
    if max_conf > 0.0:
        return {"name": max_strat, "confidence": max_conf}
    
    return {"name": "Estratégia Indefinida", "confidence": 0.2}

def predict_next(history: List[str], window: int) -> Dict[str, float]:
    """
    Prediz a probabilidade do próximo resultado com base em padrões recentes.
    Lógica aprimorada com ponderações mais dinâmicas.
    """
    w = windowed_list(history, window)
    if len(w) < 5:
        return {'V': 0.48, 'A': 0.48, 'E': 0.04}
    
    counts = frequency_counts(w)
    base_probs = counts.copy()
    
    avg_run = avg_run_length(w)
    alt = alternation_score(w)
    last = w[0] if w else None
    
    # Ajustes baseados em padrões
    
    # Tendência de Repetição: se a sequência atual é longa, aumenta a chance de reversão
    if last in ('V', 'A') and avg_run >= 3.0:
        opp = 'A' if last == 'V' else 'V'
        factor = min(1.0, (avg_run - 2) / 4)
        base_probs[opp] += 0.25 * factor  # Aumenta a chance do oposto
        base_probs[last] -= 0.15 * factor # Diminui a chance de continuação
        base_probs['E'] += 0.05 * factor # Aumenta a chance de empate
    
    # Tendência de Alternância: aumenta a chance da cor oposta
    if last in ('V', 'A') and alt >= 0.6:
        opp = 'A' if last == 'V' else 'V'
        base_probs[opp] += 0.1
        base_probs[last] -= 0.1

    # Tendência de Empate: se o último empate foi há muito tempo, aumenta a chance
    tie_pos = tie_positions(w, window)
    if tie_pos and tie_pos[0] > 5:
        base_probs['E'] += 0.05
    elif not tie_pos:
        base_probs['E'] += 0.1
    elif tie_pos and tie_pos[0] < 3: # Empate recente, reduz a chance de outro
        base_probs['E'] = max(0.02, base_probs['E'] - 0.03)

    # Normalização
    for k in base_probs:
        base_probs[k] = max(0.0, base_probs[k])
    
    s = sum(base_probs.values())
    if s == 0:
        return {'V': 0.48, 'A': 0.48, 'E': 0.04}
    
    normalized_probs = {k: round(v / s, 3) for k, v in base_probs.items()}
    return normalized_probs

def compute_confidence(baralho_info: Dict[str, Any], strat_info: Dict[str, Any], history_len: int) -> float:
    """
    Calcula a confiança global com base na força de detecção do baralho
    e da estratégia, e penaliza por histórico curto.
    """
    bar_conf = baralho_info.get("confidence", 0)
    strat_conf = strat_info.get("confidence", 0)
    
    # Se a confiança do baralho for alta, dá mais peso a ela
    weight_baralho = 0.7 if bar_conf > 0.6 else 0.5
    weight_strat = 1 - weight_baralho
    
    base = weight_baralho * bar_conf + weight_strat * strat_conf
    
    # Penalidade por histórico curto
    penalty = 0.0
    if history_len < 15:
        penalty = (15 - history_len) / 25
    
    conf = max(0.0, min(1.0, base - penalty))
    return round(conf, 3)

def suggest_action(history: List[str], window: int) -> Tuple[str, Dict[str, float], float]:
    """Gera uma sugestão de aposta com base nos padrões e na confiança."""
    baralho_info = classify_baralho(history, window)
    strat_info = detect_strategy(history, window)
    preds = predict_next(history, window)
    conf = compute_confidence(baralho_info, strat_info, len(history))
    
    baralho = baralho_info["name"]
    last = history[0] if history else None
    
    # Se a confiança é muito baixa, a melhor sugestão é observar
    if conf < 0.3:
        return ("Observar — a confiança da leitura é muito baixa", preds, conf)

    # Lógica de sugestão aprimorada e mais priorizada
    
    # 1. Repetição Forçada (Alta confiança)
    if baralho == "Repetição Forçada" and baralho_info["confidence"] > 0.6 and last in ('V', 'A'):
        opp = 'A' if last == 'V' else 'V'
        return (f"Sugerir apostar em {EMOJI[opp]} (quebra da sequência)", preds, conf)

    # 2. Alternância Equilibrada (Alta confiança)
    if baralho == "Alternância Equilibrada" and baralho_info["confidence"] > 0.6 and last in ('V', 'A'):
        opp = 'A' if last == 'V' else 'V'
        return (f"Sugerir apostar em {EMOJI[opp]} (espera alternância)", preds, conf)
        
    # 3. Ancoragem por Empate (Se o empate é muito provável)
    if baralho == "Ancoragem por Empate" and preds['E'] > 0.12 and conf > 0.5:
        return ("Sugerir apostar no Empate 🟡 — alta probabilidade de interrupção", preds, conf)
    
    # 4. Padrão Fantasma (Aposta na maior probabilidade, confiando nas previsões)
    if strat_info["name"] == "Padrão Fantasma" and conf > 0.5:
        maior_chance = max(preds, key=preds.get)
        if maior_chance != 'E':
             return (f"Sugerir apostar em {EMOJI[maior_chance]} (padrão fantasma)", preds, conf)
             
    # Sugestão padrão: aposta na maior probabilidade se a confiança for razoável
    maior_chance = max(preds, key=preds.get)
    if maior_chance != 'E' and conf >= 0.4:
        return (f"Sugerir apostar em {EMOJI[maior_chance]} (maior probabilidade geral)", preds, conf)
        
    # Caso contrário, observar
    return ("Observar — sem sugestão forte ou confiável", preds, conf)

# --- UI (interface) ---

st.title("Detector de Padrões & Estratégia — Football Studio")

col1, col2 = st.columns([1, 2])

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
    st.button("Desfazer último", on_click=undo)
    st.button("Resetar histórico", on_click=reset_history)

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
                st.success("Histórico importado com sucesso!")
                st.experimental_rerun()  # Recarrega a página para atualizar o histórico
            else:
                st.error("Formato inválido — precisa ser uma lista JSON de strings.")
        except Exception as e:
            st.error(f"Erro ao importar: {e}")

with col2:
    st.subheader("Histórico (mais recente à esquerda)")
    history = st.session_state.state['history']
    if history:
        display_history = [EMOJI.get(r, '?') for r in history[:50]]
        st.markdown(' '.join(display_history))
    else:
        st.info("Nenhum resultado ainda. Insira resultados para começar.")
        
    st.markdown("---")

    st.subheader("Análise & Diagnóstico")

    window = st.slider("Janela de análise (rodadas mais recentes)", min_value=12, max_value=MAX_HISTORY, value=DEFAULT_WINDOW)

    if len(history) < 5:
        st.info("Insira pelo menos 5 resultados para iniciar a análise.")
    else:
        baralho_info = classify_baralho(history, window)
        strat_info = detect_strategy(history, window)
        suggestion, preds, conf = suggest_action(history, window)

        st.metric("Tipo de Padrão", baralho_info["name"], delta=f"Confiança: {int(baralho_info['confidence']*100)}%")
        st.metric("Estratégia detectada", strat_info["name"], delta=f"Confiança: {int(strat_info['confidence']*100)}%")

        st.markdown("**Probabilidade prevista (próxima rodada)**")
        cols = st.columns(3)
        cols[0].progress(int(preds['V'] * 100))
        cols[0].write(f"{EMOJI['V']} Vermelho — {preds['V']*100:.1f}%")
        cols[1].progress(int(preds['A'] * 100))
        cols[1].write(f"{EMOJI['A']} Azul — {preds['A']*100:.1f}%")
        cols[2].progress(int(preds['E'] * 100))
        cols[2].write(f"{EMOJI['E']} Empate — {preds['E']*100:.1f}%")

        st.markdown("**Sugestão**")
        st.info(suggestion)
        st.markdown(f"**Confiança global da leitura:** {int(conf*100)}%")

        st.markdown("---")
        st.write("**Métricas técnicas**")
        st.json({
            'Janela': window,
            'Tamanho histórico': len(history),
            'Frequência': frequency_counts(windowed_list(history, window)),
            'Alternância': round(alternation_score(windowed_list(history, window)), 3),
            'Média de runs (sem empates)': round(avg_run_length(windowed_list(history, window)), 3),
            'Posições de empate (0=mais recente)': tie_positions(history, window)
        })

st.sidebar.title("Sobre")
st.sidebar.markdown(
    "Este é um detector aprimorado que usa heurísticas e análises de padrões para sugerir ações no jogo Football Studio.\n\n"
    "As lógicas foram revisadas para oferecer sugestões mais confiáveis e um cálculo de confiança mais robusto.\n\n"
    "**Importante:** Use isso como uma ferramenta de apoio. Nenhuma estratégia garante vitória."
)
st.sidebar.markdown("---")
st.sidebar.markdown("Código aprimorado para estudo e melhoria contínua.")
