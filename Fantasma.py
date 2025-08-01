import streamlit as st
import random
import numpy as np
from collections import Counter
from itertools import combinations

# Classe Corrigida com Geração de Fechamento Real
class LotofacilGenerator:
    def __init__(self, ultimo_sorteio, dezenas_fora):
        self.ultimo_sorteio = sorted(ultimo_sorteio)
        self.dezenas_fora = sorted(dezenas_fora)
        self.todas_dezenas = list(range(1, 26))
        self.quadrantes = [
            [1, 2, 3, 4, 5],
            [6, 7, 8, 9, 10],
            [11, 12, 13, 14, 15],
            [16, 17, 18, 19, 20],
            [21, 22, 23, 24, 25]
        ]
        self.estatisticas = self.calcular_estatisticas()
        self.peso_quadrantes = self.calcular_peso_quadrantes()

    def calcular_estatisticas(self):
        stats = {
            'repeticao_esperada': random.randint(7, 9),
            'alvo_pares': random.randint(7, 9),
            'alvo_impares': 15 - random.randint(7, 9),
            'soma_ideal': random.randint(190, 210),
            'freq_quadrantes': self.calcular_freq_quadrantes()
        }
        return stats

    def calcular_freq_quadrantes(self):
        freq = []
        total = 15
        for _ in range(5):
            q_min = max(1, total - 4 * (4 - len(freq)))
            q_max = min(4, total - 1 * (4 - len(freq)))
            valor = random.randint(q_min, q_max)
            freq.append(valor)
            total -= valor
        return freq

    def calcular_peso_quadrantes(self):
        pesos = []
        for i, q in enumerate(self.quadrantes):
            peso = 10 + len(set(q) & set(self.ultimo_sorteio))
            peso += self.estatisticas['freq_quadrantes'][i] * 2
            pesos.append(peso)
        return pesos

    def selecionar_dezenas_estrategicas(self):
        selecionadas = set()
        
        # 1. Adicionar números quentes com verificação de tamanho
        repetir = min(self.estatisticas['repeticao_esperada'], len(self.ultimo_sorteio))
        if repetir > 0:
            selecionadas.update(random.sample(self.ultimo_sorteio, repetir))
        
        # 2. Adicionar números frios com verificação de tamanho
        disponiveis = list(set(self.dezenas_fora) - selecionadas)
        adicionar = min(18 - len(selecionadas), len(disponiveis))
        if adicionar > 0:
            selecionadas.update(random.sample(disponiveis, adicionar))
        
        # 3. Completar com números aleatórios se necessário
        if len(selecionadas) < 18:
            disponiveis = list(set(self.todas_dezenas) - selecionadas)
            adicionar = 18 - len(selecionadas)
            selecionadas.update(random.sample(disponiveis, min(adicionar, len(disponiveis)))
        
        # 4. Balanceamento
        selecionadas = self.balancear_quadrantes(selecionadas)
        selecionadas = self.otimizar_diversidade(selecionadas)
        
        return sorted(selecionadas)

    def balancear_quadrantes(self, dezenas):
        dezenas = set(dezenas)
        for i, q in enumerate(self.quadrantes):
            no_quadrante = len(dezenas & set(q))
            alvo = self.estatisticas['freq_quadrantes'][i]
            
            if no_quadrante < alvo:
                opcoes = list(set(q) - dezenas)
                adicionar = min(alvo - no_quadrante, len(opcoes))
                if adicionar > 0:
                    dezenas |= set(random.sample(opcoes, adicionar))
                
            elif no_quadrante > alvo:
                opcoes = list(dezenas & set(q))
                remover = min(no_quadrante - alvo, len(opcoes))
                if remover > 0:
                    dezenas -= set(random.sample(opcoes, remover))
                    
        return dezenas

    def otimizar_diversidade(self, dezenas):
        dezenas = set(dezenas)
        pares = [d for d in dezenas if d % 2 == 0]
        impares = [d for d in dezenas if d % 2 == 1]
        diferenca = len(pares) - self.estatisticas['alvo_pares']
        
        # Correção para evitar amostras maiores que a população
        if diferenca > 0:
            trocar = min(diferenca, len(pares))
            if trocar > 0:
                remover = random.sample(pares, trocar)
                dezenas -= set(remover)
                opcoes = [n for n in self.todas_dezenas 
                          if n not in dezenas and n % 2 == 1]
                adicionar = min(trocar, len(opcoes))
                if adicionar > 0:
                    dezenas |= set(random.sample(opcoes, adicionar))
                    
        elif diferenca < 0:
            trocar = min(abs(diferenca), len(impares))
            if trocar > 0:
                remover = random.sample(impares, trocar)
                dezenas -= set(remover)
                opcoes = [n for n in self.todas_dezenas 
                          if n not in dezenas and n % 2 == 0]
                adicionar = min(trocar, len(opcoes))
                if adicionar > 0:
                    dezenas |= set(random.sample(opcoes, adicionar))
        
        # Ajuste de soma com proteção contra loops infinitos
        soma_atual = sum(dezenas)
        tentativas = 0
        while abs(soma_atual - self.estatisticas['soma_ideal']) > 15 and tentativas < 10:
            if soma_atual > self.estatisticas['soma_ideal']:
                altos = sorted(dezenas, reverse=True)[:5]
                baixos_disponiveis = sorted(set(self.todas_dezenas) - dezenas)
                if altos and baixos_disponiveis:
                    alto_escolhido = random.choice(altos)
                    baixo_escolhido = random.choice(baixos_disponiveis)
                    dezenas.remove(alto_escolhido)
                    dezenas.add(baixo_escolhido)
            else:
                baixos = sorted(dezenas)[:5]
                altos_disponiveis = sorted(set(self.todas_dezenas) - dezenas, reverse=True)
                if baixos and altos_disponiveis:
                    baixo_escolhido = random.choice(baixos)
                    alto_escolhido = random.choice(altos_disponiveis)
                    dezenas.remove(baixo_escolhido)
                    dezenas.add(alto_escolhido)
            
            soma_atual = sum(dezenas)
            tentativas += 1
            
        return dezenas

    def gerar_jogos_otimizados(self, quantidade=15):
        dezenas_selecionadas = self.selecionar_dezenas_estrategicas()
        jogos = []
        
        # Algoritmo de fechamento real com combinações únicas
        todas_combinacoes = list(combinations(dezenas_selecionadas, 15))
        random.shuffle(todas_combinacoes)
        
        # Selecionar combinações únicas mantendo diversidade
        combinacoes_selecionadas = set()
        for combo in todas_combinacoes:
            if len(combinacoes_selecionadas) >= quantidade:
                break
                
            # Verificar diversidade
            combo_set = frozenset(combo)
            if combo_set not in combinacoes_selecionadas:
                combinacoes_selecionadas.add(combo_set)
                jogos.append(sorted(combo))
                
        return jogos[:quantidade]

# Interface Streamlit
st.set_page_config(
    page_title="Gerador Profissional Lotofácil",
    page_icon="🎰",
    layout="wide"
)

st.title("🎰 Gerador Profissional de Jogos Lotofácil")
st.markdown("""
Insira os números do **último sorteio** e as **dezenas ausentes** para gerar jogos otimizados!
""")

with st.form("entrada_dados"):
    st.subheader("📊 Dados do Último Sorteio")
    col1, col2 = st.columns(2)
    
    with col1:
        ultimo_sorteio = st.text_input(
            "Números Sorteados (15 números, separados por vírgula):",
            "1,2,5,6,9,10,11,12,13,14,18,20,22,23,25"
        )
    
    with col2:
        dezenas_ausentes = st.text_input(
            "Dezenas Ausentes (10 números, separados por vírgula):",
            "3,4,7,8,15,16,17,19,21,24"
        )
    
    quantidade_jogos = st.slider("Número de Jogos", 10, 20, 15)
    submit_button = st.form_submit_button("✨ Gerar Jogos")

if submit_button:
    try:
        ultimo_sorteio = [int(x.strip()) for x in ultimo_sorteio.split(",")]
        dezenas_ausentes = [int(x.strip()) for x in dezenas_ausentes.split(",")]
        
        if len(ultimo_sorteio) != 15 or len(dezenas_ausentes) != 10:
            st.error("Erro: Insira exatamente 15 números sorteados e 10 dezenas ausentes!")
        else:
            gerador = LotofacilGenerator(ultimo_sorteio, dezenas_ausentes)
            with st.spinner('Gerando jogos otimizados...'):
                jogos_gerados = gerador.gerar_jogos_otimizados(quantidade_jogos)
            
            st.success(f"✅ {len(jogos_gerados)} jogos gerados com sucesso!")
            st.subheader("🎲 Jogos Recomendados")
            
            # Exibição horizontal com formatação profissional
            for i, jogo in enumerate(jogos_gerados, 1):
                # Formatar números com 2 dígitos
                numeros_formatados = [f"{n:02}" for n in jogo]
                st.markdown(f"**Jogo {i}:** {' - '.join(numeros_formatados)}")
            
            # Download
            csv = "\n".join([";".join(map(str, j)) for j in jogos_gerados])
            st.download_button(
                label="📥 Baixar Jogos (CSV)",
                data=csv,
                file_name="jogos_lotofacil.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"Erro: {str(e)}")

# Informações
st.sidebar.markdown("""
### 🔍 Como Funciona
1. Insira os 15 números do último sorteio
2. Insira as 10 dezenas que ficaram de fora
3. O sistema aplica estratégias profissionais:
   - Análise de repetição (7-9 números)
   - Balanceamento de quadrantes
   - Otimização par/ímpar
   - Controle de soma numérica
4. Gera 10-20 jogos otimizados

### ⚠️ Aviso Legal
Este app é para entretenimento e não garante ganhos. Jogue com responsabilidade.
""")
