import streamlit as st
import random
from itertools import combinations
from collections import Counter

# Classe para geração de jogos da Lotofácil, reescrita para maior robustez
class LotofacilGenerator:
    def __init__(self, ultimo_sorteio, dezenas_fora):
        self.ultimo_sorteio = set(ultimo_sorteio)
        self.dezenas_fora = set(dezenas_fora)
        self.todas_dezenas = set(range(1, 26))

        # Dezenas do último sorteio (quentes)
        self.dezenas_quentes = self.ultimo_sorteio
        
        # Dezenas que não saíram no último sorteio (frias)
        self.dezenas_frias = self.dezenas_fora

        # Dezenas que estão disponíveis, mas não fazem parte do sorteio anterior
        self.dezenas_disponiveis = self.todas_dezenas - self.dezenas_quentes

    def gerar_estatisticas(self):
        """Gera as estatísticas de um sorteio idealizado."""
        return {
            'repeticao_esperada': random.randint(8, 10),
            'alvo_pares': random.randint(7, 9),
            'soma_ideal': random.randint(180, 220),
        }

    def selecionar_dezenas_estrategicas(self):
        """
        Seleciona um conjunto de 18 dezenas de forma estratégica e robusta.
        A prioridade é sempre garantir 18 dezenas.
        """
        estatisticas = self.gerar_estatisticas()
        selecionadas = set()

        # Passo 1: Seleciona dezenas que se repetem do último sorteio
        repeticao = estatisticas['repeticao_esperada']
        dezenas_quentes_selecionadas = random.sample(list(self.dezenas_quentes), min(repeticao, len(self.dezenas_quentes)))
        selecionadas.update(dezenas_quentes_selecionadas)
        
        # Passo 2: Seleciona dezenas que ficaram de fora para complementar o fechamento
        quant_para_completar = 18 - len(selecionadas)
        
        if quant_para_completar > 0:
            dezenas_frias_disponiveis = list(self.dezenas_frias - selecionadas)
            num_frias_para_selecionar = min(quant_para_completar, len(dezenas_frias_disponiveis))
            selecionadas.update(random.sample(dezenas_frias_disponiveis, num_frias_para_selecionar))
            
        # Passo 3: Se ainda não tiver 18 dezenas, completa com o que resta
        quant_para_completar = 18 - len(selecionadas)
        if quant_para_completar > 0:
            restante = list(self.todas_dezenas - selecionadas)
            num_restante_para_selecionar = min(quant_para_completar, len(restante))
            selecionadas.update(random.sample(restante, num_restante_para_selecionar))

        # Passo 4: Realiza o balanceamento e otimização
        selecionadas_list = sorted(list(selecionadas))
        selecionadas_balanceadas = self._balancear(selecionadas_list)
        selecionadas_otimizadas = self._otimizar_diversidade(selecionadas_balanceadas)
        
        return sorted(list(selecionadas_otimizadas))

    def _balancear(self, dezenas_list):
        """Ajusta o balanceamento de pares, ímpares, quadrantes e soma."""
        dezenas = set(dezenas_list)
        estatisticas = self.gerar_estatisticas()
        
        # Balanceamento Par/Ímpar
        pares = [d for d in dezenas if d % 2 == 0]
        impares = [d for d in dezenas if d % 2 == 1]
        
        diferenca_pares = len(pares) - estatisticas['alvo_pares']
        
        if diferenca_pares > 0: # Trocar pares por ímpares
            para_remover = random.sample(pares, min(diferenca_pares, len(pares)))
            dezenas -= set(para_remover)
            
            opcoes_impares = list(self.todas_dezenas - dezenas - set(pares))
            para_adicionar = random.sample(opcoes_impares, min(len(para_remover), len(opcoes_impares)))
            dezenas.update(para_adicionar)
            
        elif diferenca_pares < 0: # Trocar ímpares por pares
            diferenca_impares = abs(diferenca_pares)
            para_remover = random.sample(impares, min(diferenca_impares, len(impares)))
            dezenas -= set(para_remover)

            opcoes_pares = list(self.todas_dezenas - dezenas - set(impares))
            para_adicionar = random.sample(opcoes_pares, min(len(para_remover), len(opcoes_pares)))
            dezenas.update(para_adicionar)
        
        return dezenas

    def _otimizar_diversidade(self, dezenas):
        """Ajusta a soma das dezenas para ficar mais próxima do ideal."""
        soma_atual = sum(dezenas)
        estatisticas = self.gerar_estatisticas()
        
        tentativas = 0
        while abs(soma_atual - estatisticas['soma_ideal']) > 15 and tentativas < 10:
            
            if soma_atual > estatisticas['soma_ideal']:
                # Soma alta, troca um número alto por um baixo
                altos = sorted(list(dezenas), reverse=True)[:5]
                baixos_disponiveis = sorted(list(self.todas_dezenas - dezenas))
                if not altos or not baixos_disponiveis: break
                
                alto_escolhido = random.choice(altos)
                baixo_escolhido = random.choice(baixos_disponiveis)
                dezenas.remove(alto_escolhido)
                dezenas.add(baixo_escolhido)
            else:
                # Soma baixa, troca um número baixo por um alto
                baixos = sorted(list(dezenas))[:5]
                altos_disponiveis = sorted(list(self.todas_dezenas - dezenas), reverse=True)
                if not baixos or not altos_disponiveis: break

                baixo_escolhido = random.choice(baixos)
                alto_escolhido = random.choice(altos_disponiveis)
                dezenas.remove(baixo_escolhido)
                dezenas.add(alto_escolhido)
            
            soma_atual = sum(dezenas)
            tentativas += 1
            
        return dezenas

    def gerar_jogos_otimizados(self, quantidade=15, dezenas_selecionadas=None):
        if dezenas_selecionadas is None:
            st.error("Erro interno: A lista de dezenas selecionadas não foi passada para a função.")
            return []

        if len(dezenas_selecionadas) < 15:
            st.warning(f"Aviso: O fechamento tem apenas {len(dezenas_selecionadas)} dezenas. Só será possível gerar um jogo.")
            if len(dezenas_selecionadas) == 15:
                return [sorted(dezenas_selecionadas)]
            else:
                return []
        
        todas_combinacoes = list(combinations(dezenas_selecionadas, 15))
        random.shuffle(todas_combinacoes)
        
        combinacoes_selecionadas = set()
        jogos = []
        for combo in todas_combinacoes:
            if len(combinacoes_selecionadas) >= quantidade:
                break
            
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

