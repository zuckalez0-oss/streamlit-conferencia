import streamlit as st
import pandas as pd
import altair as alt  # Importa a biblioteca Altair para gráficos mais avançados

def processar_dataframe(df): #funcao para processar o dataframe e exibir os dados e graficos
    """Função para processar o DataFrame e exibir os dados e gráficos."""
    st.header("Visão Geral dos Dados")
    
    # Converte a coluna 'Qtd' para um tipo numérico, tratando erros.
    df['Qtd'] = pd.to_numeric(df['Qtd'], errors='coerce')

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Projetos", f"{df['Projeto'].nunique()}") #nunique() conta o número de valores únicos na coluna 'Projeto'
    col2.metric("Total de Desenhos", f"{len(df)}") #len(df) retorna o número total de linhas no DataFrame
    col3.metric("Quantidade Total de Itens", f"{df['Qtd'].sum():.0f}") #soma os valores na coluna 'Qtd' e formata como inteiro

    st.write("Dados da planilha:")
    st.dataframe(df)
    st.markdown("---")
#explicação Streamlit para upload e análise de planilhas Excel contendo dados de desenhos

# Título da aplicação Streamlit

st.title("Levantamento de Desenhos") #Título da aplicação Streamlit

st.header("1. Faça o upload da sua planilha")
uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=['xlsx']) #usando file_uploader do streamlit para upload de arquivos Excel 

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file) #Lê o arquivo Excel usando pandas
    except Exception as e:
        st.error(f"Erro ao ler o arquivo Excel: {e}") # Exibe uma mensagem de erro se o arquivo não puder ser lido
        st.stop() # Interrompe a execução se houver erro ao ler o arquivo

    st.markdown("---")
    st.header("2. Lista de Projetos e Quantidade de Desenhos")
    contagem = df["Projeto"].value_counts().reset_index() #Conta a ocorrência de cada projeto na coluna 'Projeto'
    contagem.columns = ['Projeto', 'Qtd de desenhos'] #Renomeia as colunas para 'Projeto' e 'Contagem'
    st.dataframe(contagem, use_container_width=True) #Exibe o DataFrame de contagem no Streamlit e ajusta a largura do contêiner
    st.markdown("---")
    
    st.header("Resumo de Orçamentos") #Novo cabeçalho para a seção de resumo de orçamentos
    contagem_total_de_projetos = len(contagem)
    
    # --- ALTERAÇÃO AQUI ---
    # Correção: Usar col1.metric e col2.metric para exibir nas colunas definidas
    col1, col2 = st.columns(2)
    col1.metric("Total de Projetos", contagem_total_de_projetos)
    col2.metric("Total de Desenhos", len(df))
    # --- FIM DA ALTERAÇÃO ---
    
    # Verifica se a coluna 'Orçamento Fechado?' existe no DataFrame
    if 'Orçamento Fechado?' in df.columns:
        orcamento_contagem = df['Orçamento Fechado?'].value_counts().reset_index() #Conta a ocorrência de cada status na coluna 'Orçamento Fechado?'
        orcamento_contagem.columns = ['Orçamento Fechado?', 'Qtd de desenhos'] #Renomeia as colunas
        orcamento_contagem_total = orcamento_contagem['Qtd de desenhos'].sum()
        orcamento_fechado_sim = orcamento_contagem[orcamento_contagem['Orçamento Fechado?'] == 'SIM']['Qtd de desenhos'].values
        total_de_orcamentos = len(orcamento_contagem)
        
        col1_orc, col2_orc = st.columns(2)
        col1_orc.metric("Desenhos Fechados", orcamento_fechado_sim[0] if len(orcamento_fechado_sim) > 0 else 0)
        col2_orc.metric('Desenhos em Aberto', orcamento_contagem_total - (orcamento_fechado_sim[0] if len(orcamento_fechado_sim) > 0 else 0))
    else:
        st.info("Coluna 'Orçamento Fechado?' não encontrada na planilha.")

    st.markdown("---")

        
        
        

    
