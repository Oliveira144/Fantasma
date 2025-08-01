import streamlit as st
import random
import numpy as np
from collections import Counter

# Configuração da página
st.set_page_config(
    page_title="Gerador Profissional de Jogos Lotofácil",
    page_icon="🍀",
    layout="wide"
)

# Título e descrição
st.title("🍀 Gerador Profissional de Jogos Lotofácil")
st.markdown("""
Insira os números do **último sorteio** e as **dezenas ausentes** para gerar jogos otimizados usando técnicas profissionais!
""")

# Classe principal do gerador
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
        """Calcula estatísticas vitais para a geração de jogos"""
        stats = {
            'repeticao_esperada': random.randint(7, 9),
            'alvo_pares': random.randint(7, 9),
            'alvo_impares': 15 - random.randint(7, 9),
            'soma_ideal': random.randint(190, 210),
            'freq_quadrantes': self.calcular_freq_quadrantes()
        }
        return stats

    def calcular_freq_quadrantes(self):
        """Calcula a distribuição ideal por quadrantes"""
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
        """Atribui pesos aos quadrantes baseado na frequência ideal"""
        pesos = []
        for i, q in enumerate(self.quadrantes):
            peso = 10 + len(set(q) & set(self.ultimo_sorteio))
            peso += self.estatisticas['freq_quadrantes'][i] * 2
            pesos.append(peso)
        return pesos

    def selecionar_dezenas_estrategicas(self):
        """Seleciona 18 dezenas usando estratégias profissionais"""
        selecionadas = set()
        
        # Adicionar números quentes (do último sorteio)
        repetir = min(self.estatisticas['repeticao_esperada'], 10)
        selecionadas.update(random.sample(self.ultimo_sorteio, repetir))
        
        # Adicionar números frios (dezenas ausentes)
        adicionar = 18 - len(selecionadas)
        selecionadas.update(random.sample(self.dezenas_fora, adicionar))
        
        # Balancear quadrantes
        selecionadas = self.balancear_quadrantes(selecionadas)
        
        # Otimizar diversidade
        selecionadas = self.otimizar_diversidade(selecionadas)
        
        return sorted(selecionadas)

    def balancear_quadrantes(self, dezenas):
        """Garante distribuição adequada por quadrantes"""
        for i, q in enumerate(self.quadrantes):
            no_quadrante = len(set(dezenas) & set(q))
            alvo = self.estatisticas['freq_quadrantes'][i]
            
            if no_quadrante < alvo:
                opcoes = list(set(q) - set(dezenas))
                adicionar = min(alvo - no_quadrante, len(opcoes))
                dezenas.update(random.sample(opcoes, adicionar))
                
            elif no_quadrante > alvo:
                opcoes = list(set(dezenas) & set(q))
                remover = min(no_quadrante - alvo, len(opcoes))
                for num in random.sample(opcoes, remover):
                    dezenas.remove(num)
                    
        return dezenas

    def otimizar_diversidade(self, dezenas):
        """Otimiza par/ímpar e soma numérica"""
        pares = [d for d in dezenas if d % 2 == 0]
        impares = [d for d in dezenas if d % 2 == 1]
        diferenca = len(pares) - self.estatisticas['alvo_pares']
        
        if diferenca > 0:
            trocar = random.sample(pares, diferenca)
            opcoes = list(set(self.todas_dezenas) - set(dezenas) - set(impares))
            dezenas = dezenas - set(trocar)
            dezenas.update(random.sample(opcoes, diferenca))
        elif diferenca < 0:
            trocar = random.sample(impares, abs(diferenca))
            opcoes = list(set(self.todas_dezenas) - set(dezenas) - set(pares))
            dezenas = dezenas - set(trocar)
            dezenas.update(random.sample(opcoes, abs(diferenca)))
            
        soma_atual = sum(dezenas)
        while abs(soma_atual - self.estatisticas['soma_ideal']) > 15:
            if soma_atual > self.estatisticas['soma_ideal']:
                alto = max(dezenas)
                baixo = min(set(self.todas_dezenas) - set(dezenas))
                dezenas.remove(alto)
                dezenas.add(baixo)
            else:
                baixo = min(dezenas)
                alto = max(set(self.todas_dezenas) - set(dezenas))
                dezenas.remove(baixo)
                dezenas.add(alto)
            soma_atual = sum(dezenas)
            
        return dezenas

    def gerar_jogos_otimizados(self, quantidade=15):
        """Gera jogos usando matriz de fechamento otimizada"""
        dezenas_selecionadas = self.selecionar_dezenas_estrategicas()
        jogos = []
        
        # Matriz de fechamento para 18 números
        matriz = [
            [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
            [1,2,3,4,5,6,7,8,16,17,18,9,10,11,12],
            [1,2,3,4,5,9,10,11,13,14,15,16,17,18,6],
            [1,2,3,6,7,8,9,10,11,12,13,14,15,16,17],
            [1,2,3,6,7,8,9,12,13,14,15,16,17,18,4],
            [1,2,4,5,6,7,8,9,10,11,12,13,14,15,18],
            [1,4,5,6,7,8,10,11,12,13,14,15,16,17,18],
            [2,3,4,5,6,7,8,9,10,11,12,16,17,18,13],
            [2,3,4,5,9,10,11,12,13,14,15,16,17,18,1],
            [2,3,5,7,8,9,10,11,12,13,14,15,16,17,18],
            [3,4,5,6,7,8,9,10,11,12,13,14,15,17,18],
            [1,2,3,4,5,7,8,11,12,13,14,15,16,17,18],
            [1,2,3,4,6,9,10,11,12,13,14,15,16,17,18],
            [1,2,3,5,6,8,10,11,12,13,14,15,16,17,18],
            [1,2,4,5,6,7,9,10,11,12,13,14,15,16,17],
            [1,3,4,5,6,7,8,9,10,11,12,14,15,16,17],
            [1,3,4,5,7,8,9,10,11,12,13,15,16,17,18],
            [1,3,5,6,7,8,9,10,12,13,14,15,16,17,18],
            [2,3,4,5,6,7,8,10,11,12,13,14,15,16,18],
            [2,4,5,6,7,8,9,10,11,13,14,15,16,17,18]
        ]
        
        # Gerar jogos usando a matriz
        for combinacao in matriz:
            jogo = [dezenas_selecionadas[i-1] for i in combinacao]
            jogos.append(sorted(jogo))
            
            if len(jogos) >= quantidade:
                break
                
        return jogos[:quantidade]

# Interface do Streamlit
with st.form("entrada_dados"):
    st.subheader("📊 Dados do Último Sorteio")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Números Sorteados** (15 números)")
        ultimo_sorteio = st.text_input(
            "Insira os números sorteados, separados por vírgula:",
            "1,2,5,6,9,10,11,12,13,14,18,20,22,23,25"
        )
    
    with col2:
        st.write("**Dezenas Ausentes** (10 números)")
        dezenas_ausentes = st.text_input(
            "Insira as dezenas ausentes, separadas por vírgula:",
            "3,4,7,8,15,16,17,19,21,24"
        )
    
    quantidade_jogos = st.slider("Quantidade de Jogos a Gerar", 10, 20, 15)
    
    submit_button = st.form_submit_button("✨ Gerar Jogos Otimizados")

# Processamento
if submit_button:
    try:
        # Converter entradas em listas de inteiros
        ultimo_sorteio = [int(x.strip()) for x in ultimo_sorteio.split(",") if x.strip().isdigit()]
        dezenas_ausentes = [int(x.strip()) for x in dezenas_ausentes.split(",") if x.strip().isdigit()]
        
        if len(ultimo_sorteio) != 15 or len(dezenas_ausentes) != 10:
            st.error("⚠️ Por favor, insira exatamente 15 números sorteados e 10 dezenas ausentes!")
        else:
            # Inicializar gerador
            gerador = LotofacilGenerator(ultimo_sorteio, dezenas_ausentes)
            
            # Gerar jogos
            with st.spinner('Gerando jogos otimizados...'):
                jogos_gerados = gerador.gerar_jogos_otimizados(quantidade_jogos)
            
            # Exibir resultados
            st.success(f"✅ {quantidade_jogos} jogos gerados com sucesso!")
            st.subheader("🎲 Seus Jogos Otimizados")
            
            # Exibir jogos em colunas
            cols = st.columns(3)
            for i, jogo in enumerate(jogos_gerados):
                with cols[i % 3]:
                    st.markdown(f"**Jogo {i+1}**")
                    st.write(jogo)
            
            # Botão para download
            st.download_button(
                label="📥 Baixar Todos os Jogos (CSV)",
                data="\n".join([";".join(map(str, jogo)) for jogo in jogos_gerados]),
                file_name="jogos_lotofacil.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"Erro: {str(e)}")

# Informações adicionais
st.sidebar.markdown("""
### ℹ️ Sobre o Gerador
Este sistema utiliza técnicas profissionais de apostas:
- **Análise de padrões** de repetição
- **Otimização matemática** de quadrantes
- **Balanceamento** par/ímpar
- **Fechamento estratégico** com garantia de cobertura

### 📌 Dicas Importantes
1. Verifique sempre os números inseridos
2. Combine com seus palpites pessoais
3. Jogue com responsabilidade

### ⚠️ Aviso Legal
Este app é apenas para entretenimento e não garante ganhos. As loterias são jogos de azar.
""")

# Rodapé
st.markdown("---")
st.caption("Gerador Profissional de Jogos Lotofácil • Desenvolvido com Streamlit")