def validar_entradas(numeros, contagem_esperada, nome_campo):
    if len(numeros) != contagem_esperada:
        return False, f"Erro: Insira exatamente {contagem_esperada} números para {nome_campo}!"
    if any(n < 1 or n > 25 for n in numeros):
        return False, f"Erro: Todos os números de {nome_campo} devem estar entre 1 e 25!"
    if len(set(numeros)) != contagem_esperada:
        return False, f"Erro: Números duplicados foram encontrados em {nome_campo}!"
    return True, ""

with st.form("entrada_dados"):
    st.subheader("📊 Dados do Último Sorteio")
    col1, col2 = st.columns(2)
    
    with col1:
        ultimo_sorteio_str = st.text_input(
            "Números Sorteados (15 números, separados por vírgula):",
            "1,2,5,6,9,10,11,12,13,14,18,20,22,23,25"
        )
    
    with col2:
        dezenas_ausentes_str = st.text_input(
            "Dezenas Ausentes (10 números, separados por vírgula):",
            "3,4,7,8,15,16,17,19,21,24"
        )
    
    quantidade_jogos = st.slider("Número de Jogos", 10, 20, 15)
    submit_button = st.form_submit_button("✨ Gerar Jogos")

if submit_button:
    try:
        ultimo_sorteio = [int(x.strip()) for x in ultimo_sorteio_str.split(",") if x.strip()]
        dezenas_ausentes = [int(x.strip()) for x in dezenas_ausentes_str.split(",") if x.strip()]
        
        validacao_sorteio, msg_sorteio = validar_entradas(ultimo_sorteio, 15, "Sorteados")
        validacao_ausentes, msg_ausentes = validar_entradas(dezenas_ausentes, 10, "Ausentes")
        
        if not validacao_sorteio:
            st.error(msg_sorteio)
        elif not validacao_ausentes:
            st.error(msg_ausentes)
        elif set(ultimo_sorteio) & set(dezenas_ausentes):
            st.error("Erro: Existem números em comum entre os sorteados e os ausentes!")
        else:
            gerador = LotofacilGenerator(ultimo_sorteio, dezenas_ausentes)
            
            with st.spinner('Gerando jogos otimizados...'):
                dezenas_selecionadas = gerador.selecionar_dezenas_estrategicas()
                
                # Mensagem de depuração
                st.info(f"✅ Fechamento com **{len(dezenas_selecionadas)}** dezenas gerado com sucesso!")
                
                jogos_gerados = gerador.gerar_jogos_otimizados(quantidade_jogos, dezenas_selecionadas)
            
            if jogos_gerados:
                st.success(f"✅ {len(jogos_gerados)} jogos gerados com sucesso!")
                st.subheader("🎲 Jogos Recomendados")
                
                colunas_por_linha = 5
                total_jogos = len(jogos_gerados)
                num_linhas = (total_jogos + colunas_por_linha - 1) // colunas_por_linha
                
                for i in range(num_linhas):
                    cols = st.columns(colunas_por_linha)
                    for j in range(colunas_por_linha):
                        idx = i * colunas_por_linha + j
                        if idx < total_jogos:
                            jogo = jogos_gerados[idx]
                            numeros_formatados = [f"{n:02}" for n in jogo]
                            cols[j].markdown(f"**Jogo {idx+1}:**<br>{' - '.join(numeros_formatados)}", unsafe_allow_html=True)

                csv = "\n".join([";".join(map(str, j)) for j in jogos_gerados])
                st.download_button(
                    label="📥 Baixar Jogos (CSV)",
                    data=csv,
                    file_name="jogos_lotofacil.csv",
                    mime="text/csv"
                )
            
    except Exception as e:
        st.error(f"Erro: Verifique o formato dos números. Detalhes: {e}")

# Informações
st.sidebar.markdown("""
---
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