#====Análise dos dados carregados====

    st.header("3. Análise dos Dados")

    # Converte a coluna 'Qtd' para um tipo numérico, tratando erros.

    df['Qtd'] = pd.to_numeric(df['Qtd'], errors='coerce') # Converte a coluna 'Qtd' para numérico, tratando erros

    col1_graf, col2_graf = st.columns(2) #Cria duas colunas no streamlit para exibir gráficos lado a lado

    with col1_graf: #operador with para agrupar elementos na primeira coluna
        # --- ALTERAÇÃO AQUI ---
        # Gráfico de barras (Altair) para quantidade por espessura com cores
        st.write("#### Quantidade de Itens por Espessura")
        # Agrupa por 'Espessura' e soma a 'Qtd', tratando valores não numéricos
        qtd_por_espessura = df.groupby('Esp')['Qtd'].sum().dropna().reset_index()
        
        if not qtd_por_espessura.empty:
            qtd_por_espessura.columns = ['Espessura', 'Quantidade'] # Renomeia colunas
            
            # Cria o gráfico Altair
            chart = alt.Chart(qtd_por_espessura).mark_bar().encode(
                x=alt.X('Espessura:N', sort=None), # Trata Espessura como Categórico (Nominal)
                y=alt.Y('Quantidade:Q'), # Trata Quantidade como Quantitativo
                color=alt.Color('Espessura:N', legend=None), # Define a cor baseada na Espessura
                tooltip=['Espessura', 'Quantidade'] # Adiciona tooltip
            ).interactive() # Permite zoom e pan
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.write("Não há dados de quantidade para exibir por espessura.")
        # --- FIM DA ALTERAÇÃO ---

    with col2_graf:
        # Gráfico de barras para quantidade de desenhos por projeto
        st.write("#### Quantidade de Desenhos por Projeto")
        desenhos_por_projeto = df['Projeto'].value_counts()
        st.bar_chart(desenhos_por_projeto) # Mantém st.bar_chart simples aqui

#====fim da seção de análise dos dados====
    
    st.markdown("---")
    st.header("4. Filtrar por Projeto")

    projeto_filtrado = st.text_input("Digite o nome do projeto:", "") #Cria um campo de entrada de texto para filtrar por projeto

    if projeto_filtrado:
        df_filtrado = df[df['Projeto'].astype(str).str.contains(projeto_filtrado, case=False, na=False)] #case =False para ignorar maiúsculas/minúsculas #na =False para evitar erros com valores NaN
        
        if df_filtrado.empty: # Verifica se o DataFrame filtrado está vazio
            st.warning("Nenhum dado encontrado para o filtro aplicado.") # Exibe um aviso se nenhum dado for encontrado
        else:
            st.write(f"Dados filtrados para o projeto contendo '{projeto_filtrado}':")
            st.dataframe(df_filtrado)
            
            st.markdown(f"##### Estatísticas do Projeto: *{projeto_filtrado}*")
            
            # Garante que 'Qtd' e 'Kg Total' sejam numéricos antes de somar
            df_filtrado['Qtd'] = pd.to_numeric(df_filtrado['Qtd'], errors='coerce')
            df_filtrado['Kg Total'] = pd.to_numeric(df_filtrado['Kg Total'], errors='coerce')

            total_desenhos_filtrados = len(df_filtrado)
            total_qtd_filtrada = df_filtrado['Qtd'].sum()
            peso_total_filtrado = df_filtrado['Kg Total'].sum()

            col1_stats, col2_stats, col3_stats = st.columns(3)
            col1_stats.metric("Total de desenhos", total_desenhos_filtrados)
            col2_stats.metric("Qtd total de peças", f"{total_qtd_filtrada:.0f}")
            col3_stats.metric("Peso total (Kg)", f"{peso_total_filtrado:.2f}") #usa metric para exibir as estatísticas do projeto filtrado

            # --- ALTERAÇÃO AQUI ---
            # Gráfico de barras (Altair) para o filtro
            st.write("##### Qtd de Itens por Espessura (Projeto Filtrado)")
            qtd_por_espessura_filtrado = df_filtrado.groupby('Esp')['Qtd'].sum().dropna().reset_index()
            
            if not qtd_por_espessura_filtrado.empty:
                qtd_por_espessura_filtrado.columns = ['Espessura', 'Quantidade']
                
                chart_filtrado = alt.Chart(qtd_por_espessura_filtrado).mark_bar().encode(
                    x=alt.X('Espessura:N', sort=None),
                    y=alt.Y('Quantidade:Q'),
                    color=alt.Color('Espessura:N', legend=None),
                    tooltip=['Espessura', 'Quantidade']
                ).interactive()
                
                st.altair_chart(chart_filtrado, use_container_width=True)
            else:
                st.write("Não há dados de quantidade para exibir por espessura neste projeto.")
            # --- FIM DA ALTERAÇÃO ---

else:
    st.info("Aguardando o upload de um arquivo Excel para iniciar a análise.")
