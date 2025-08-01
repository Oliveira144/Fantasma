import streamlit as st
import numpy as np
from collections import deque, Counter

class BacBoPredictor:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.game_history = []
        self.point_history = []
        self.streaks = {'Player': 0, 'Banker': 0, 'Tie': 0}
        self.win_stats = {'Player': 0, 'Banker': 0, 'Tie': 0}
    
    def add_result(self, result: str, points: int):
        result = result.upper()
        self.game_history.append(result)
        self.point_history.append(points)
        self.win_stats[result] += 1
        self._update_streaks(result)
    
    def _update_streaks(self, result):
        for key in self.streaks:
            self.streaks[key] = self.streaks[key] + 1 if key == result else 0

    def analyze(self):
        return {
            'current_streak': self._get_current_streak(),
            'hot_zones': self._get_hot_zones(),
            'tie_risk': self._check_tie_risk(),
            'swing': self._calculate_swing()
        }
    
    def _get_current_streak(self):
        return max(self.streaks.values())
    
    def _get_hot_zones(self):
        if len(self.point_history) < 5: return []
        recent = self.point_history[-10:] if len(self.point_history) >= 10 else self.point_history
        freq = Counter(recent)
        return [k for k, v in freq.items() if v >= max(freq.values())*0.7]
    
    def _check_tie_risk(self):
        if len(self.point_history) < 3: return False
        return 8 <= np.mean(self.point_history[-3:]) <= 9
    
    def _calculate_swing(self):
        if len(self.point_history) < 2: return 0
        return abs(self.point_history[-1] - self.point_history[-2])

# Configuração do App
st.set_page_config(layout="wide", page_title="Bac Bo PRO", page_icon="🎲")

# CSS Customizado
st.markdown("""
<style>
/* Botões Principais */
.big-btn {
    height: 100px !important;
    font-size: 24px !important;
    margin: 5px 0 !important;
    border-radius: 10px !important;
    transition: all 0.2s !important;
}
.big-btn:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.player-btn { background-color: #3b82f6 !important; }
.banker-btn { background-color: #ef4444 !important; }
.tie-btn { background-color: #a855f7 !important; }

/* Histórico Visual */
.history-container {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin: 15px 0;
}
.history-item {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 16px;
    position: relative;
}
.point-label {
    font-size: 10px;
    margin-top: 2px;
}
</style>
""", unsafe_allow_html=True)

# Inicialização
if 'predictor' not in st.session_state:
    st.session_state.predictor = BacBoPredictor()

# --- Layout Principal ---
st.title("🎲 BAC BO PREDICTOR PRO")

# Seção de Registro Rápido
st.header("Registrar Resultado")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔵 PLAYER", key="player", help="Registrar vitória do Player",
                use_container_width=True, type="primary", className="big-btn player-btn"):
        pts = np.random.randint(3, 13)
        st.session_state.predictor.add_result("Player", pts)
        st.rerun()

with col2:
    if st.button("🔴 BANKER", key="banker", help="Registrar vitória do Banker",
                use_container_width=True, type="primary", className="big-btn banker-btn"):
        pts = np.random.randint(3, 13)
        st.session_state.predictor.add_result("Banker", pts)
        st.rerun()

with col3:
    if st.button("🟣 TIE", key="tie", help="Registrar empate",
                use_container_width=True, type="primary", className="big-btn tie-btn"):
        pts = np.random.randint(3, 13)
        st.session_state.predictor.add_result("Tie", pts)
        st.rerun()

# Seção de Análise
if st.session_state.predictor.game_history:
    analysis = st.session_state.predictor.analyze()
    
    # Layout em Colunas
    col_anal, col_hist = st.columns([3, 2])
    
    with col_anal:
        st.header("📊 Análise em Tempo Real")
        
        # Alertas
        current_streak = analysis['current_streak']
        if current_streak >= 3:
            st.warning(f"🚨 Sequência detectada: {current_streak} jogos iguais")
        
        # Hot Zones
        if analysis['hot_zones']:
            st.subheader("Zonas Quentes")
            cols = st.columns(len(analysis['hot_zones']))
            for i, zone in enumerate(analysis['hot_zones']):
                cols[i].metric(label=f"{zone} pontos", value="")
        
        # Gráfico
        st.line_chart({
            'Pontos': st.session_state.predictor.point_history[-20:]
        })
        
        # Alerta de Tie
        if analysis['tie_risk']:
            st.markdown("""
            <div style="
                background: #e6f3ff;
                border-left: 4px solid #0066cc;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            ">
                <b>⚠️ Alerta de Tie Possível</b>
                <p>Média recente: {:.1f} pontos</p>
            </div>
            """.format(np.mean(st.session_state.predictor.point_history[-3:])),
            unsafe_allow_html=True)
    
    with col_hist:
        st.header("📜 Histórico e Estatísticas")
        
        # Histórico Visual
        st.subheader("Últimos Resultados")
        history_html = "<div class='history-container'>"
        for res, pts in zip(st.session_state.predictor.game_history[-8:], 
                          st.session_state.predictor.point_history[-8:]):
            color = "#3b82f6" if res == "PLAYER" else "#ef4444" if res == "BANKER" else "#a855f7"
            history_html += f"""
            <div class="history-item" style="background-color: {color}">
                {pts}
                <div class="point-label">{res[0]}</div>
            </div>
            """
        history_html += "</div>"
        st.markdown(history_html, unsafe_allow_html=True)
        
        # Estatísticas
        st.subheader("Performance")
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Total Jogos", len(st.session_state.predictor.game_history))
            st.metric("Maior Sequência", analysis['current_streak'])
        with col_stat2:
            st.metric("Player Wins", st.session_state.predictor.win_stats['PLAYER'])
            st.metric("Banker Wins", st.session_state.predictor.win_stats['BANKER'])

else:
    st.info("Use os botões acima para registrar os primeiros resultados")

# Botão de Reset
if st.button("🔄 Reiniciar Sistema", type="secondary"):
    st.session_state.predictor.reset()
    st.rerun()

# Rodapé
st.markdown("---")
st.caption("Bac Bo Predictor PRO v3.0 | Análise em tempo real")
