import streamlit as st
import random
import numpy as np
from collections import Counter, deque

class BacBoPredictor:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.game_history = []
        self.point_history = []
        self.streaks = {'Player': 0, 'Banker': 0, 'Tie': 0}
        self.win_percentages = {'Player': 0, 'Banker': 0, 'Tie': 0}
        self.patterns = deque(maxlen=100)
        self.hot_numbers = []
        self.trends = {'Player': 0, 'Banker': 0, 'Tie': 0}
        
    def add_result(self, result: str, points: int):
        result = result.capitalize()
        if result not in ['Player', 'Banker', 'Tie']:
            return False
            
        self.game_history.append(result)
        self.point_history.append(points)
        self._update_streaks(result)
        self._update_win_percentages()
        self._update_patterns()
        self._update_hot_numbers()
        self._update_trends()
        return True
    
    def _update_streaks(self, result):
        for outcome in self.streaks:
            self.streaks[outcome] = self.streaks[outcome] + 1 if outcome == result else 0
    
    def _update_win_percentages(self):
        total = len(self.game_history)
        if total == 0:
            return
            
        for outcome in ['Player', 'Banker', 'Tie']:
            count = sum(1 for r in self.game_history if r == outcome)
            self.win_percentages[outcome] = round(count / total * 100, 1)
    
    def _update_patterns(self):
        if len(self.game_history) >= 5:
            sequence = tuple(self.game_history[-5:])
            self.patterns.append(sequence)
    
    def _update_hot_numbers(self):
        if len(self.point_history) < 10:
            return
            
        recent_points = self.point_history[-20:]
        counts = Counter(recent_points)
        
        if not counts:
            return
            
        avg_frequency = sum(counts.values()) / len(counts)
        threshold = avg_frequency * 1.5
        
        self.hot_numbers = [n for n, count in counts.items() if count >= threshold]
    
    def _update_trends(self):
        if len(self.game_history) < 10:
            return
            
        recent = self.game_history[-10:]
        self.trends = {
            'Player': round(recent.count('Player') / 10 * 100, 1),
            'Banker': round(recent.count('Banker') / 10 * 100, 1),
            'Tie': round(recent.count('Tie') / 10 * 100, 1)
        }
    
    def predict_next(self):
        if len(self.game_history) < 15:
            return None, 0
        
        # Fator 1: Sequências atuais
        if self.streaks['Player'] >= 3:
            return 'Banker', 75
        elif self.streaks['Banker'] >= 3:
            return 'Player', 80
        
        # Fator 2: Tendência recente
        if self.trends['Tie'] < 5 and random.random() < 0.3:
            return 'Tie', 65
        
        # Fator 3: Padrões históricos
        last_3 = tuple(self.game_history[-3:])
        pattern_matches = []
        
        for pattern in self.patterns:
            if pattern[:3] == last_3:
                pattern_matches.append(pattern[3])
        
        if pattern_matches:
            most_common = Counter(pattern_matches).most_common(1)
            if most_common:
                outcome = most_common[0][0]
                confidence = min(80, most_common[0][1] * 15)
                return outcome, confidence
        
        # Fator 4: Porcentagem geral
        if self.win_percentages['Player'] < 40:
            return 'Player', 60
        elif self.win_percentages['Banker'] < 40:
            return 'Banker', 65
        
        # Fallback: Aleatório com base nas tendências
        outcomes = ['Player', 'Banker', 'Tie']
        weights = [
            self.win_percentages['Player'],
            self.win_percentages['Banker'],
            max(5, self.win_percentages['Tie'])
        ]
        choice = random.choices(outcomes, weights=weights, k=1)[0]
        confidence = weights[outcomes.index(choice)] * 0.8
        return choice, confidence
    
    def get_tie_probability(self):
        if len(self.point_history) < 3:
            return 0
            
        avg = np.mean(self.point_history[-3:])
        
        if 7.5 <= avg <= 9.0:
            return min(90, 50 + (abs(8.25 - avg) * 20))
        
        return max(10, 40 - abs(8.25 - avg) * 10)

# Configuração do Streamlit
st.set_page_config(layout="wide", page_title="Bac Bo PRO Predictor", page_icon="🎲")

