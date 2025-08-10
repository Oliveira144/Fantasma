import streamlit as st
from typing import List, Dict, Tuple

EMOJI = {'V': '🔴', 'A': '🔵', 'E': '🟡'}
MAX_HISTORY = 200
DEFAULT_WINDOW = 50

class ManipulationDetector:
    def __init__(self, history: List[str]):
        self.history = history

    def _compute_runs(self) -> List[int]:
        runs = []
        if not self.history:
            return runs
        cur = None
        count = 0
        for r in self.history:
            if r == 'E':  # Ignorar empates nos runs
                continue
            if r == cur:
                count += 1
            else:
                if count > 0:
                    runs.append(count)
                cur = r
                count = 1
        if count > 0:
            runs.append(count)
        return runs

    def _frequency(self) -> Dict[str,int]:
        return {k: self.history.count(k) for k in ['V','A','E']}

    def _alternation_score(self) -> float:
        pairs = 0
        alt = 0
        prev = None
        for r in self.history:
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

    def _analyze_level_1(self) -> Dict:
        runs = self._compute_runs()
        avg_run = sum(runs)/len(runs) if runs else 0
        repetitive = avg_run > 3
        confidence = min(1.0, avg_run/10)
        return {"avg_run": avg_run, "repetitive_pattern": repetitive, "confidence": confidence}

    def _analyze_level_2(self) -> Dict:
        alt_score = self._alternation_score()
        strong_alt = alt_score > 0.7
        return {"alternation_score": alt_score, "strong_alternation": strong_alt, "confidence": alt_score}

    def _analyze_level_3(self) -> Dict:
        freq = self._frequency()
        e_ratio = freq['E'] / len(self.history) if self.history else 0
        anchored = e_ratio > 0.1
        return {"empate_ratio": e_ratio, "anchored_by_ties": anchored, "confidence": min(1.0, e_ratio*5)}

    def _analyze_level_4(self) -> Dict:
        runs = self._compute_runs()
        alt_score = self._alternation_score()
        cyclical = (len(runs) >= 4 and alt_score > 0.4 and max(runs) < 5)
        confidence = 0.6 if cyclical else 0.2
        return {"cyclical_pattern": cyclical, "confidence": confidence}

    def _analyze_level_5(self) -> Dict:
        runs = self._compute_runs()
        avg_run = sum(runs)/len(runs) if runs else 0
        alt_score = self._alternation_score()
        inverted = avg_run > 2.5 and alt_score < 0.4
        confidence = 0.7 if inverted else 0.3
        return {"inversion_detected": inverted, "confidence": confidence}

    def _analyze_level_6(self) -> Dict:
        freq = self._frequency()
        e_ratio = freq['E'] / len(self.history) if self.history else 0
        alt_score = self._alternation_score()
        noise = alt_score > 0.5 and e_ratio > 0.03
        confidence = 0.6 if noise else 0.2
        return {"noise_detected": noise, "confidence": confidence}

    def _analyze_level_7(self) -> Dict:
        freq = self._frequency()
        alt_score = self._alternation_score()
        v_a_diff = abs(freq['V'] - freq['A'])
        ghost = v_a_diff <= 3 and alt_score > 0.35
        confidence = 0.5 if ghost else 0.1
        return {"ghost_pattern": ghost, "confidence": confidence}

    def _analyze_level_8(self) -> Dict:
        runs = self._compute_runs()
        alt_score = self._alternation_score()
        freq = self._frequency()
        e_ratio = freq['E'] / len(self.history) if self.history else 0
        quantum = alt_score > 0.45 and 1 <= max(runs, default=0) <= 3 and e_ratio > 0.05
        confidence = 0.7 if quantum else 0.2
        return {"quantum_pattern": quantum, "confidence": confidence}

    def _analyze_level_9(self) -> Dict:
        runs = self._compute_runs()
        alt_score = self._alternation_score()
        reversed_cycle = (len(runs) > 3 and runs[0] >= 3 and alt_score < 0.5)
        confidence = 0.6 if reversed_cycle else 0.1
        return {"reversed_cycle": reversed_cycle, "confidence": confidence}

    def _analyze_level_10(self) -> Dict:
        freq = self._frequency()
        e_ratio = freq['E'] / len(self.history) if self.history else 0
        runs = self._compute_runs()
        avg_run = sum(runs)/len(runs) if runs else 0
        collapse = avg_run > 5 and e_ratio < 0.03
        confidence = 0.8 if collapse else 0.1
        return {"max_manipulation": collapse, "confidence": confidence}

    def analyze_levels(self) -> Dict[int, Dict]:
        results = {}
        for lvl in range(1, 11):
            func = getattr(self, f"_analyze_level_{lvl}", None)
            if func:
                results[lvl] = func()
            else:
                results[lvl] = {"status": "Nível não implementado"}
        return results

    def predict_next(self) -> Dict[str,float]:
        levels = self.analyze_levels()
        base_probs = {"V": 0.48, "A": 0.48, "E": 0.04}

        for lvl, res in levels.items():
            conf = res.get("confidence", 0)
            if lvl == 1 and res.get("repetitive_pattern", False):
                base_probs["E"] += 0.1 * conf
                base_probs["V"] -= 0.05 * conf
                base_probs["A"] -= 0.05 * conf
            if lvl == 2 and res.get("strong_alternation", False):
                base_probs["V"] += 0.05 * conf
                base_probs["A"] += 0.05 * conf
                base_probs["E"] -= 0.05 * conf

        total = sum(base_probs.values())
        for k in base_probs:
            base_probs[k] = max(0, base_probs[k]/total)

        return base_probs

    def suggest_bet(self) -> Tuple[str, float]:
        preds = self.predict_next()
        best = max(preds, key=preds.get)
        conf = preds[best]
        return best, conf