# CSS Customizado
st.markdown("""
<style>
:root {
    --player-color: #3b82f6;
    --banker-color: #ef4444;
    --tie-color: #a855f7;
}

.header {
    background: linear-gradient(135deg, #1a2a4a, #0d1b2f);
    color: white;
    padding: 15px 25px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.control-btn {
    height: 80px;
    font-size: 20px;
    font-weight: bold;
    border: none;
    border-radius: 10px;
    transition: all 0.3s;
    margin-bottom: 10px;
    width: 100%;
}

.control-btn:hover {
    transform: scale(1.03);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.player-btn {
    background: var(--player-color);
    color: white;
}

.banker-btn {
    background: var(--banker-color);
    color: white;
}

.tie-btn {
    background: var(--tie-color);
    color: white;
}

.reset-btn {
    background: #6c757d;
    color: white;
}

.history-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
    gap: 15px;
    margin: 20px 0;
}

.history-card {
    border-radius: 12px;
    height: 80px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    color: white;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}

.points-display {
    font-size: 28px;
    margin-bottom: 5px;
}

.result-display {
    font-size: 16px;
    letter-spacing: 1px;
}

.player-card {
    background: var(--player-color);
}

.banker-card {
    background: var(--banker-color);
}

.tie-card {
    background: var(--tie-color);
}

.stats-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin: 25px 0;
}

.stat-card {
    border-radius: 12px;
    padding: 20px;
    background: #f8f9fa;
    text-align: center;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.prediction-card {
    background: linear-gradient(135deg, #2b313e, #1e2533);
    border-radius: 15px;
    padding: 20px;
    margin: 20px 0;
    color: white;
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
}

.chart-container {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin: 25px 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

# Inicialização do sistema
if 'predictor' not in st.session_state:
    st.session_state.predictor = BacBoPredictor()

# Layout Principal
st.markdown('<div class="header"><h1>🎲 Bac Bo PRO Predictor</h1></div>', unsafe_allow_html=True)

# Seção de Controle
st.header("🎮 Controle do Jogo")
col1, col2, col3, col4 = st.columns([1, 1, 1, 1.2])

# Botões de controle
with col1:
    if st.button("🔵 PLAYER", key="player", use_container_width=True):
        st.session_state.predictor.add_result("Player", random.randint(3, 9))
        st.rerun()

with col2:
    if st.button("🔴 BANKER", key="banker", use_container_width=True):
        st.session_state.predictor.add_result("Banker", random.randint(3, 9))
        st.rerun()

with col3:
    if st.button("🟣 TIE", key="tie", use_container_width=True):
        st.session_state.predictor.add_result("Tie", random.randint(3, 9))
        st.rerun()

with col4:
    if st.button("🔄 Reiniciar Sistema", key="reset", use_container_width=True):
        st.session_state.predictor.reset()
        st.rerun()

# Seção de Análise
if st.session_state.predictor.game_history:
    # Predição
    prediction, confidence = st.session_state.predictor.predict_next()
    tie_prob = st.session_state.predictor.get_tie_probability()
    
    # Sugestão da IA
    st.header("🔮 Sugestão da IA")
    if prediction:
        color = "#3b82f6" if prediction == 'Player' else "#ef4444" if prediction == 'Banker' else "#a855f7"
        st.markdown(f"""
        <div class="prediction-card">
            <div style="text-align:center;">
                <div style="font-size:28px; font-weight:bold; color:{color}; margin-bottom:10px;">
                    {prediction.upper()}
                </div>
                <div style="font-size:18px; margin-bottom:15px;">
                    Confiança: {confidence}%
                </div>
                <div style="height:10px; background:#e0e0e0; border-radius:5px; overflow:hidden;">
                    <div style="height:100%; width:{confidence}%; background:{color}; border-radius:5px;"></div>
                </div>
            </div>
            <div style="background:rgba(168, 85, 247, 0.15); padding:15px; border-radius:10px; margin-top:20px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>Probabilidade de Empate (Tie):</div>
                    <div style="font-size:24px; font-weight:bold; color:#a855f7;">{tie_prob}%</div>
                </div>
                <div style="height:10px; background:#e0e0e0; border-radius:5px; margin-top:10px; overflow:hidden;">
                    <div style="height:100%; width:{tie_prob}%; background:#a855f7; border-radius:5px;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Coletando dados para análise...")
    
    # Histórico de Jogos
    st.header("📜 Histórico de Jogos")
    history_html = '<div class="history-container">'
    for res, pts in zip(st.session_state.predictor.game_history[-12:], 
                      st.session_state.predictor.point_history[-12:]):
        card_class = "player-card" if res == "Player" else "banker-card" if res == "Banker" else "tie-card"
        result_char = "P" if res == "Player" else "B" if res == "Banker" else "T"
        
        history_html += f"""
        <div class="history-card {card_class}">
            <div class="points-display">{pts}</div>
            <div class="result-display">{result_char}</div>
        </div>
        """
    history_html += '</div>'
    st.markdown(history_html, unsafe_allow_html=True)
    
    # Estatísticas
    st.header("📊 Estatísticas")
    stats_html = '<div class="stats-container">'
    
    # Player
    stats_html += f"""
    <div class="stat-card">
        <div style="color:var(--player-color); font-size:22px; font-weight:bold; margin-bottom:10px;">Player</div>
        <div style="font-size:34px; font-weight:bold; color:var(--player-color);">
            {st.session_state.predictor.win_percentages['Player']}%
        </div>
    </div>
    """
    
    # Banker
    stats_html += f"""
    <div class="stat-card">
        <div style="color:var(--banker-color); font-size:22px; font-weight:bold; margin-bottom:10px;">Banker</div>
        <div style="font-size:34px; font-weight:bold; color:var(--banker-color);">
            {st.session_state.predictor.win_percentages['Banker']}%
        </div>
    </div>
    """
    
    # Tie
    stats_html += f"""
    <div class="stat-card">
        <div style="color:var(--tie-color); font-size:22px; font-weight:bold; margin-bottom:10px;">Tie</div>
        <div style="font-size:34px; font-weight:bold; color:var(--tie-color);">
            {st.session_state.predictor.win_percentages['Tie']}%
        </div>
    </div>
    """
    
    stats_html += '</div>'
    st.markdown(stats_html, unsafe_allow_html=True)
    
    # Gráfico de Tendência
    if len(st.session_state.predictor.point_history) > 1:
        st.header("📈 Tendência de Pontos")
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.line_chart({
                "Pontos": st.session_state.predictor.point_history[-20:]
            }, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Adicione mais resultados para ver o gráfico")

# Estado inicial
else:
    st.info("👆 Use os botões acima para registrar os primeiros resultados")

# Rodapé
st.markdown("---")
st.caption("Bac Bo PRO Predictor v6.0 | Sistema de análise preditiva avançada")