def main():
    st.set_page_config(page_title="Detector de Manipulação Football Studio", page_icon="🎯", layout="wide")

    if 'history' not in st.session_state:
        st.session_state.history = []

    st.title("Detector de Manipulação Football Studio")

    col1, col2, col3 = st.columns(3)
    if col1.button(f"{EMOJI['V']} Vermelho (V)"):
        st.session_state.history.insert(0, 'V')
    if col2.button(f"{EMOJI['A']} Azul (A)"):
        st.session_state.history.insert(0, 'A')
    if col3.button(f"{EMOJI['E']} Empate (E)"):
        st.session_state.history.insert(0, 'E')

    if st.button("Desfazer último"):
        if st.session_state.history:
            st.session_state.history.pop(0)

    if st.button("Resetar histórico"):
        st.session_state.history = []

    st.markdown("---")

    st.subheader("Histórico (mais recente à esquerda)")

    history = st.session_state.history[:MAX_HISTORY]

    if history:
        # Mostrar do mais recente (esquerda) para o mais antigo (direita)
        st.markdown(" ".join(EMOJI[val] for val in history))
    else:
        st.write("Nenhum resultado registrado.")

    st.markdown("---")

    if not history:
        st.info("Insira resultados para começar a análise.")
        return

    window = st.slider("Janela de análise (mais recentes resultados)", min_value=12, max_value=DEFAULT_WINDOW, value=min(DEFAULT_WINDOW, len(history)))
    history_window = history[:window]

    detector = ManipulationDetector(history_window)
    levels = detector.analyze_levels()
    prediction = detector.predict_next()
    suggested_bet, conf = detector.suggest_bet()

    st.subheader("Análise dos 10 níveis de manipulação")
    for lvl in range(1, 11):
        res = levels.get(lvl, {})
        conf_level = res.get("confidence", 0)
        st.markdown(f"**Nível {lvl}:** Confiança {conf_level*100:.1f}%")

    st.markdown("---")

    st.subheader("Previsão para próximo resultado")
    cols = st.columns(3)
    cols[0].progress(int(prediction['V']*100))
    cols[0].write(f"{EMOJI['V']} Vermelho — {prediction['V']*100:.1f}%")
    cols[1].progress(int(prediction['A']*100))
    cols[1].write(f"{EMOJI['A']} Azul — {prediction['A']*100:.1f}%")
    cols[2].progress(int(prediction['E']*100))
    cols[2].write(f"{EMOJI['E']} Empate — {prediction['E']*100:.1f}%")

    st.subheader("Sugestão de aposta")
    st.info(f"Apostar em {EMOJI[suggested_bet]} (confiança: {conf*100:.1f}%)")

if __name__ == "__main__":
    main()
