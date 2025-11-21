import streamlit as st
import pandas as pd
import altair as alt
import datetime # Importa a biblioteca de data
import re # Importa regex para extrair números

# Título da aplicação
st.set_page_config(layout="wide")
st.title('Ferramenta de Conferência de Dados')




# --- INÍCIO DA ALTERAÇÃO (Constante para o Grupo) ---
NOME_GRUPO_GALVANIZADO = "PERFIL GALVANIZADO" # Defina o nome exato do grupo aqui
# --- FIM DA ALTERAÇÃO ---

# Componente para upload de arquivo
uploaded_file = st.file_uploader("1. Escolha sua planilha (CSV ou Excel)", type=['csv', 'xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # ALTERAÇÃO 1: 'header=1' para ler a 2ª linha como cabeçalho
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=1) 
        else:
            df = pd.read_excel(uploaded_file, header=1)

        # --- INÍCIO DA ALTERAÇÃO 13: Excluir a última linha (linha de total) ---
        if not df.empty:
            df = df.iloc[:-1] # Remove a última linha do DataFrame
        # --- FIM DA ALTERAÇÃO 13 ---

        # --- INÍCIO DA ALTERAÇÃO 12 (Substitui 11.1) ---
        # Limpa espaços em branco (início/fim) E normaliza espaços duplos/múltiplos para um único espaço.
        df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
        # --- FIM DA ALTERAÇÃO 12 ---
        
        # --- INÍCIO DA ALTERAÇÃO (Seleção Dinâmica de Colunas) ---
        
        # 1. Define as colunas que SEMPRE queremos excluir por padrão (LISTA ATUALIZADA)
        colunas_excluidas_padrao = [
            "Emitir",
            "Obs Op",
            "Selec",
            "Data desenvolvimento",
            "Nº Proc.",
            "Sit.",
            "Nº Desenvolvimento",
            "Sequência desenvolvimento",
            "Bitola",
            "Sub Grupo_1",
            "Coleção",
            "Modelagem",
            "Ind. Terceiros",
            "Data Cancelamento",
            "Data Encerramento",
            "Usuário Cancelou",
            "Usuário Encerrou",
            "BLOCO 2"
        ]
        
        # 2. Pega todas as colunas disponíveis no 'df' original
        todas_as_colunas = df.columns.tolist()
        
        # 3. Filtra a lista padrão para incluir apenas colunas que REALMENTE existem no 'df'
        default_excluir = [col for col in colunas_excluidas_padrao if col in todas_as_colunas]
        
        # 4. Cria o widget multiselect dentro de um expander
        with st.expander("Configurações Avançadas: Excluir Colunas da Análise"):
            colunas_para_excluir_selecionadas = st.multiselect(
                label="Selecione as colunas para excluir da visualização e análise:",
                options=todas_as_colunas,
                default=default_excluir,
                help="Colunas selecionadas aqui serão removidas. Desmarque se precisar analisar alguma delas (ex: 'Pedido')."
            )
        
        # 5. df_display é o nosso dataframe "limpo"
        df_display = df.drop(columns=colunas_para_excluir_selecionadas, errors='ignore')
        
        # --- FIM DA ALTERAÇÃO ---

        # Copia o dataframe para aplicar filtros de exibição
        df_filtered = df_display.copy()

        # --- INÍCIO DA ALTERAÇÃO 5: NOVOS FILTROS E 3 MÉTRICAS DE PESO ---
        
        st.header("Filtros e Detalhamento de Peso")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # --- INÍCIO DA ALTERAÇÃO (Verificar se colunas de data ainda existem) ---
            # Pega as colunas disponíveis DEPOIS da exclusão
            colunas_disponiveis = ["Nenhuma"] + df_display.columns.tolist()
            # --- FIM DA ALTERAÇÃO ---
            
            # --- INÍCIO DA ALTERAÇÃO (Filtro de Data Padrão) ---
            default_date_col = "Data Emissão"
            default_index = 0 # Padrão é "Nenhuma"
            if default_date_col in colunas_disponiveis:
                default_index = colunas_disponiveis.index(default_date_col)
            
            coluna_data = st.selectbox(
                "Primeiro, selecione a coluna de data para filtros/métricas:", # ALTERAÇÃO 14.1: Texto mais claro
                options=colunas_disponiveis,
                index=default_index # Define o valor padrão
            )
            # --- FIM DA ALTERAÇÃO ---
        
        grupos_selecionados = [] # Inicializa a lista
        with col2:
            try:
                grupos_disponiveis = df_filtered['Grupo'].dropna().unique().tolist()
                grupos_selecionados = st.multiselect(
                    "Filtrar por Grupo:",
                    options=grupos_disponiveis
                )
                if grupos_selecionados: 
                    df_filtered = df_filtered[df_filtered['Grupo'].isin(grupos_selecionados)]
            except KeyError:
                st.info("Coluna 'Grupo' não encontrada (provavelmente foi excluída).")
        
        col3, col4 = st.columns(2)
        
        # --- INÍCIO DA ALTERAÇÃO (Filtros Condicionais) ---
        fator_kg_m = 1.0
        sub_grupos_selecionados = []

        with col3:
            # LÓGICA CONDICIONAL: Só mostra se o grupo "PERFIL GALVANIZADO" for selecionado
            if NOME_GRUPO_GALVANIZADO in grupos_selecionados:
                try:
                    # 1. Filtro de Sub Grupo
                    sub_grupos_disponiveis = df_filtered['Sub Grupo'].dropna().unique().tolist()
                    sub_grupos_selecionados = st.multiselect(
                        "Filtrar por Sub Grupo:",
                        options=sub_grupos_disponiveis
                    )
                    # Aplica o filtro de subgrupo imediatamente
                    if sub_grupos_selecionados: 
                        df_filtered = df_filtered[df_filtered['Sub Grupo'].isin(sub_grupos_selecionados)]
                    
                    # 2. Fator de Conversão
                    fator_kg_m = st.number_input(
                        "Fator de Conversão (kg/m):", 
                        value=1.0, 
                        min_value=0.01, 
                        format="%.4f",
                        help="Insira quantos KG existem por Metro de telha/perfil. Ex: 0.473"
                    )

                except KeyError:
                    st.info("Coluna 'Sub Grupo' não encontrada (provavelmente foi excluída).")
            
            # Filtro de Descrição (original)
            try:
                texto_descricao = st.text_input("Filtrar por Descrição do Produto (contém):")
                
                if texto_descricao: 
                    df_filtered = df_filtered[
                        df_filtered['Descrição do Produto'].str.contains(texto_descricao, case=False, na=False)
                    ]
            except KeyError:
                st.info("Coluna 'Descrição do Produto' não encontrada (provavelmente foi excluída).")
        # --- FIM DA ALTERAÇÃO ---
        
        with col4:
            # --- INÍCIO DA ALTERAÇÃO (Req: Filtrar tabela pela data) ---
            # 1. Label e Help atualizados
            data_especifica = st.date_input(
                "Filtrar por data específica (e Métrica 1):", # Label atualizado
                value=None, # Começa sem data selecionada
                help="Selecione uma data para 'Métrica 1'. Esta data **também filtrará a tabela principal** (a menos que 'Filtrar hoje' esteja marcado)." # Help atualizado
            )
            # --- FIM DA ALTERAÇÃO ---
            
            filtrar_hoje = st.checkbox(
                "Filtrar tabela principal pela data de hoje", 
                value=False,
                help="Se marcado, a tabela principal exibirá apenas os registros da data de hoje (baseado na coluna de data selecionada)."
            )

        # --- Conversão de data antecipada para uso nos filtros e métricas ---
        if coluna_data != "Nenhuma" and coluna_data in df_filtered.columns:
            # Converte a coluna de data principal
            df_filtered[coluna_data] = pd.to_datetime(df_filtered[coluna_data], errors='coerce')
            
            # --- INÍCIO DA CORREÇÃO (Nome da coluna com ponto) ---
            # Converte a Dt. Término Prod. (se existir) para a Análise 10
            if 'Dt. Término Prod.' in df_filtered.columns:
                 df_filtered['Dt. Término Prod.'] = pd.to_datetime(df_filtered['Dt. Término Prod.'], errors='coerce')
            # --- FIM DA CORREÇÃO ---


        # --- Cálculo das 3 Métricas ---
        df_metricas = df_filtered.copy() # df_metricas agora reflete TODOS os filtros (Grupo, SubGrupo, Descrição)
        peso_data_especifica = 0.0
        peso_sem_data = 0.0
        peso_total = 0.0

        try:
            # ALTERAÇÃO 6: CORREÇÃO DO CÁLCULO DE PESO (Remove vírgula do milhar)
            plan_str = df_metricas['PLANEJAMENTO'].astype(str).str.replace(',', '', regex=False)
            prod_str = df_metricas['PRODUCAO'].astype(str).str.replace(',', '', regex=False)
            
            plan = pd.to_numeric(plan_str, errors='coerce').fillna(0)
            prod = pd.to_numeric(prod_str, errors='coerce').fillna(0)
            
            df_metricas['Peso_Calculado'] = plan + prod
            peso_total = df_metricas['Peso_Calculado'].sum() # Em KG
            
            if coluna_data != "Nenhuma" and coluna_data in df_metricas.columns:                
                # PESO SEM DATA
                df_sem_data = df_metricas[df_metricas[coluna_data].isna()].copy()
                peso_sem_data = df_sem_data['Peso_Calculado'].sum() # Em KG
                
                # PESO DA DATA ESPECÍFICA
                if data_especifica:
                    data_filtro_norm = pd.to_datetime(data_especifica).normalize()
                    
                    df_data_especifica_base = df_metricas[
                        df_metricas[coluna_data].dt.normalize() == data_filtro_norm
                    ].copy()
                    
                    peso_data_especifica = df_data_especifica_base['Peso_Calculado'].sum() # Em KG
            
            elif coluna_data != "Nenhuma":
                 st.warning(f"A coluna '{coluna_data}' não foi encontrada. As métricas de data não podem ser calculadas.")

        except KeyError:
            st.warning("Colunas 'PLANEJAMENTO' ou 'PRODUCAO' não encontradas (provavelmente foram excluídas). Não foi possível calcular o peso total.")
        except Exception as e:
            st.error(f"Erro ao calcular o peso: {e}")
            
        def formatar_br(numero):
            padrao_us = f"{numero:,.2f}"
            padrao_br = padrao_us.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
            return f"{padrao_br} kg"
        
        # --- INÍCIO DA ALTERAÇÃO (Função para Metros) ---
        def formatar_m(numero):
            padrao_us = f"{numero:,.2f}"
            padrao_br = padrao_us.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
            return f"{padrao_br} m"
        # --- FIM DA ALTERAÇÃO ---

        # --- INÍCIO DA ALTERAÇÃO (Lógica de Conversão) ---
        label_unidade_principal = "Peso"
        formatador_func = formatar_br
        val_data = peso_data_especifica
        val_sem_data = peso_sem_data
        val_total = peso_total

        if NOME_GRUPO_GALVANIZADO in grupos_selecionados:
            if fator_kg_m <= 0:
                st.warning("Fator de conversão (kg/m) deve ser maior que zero para calcular a metragem.")
            else:
                label_unidade_principal = "Metragem"
                formatador_func = formatar_m
                val_data = peso_data_especifica / fator_kg_m
                val_sem_data = peso_sem_data / fator_kg_m
                val_total = peso_total / fator_kg_m
        
        st.subheader(f"Resumo ({label_unidade_principal})")
        # --- FIM DA ALTERAÇÃO ---

        col_m1, col_m2, col_m3 = st.columns(3)
        
        # --- INÍCIO DA ALTERAÇÃO (Padronização dos 3 cards) ---
        with col_m1:
            # Label dinâmico (Peso ou Metragem)
            label_metrica_data = f"{label_unidade_principal} da Data ({data_especifica.strftime('%d/%m/%Y')})" if data_especifica else f"{label_unidade_principal} da Data (Nenhuma)"
            
            if coluna_data == "Nenhuma":
                # Convertido para st.markdown
                st.markdown(f"""
                <div style="line-height: 1.25;">
                    <div style="font-size: 0.875rem; color: inherit; opacity: 0.7; padding-bottom: 4px;">{label_metrica_data}</div>
                    <div style="font-size: 1.75rem; font-weight: 600; color: inherit; line-height: 1;">Selecione uma coluna de data</div>
                </div>
                """, unsafe_allow_html=True)
            
            elif data_especifica: # Só aplica a lógica se uma data foi selecionada
                # Pega os nomes dos grupos para verificação
                GRUPO_FQ6 = "PERFIL FQ 6"
                GRUPO_ROLETADO = "PERFIL FQ ROLETADO"
                GRUPO_FQ3 = "PERFIL FQ 3"
                GRUPO_FF = "PERFIL FF"
                
                # Converte a lista de seleção em um conjunto (set) para facilitar a comparação
                set_grupos_selecionados = set(grupos_selecionados)
                
                # Define os conjuntos de condições
                cond_1_grupos = {GRUPO_FQ6, GRUPO_ROLETADO}
                cond_2_grupos = {GRUPO_FQ3, GRUPO_FF}
                
                # Define a cor padrão e a mensagem de aviso
                color_style = "color: inherit;" # Cor padrão para o valor
                warning_message = "" # Sem aviso por padrão
                
                # CONDIÇÃO 1: (PERFIL FQ 6 e PERFIL FQ ROLETADO)
                # O CHECK É SEMPRE FEITO NO PESO (KG)
                if set_grupos_selecionados == cond_1_grupos:
                    if peso_data_especifica > 45000: # 45 toneladas
                        # --- INÍCIO DA ALTERAÇÃO (Pintar o valor) ---
                        color_style = "color: #FF4B4B;" # Muda a cor do valor para vermelho
                        # --- FIM DA ALTERAÇÃO ---
                        warning_message = '<div style="color: #FF4B4B; font-size: 0.875rem; font-weight: 600; padding-top: 4px;">Volume excede capacidade</div>'
                
                # CONDIÇÃO 2: (PERFIL FQ 3 e PERFIL FF)
                # O CHECK É SEMPRE FEITO NO PESO (KG)
                elif set_grupos_selecionados == cond_2_grupos:
                    if peso_data_especifica > 1800: # 1800 kg
                        # --- INÍCIO DA ALTERAÇÃO (Pintar o valor) ---
                        color_style = "color: #FF4B4B;" # Muda a cor do valor para vermelho
                        # --- FIM DA ALTERAÇÃO ---
                        warning_message = '<div style="color: #FF4B4B; font-size: 0.875rem; font-weight: 600; padding-top: 4px;">Volume excede capacidade</div>'

                # Formata o valor (KG ou M)
                valor_formatado = formatador_func(val_data)
                
                # Monta o HTML para o "pseudo-metric" (Este já estava correto)
                st.markdown(f"""
                <div style="line-height: 1.25;">
                    <div style="font-size: 0.875rem; color: inherit; opacity: 0.7; padding-bottom: 4px;">
                        {label_metrica_data}
                    </div>
                    <div style="font-size: 1.75rem; font-weight: 600; {color_style}; line-height: 1;">
                        {valor_formatado}
                    </div>
                    {warning_message}
                </div>
                """, unsafe_allow_html=True)
            
            else: # Caso onde coluna_data != "Nenhuma" mas data_especifica é None
                # Convertido para st.markdown
                valor_formatado = formatador_func(val_data) # Mostra 0.00 kg ou 0.00 m
                st.markdown(f"""
                <div style="line-height: 1.25;">
                    <div style="font-size: 0.875rem; color: inherit; opacity: 0.7; padding-bottom: 4px;">{label_metrica_data}</div>
                    <div style="font-size: 1.75rem; font-weight: 600; color: inherit; line-height: 1;">{valor_formatado}</div>
                </div>
                """, unsafe_allow_html=True)

        with col_m2:
            # Convertido para st.markdown
            label_metrica_sem_data = f"{label_unidade_principal} (Itens Sem Data)"
            valor_formatado_sem_data = formatador_func(val_sem_data)
            st.markdown(f"""
            <div style="line-height: 1.25;">
                <div style="font-size: 0.875rem; color: inherit; opacity: 0.7; padding-bottom: 4px;">{label_metrica_sem_data}</div>
                <div style="font-size: 1.75rem; font-weight: 600; color: inherit; line-height: 1;">{valor_formatado_sem_data}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m3:
            # Convertido para st.markdown
            label_metrica_total = f"{label_unidade_principal} Total (Filtros Atuais)"
            valor_formatado_total = formatador_func(val_total)
            st.markdown(f"""
            <div style="line-height: 1.25;">
                <div style="font-size: 0.875rem; color: inherit; opacity: 0.7; padding-bottom: 4px;">{label_metrica_total}</div>
                <div style="font-size: 1.75rem; font-weight: 600; color: inherit; line-height: 1;">{valor_formatado_total}</div>
            </div>
            """, unsafe_allow_html=True)
        # --- FIM DA ALTERAÇÃO ---
            
        # --- FIM DA ALTERAÇÃO 5 ---


        st.header('Visualização da Planilha (Itens Filtrados)')
        
        # --- INÍCIO DA ALTERAÇÃO 8: Formatação da Data na Tabela Principal ---
        column_config = {} # Inicia config vazia

        # ALTERAÇÃO 11.2: Adiciona config para 'Qtde Mat. Prima [KG]' como texto
        if 'Qtde Mat. Prima [KG]' in df_filtered.columns:
             column_config['Qtde Mat. Prima [KG]'] = st.column_config.TextColumn(
                 label='Qtde Mat. Prima [KG]'
             )
        
        # --- INÍCIO DA CORREÇÃO (Nome da coluna com ponto) ---
        # ALTERAÇÃO 14.3: Adiciona formatação de data para 'Dt. Término Prod.'
        if 'Dt. Término Prod.' in df_filtered.columns:
            column_config['Dt. Término Prod.'] = st.column_config.DatetimeColumn(
                label='Dt. Término Prod.',
                format="DD/MM/YYYY"
            )
        # --- FIM DA CORREÇÃO ---

        # --- LÓGICA DE FILTRO E EXIBIÇÃO DA TABELA PRINCIPAL ---
        hoje_dt = pd.to_datetime(datetime.date.today()).normalize()
        
        # 2. Cria uma cópia do DF filtrado para não afetar os cálculos de métrica
        df_para_exibir = df_filtered.copy()

        # --- INÍCIO DA ALTERAÇÃO (Req: Filtrar tabela pela data) ---
        
        # CONDIÇÃO 1: Prioridade para o checkbox "Filtrar hoje"
        if filtrar_hoje and coluna_data != "Nenhuma" and coluna_data in df_para_exibir.columns:
            st.info(f"Exibindo apenas registros de **hoje** ({hoje_dt.strftime('%d/%m/%Y')})")
            df_para_exibir = df_para_exibir[df_para_exibir[coluna_data].dt.normalize() == hoje_dt]
        
        # CONDIÇÃO 2: Se "hoje" não estiver marcado, filtra pela "data_especifica" (se ela foi selecionada)
        elif data_especifica and coluna_data != "Nenhuma" and coluna_data in df_para_exibir.columns:
            data_filtro_norm = pd.to_datetime(data_especifica).normalize()
            st.info(f"Exibindo apenas registros da data selecionada: **{data_filtro_norm.strftime('%d/%m/%Y')}**")
            df_para_exibir = df_para_exibir[
                df_para_exibir[coluna_data].dt.normalize() == data_filtro_norm
            ]
        # CONDIÇÃO 3: Se nenhum filtro de data acima estiver ativo, df_para_exibir continua como está (completo ou filtrado por Grupo/Descrição)
        
        # --- FIM DA ALTERAÇÃO ---


        # Ordena e exibe o dataframe
        if coluna_data != "Nenhuma" and coluna_data in df_para_exibir.columns:
            # Adiciona a formatação de data DD/MM/YYYY ao config
            column_config[coluna_data] = st.column_config.DatetimeColumn(
                label=coluna_data, # Usa o nome original da coluna como rótulo
                format="DD/MM/YYYY" # Formato brasileiro
            )

            # Ordena a tabela principal (filtrada)
            df_ordenado = df_para_exibir.sort_values(by=coluna_data, na_position='first')
            
            # Aplica o column_config
            st.dataframe(df_ordenado, column_config=column_config)
        else:
            # Aplica o column_config
            st.dataframe(df_para_exibir, column_config=column_config)
        # --- FIM DA ALTERAÇÃO 8 ---
            
        # --- INÍCIO DA ALTERAÇÃO (Verificação de Arquivos) ---
        st.divider()
        st.header("Verificação de Arquivos na Pasta")
        
        # --- INÍCIO DA ALTERAÇÃO (Link para o Drive) ---
        st.info("Para verificar os pedidos, você precisa de um script que lê sua pasta e gera o `lista_arquivos.txt`.")
        st.markdown("""
        **Como gerar o arquivo `lista_arquivos.txt`:**

        1.  Clique no link/botão abaixo para **baixar o script gerador (`.exe` ou `.py`)** do seu Google Drive.
        2.  Execute o script que você baixou (dando dois cliques).
        3.  Siga as instruções na tela (selecionar pasta de entrada e saída).
        4.  Carregue o `lista_arquivos.txt` gerado abaixo.
        """)
        
        st.markdown("---")
        st.subheader("Baixar Script Gerador de Lista (GUI)")
        
        # !!! IMPORTANTE !!!
        # Substitua o link abaixo pelo link de compartilhamento real do seu Google Drive
        link_do_drive = "https://drive.google.com/drive/u/0/folders/1055I42M4NSuEu_b_lBUTvcXVEJowPfSS" 
        
        st.markdown(f"""
        <a href="{link_do_drive}" target="_blank" style="
            display: inline-block;
            padding: 0.75rem 1.25rem;
            background-color: #0068c9; /* Cor azul bonita */
            color: white;
            text-decoration: none;
            font-weight: 600;
            border-radius: 0.5rem;
            text-align: center;
        ">
            Clique aqui para baixar o Script Gerador (do Drive)
        </a>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        # --- FIM DA ALTERAÇÃO ---
        
        uploaded_file_list = st.file_uploader("2. Carregar lista_arquivos.txt", type=['txt'])
        
        file_numbers_set = set()
        
        if uploaded_file_list is not None:
            try:
                # Ler o Txt
                file_names = uploaded_file_list.getvalue().decode("utf-8").splitlines()
                
                # --- INÍCIO DA ALTERAÇÃO (Regex corrigido) ---
                # Extrair os números dos arquivos. Ex: "460693_Div.pdf" -> "460693"
                # Este regex procura por uma sequência de 6 ou mais dígitos
                pattern = re.compile(r'(\d{6,})') 
                
                for name in file_names:
                    match = pattern.search(name)
                    if match:
                        # Adiciona o primeiro grupo de 6+ dígitos encontrado
                        file_numbers_set.add(match.group(1)) 
                # --- FIM DA ALTERAÇÃO ---
                        
                st.success(f"{len(file_numbers_set)} números de pedidos únicos extraídos da lista de arquivos.")
            except Exception as e:
                st.error(f"Erro ao ler a lista de arquivos: {e}")
        # --- FIM DA ALTERAÇÃO ---
            
        # --- INÍCIO DA ALTERAção (Separar em duas tabelas) ---
        
        st.divider() 
        # Título atualizado
        st.header("Análise: Pedidos Pendentes (Emitidos antes de hoje E sem Dt. Término Prod.)")

        if coluna_data == "Nenhuma":
            st.info("Para rodar esta análise, selecione a 'coluna de data (Emissão)' principal no topo da página.")
        
        # --- INÍCIO DA ALTERAÇÃO (Verificar colunas DEPOIS da exclusão) ---
        elif 'Usuário Emitiu' not in df_display.columns:
            st.error("Erro na análise: A coluna 'Usuário Emitiu' não foi encontrada (provavelmente foi excluída).")
        
        elif 'Dt. Término Prod.' not in df_display.columns:
            st.error("Erro na análise: A coluna 'Dt. Término Prod.' é necessária, mas não foi encontrada (provavelmente foi excluída).")
            
        elif 'Pedido' not in df_display.columns:
            st.error("Erro na análise: A coluna 'Pedido' é necessária, mas não foi encontrada (provavelmente foi excluída).")
        # --- FIM DA ALTERAÇÃO ---
            
        else:
            try:
                hoje_dt = pd.to_datetime(datetime.date.today()).normalize() 

                df_analise = df_display.copy()
                # Coluna de EMISSÃO (selecionada no selectbox)
                df_analise[coluna_data] = pd.to_datetime(df_analise[coluna_data], errors='coerce') 
                
                # --- INÍCIO DA CORREÇÃO (Nome da coluna com ponto) ---
                # Coluna de TÉRMINO (para filtro .isna())
                # Adicionamos 'errors='coerce'' aqui também por segurança
                df_analise['Dt. Término Prod.'] = pd.to_datetime(df_analise['Dt. Término Prod.'], errors='coerce')

                # CONDIÇÃO 1: Data de emissão anterior a hoje
                condicao_emissao_antiga = (df_analise[coluna_data].dt.normalize() < hoje_dt)
                # CONDIÇÃO 2: Data de término está vazia
                condicao_termino_nula = df_analise['Dt. Término Prod.'].isna()
                # --- FIM DA CORREÇÃO ---
                
                # Combinação das condições
                condicao_final = condicao_emissao_antiga & condicao_termino_nula
                
                pedidos_pendentes = df_analise[condicao_final].copy() # Adicionado .copy()
                
                # --- INÍCIO DA NOVA VERIFICAÇÃO DE PASTA ---
                if uploaded_file_list:
                    def check_file_status(pedido_num):
                        # Converte o número (que pode ser float 123456.0) para string "123456"
                        pedido_str = str(pedido_num).split('.')[0] 
                        
                        if pedido_str in file_numbers_set:
                            return "Pedido na Pasta"
                        else:
                            return "Pedido Ausente"
                    
                    # --- INÍCIO DA ALTERAÇÃO (Usar "Pedido") ---
                    pedidos_pendentes["Status Pasta"] = pedidos_pendentes["Pedido"].apply(check_file_status)
                    # --- FIM DA ALTERAÇÃO ---
                else:
                    pedidos_pendentes["Status Pasta"] = "Carregue a lista"
                # --- FIM DA NOVA VERIFICAÇÃO DE PASTA ---
                
                
                # CONDIÇÃO 3: Excluir cliente "NOROACO" (Mantida)
                cliente_a_excluir = "NOROACO COMERCIO DE FERRO E ACO LTDA"
                if 'Cliente' in pedidos_pendentes.columns:
                    pedidos_pendentes = pedidos_pendentes[
                        pedidos_pendentes['Cliente'] != cliente_a_excluir
                    ]
                else:
                    # Não é um erro, apenas informa se a coluna não existir (pois pode ter sido excluída)
                    if 'Cliente' not in df.columns: # Verifica no 'df' original
                         st.info("Coluna 'Cliente' não encontrada. Não foi possível aplicar o filtro de exclusão para 'NOROACO'.")


                # --- INÍCIO DA ALTERAÇÃO (Separar em duas tabelas) ---
                
                # 1. Separar os DataFrames
                pedidos_ausentes = pedidos_pendentes[pedidos_pendentes["Status Pasta"] == "Pedido Ausente"]
                pedidos_na_pasta = pedidos_pendentes[pedidos_pendentes["Status Pasta"] == "Pedido na Pasta"]
                
                # --- INÍCIO DA CORREÇÃO (Nome da coluna com ponto) ---
                # 2. Configurações da Tabela (usadas por ambas)
                # --- INÍCIO DA ALTERAÇÃO (Usar colunas que sobraram) ---
                colunas_disponiveis_analise = df_display.columns.tolist()
                
                colunas_alerta = ['Pedido', 'Status Pasta', 'Usuário Emitiu', coluna_data, 'Dt. Término Prod.']
                # Adiciona outras colunas dinamicamente se elas não foram excluídas
                if 'Cliente' in colunas_disponiveis_analise:
                    colunas_alerta.append('Cliente')
                if 'Descrição do Produto' in colunas_disponiveis_analise:
                    colunas_alerta.append('Descrição do Produto')
                
                # Garante que só vamos mostrar colunas que realmente existem
                colunas_alerta = [col for col in colunas_alerta if col in colunas_disponiveis_analise or col == 'Status Pasta']
                # --- FIM DA ALTERAÇÃO ---

                
                config_tabela_alerta = {
                    coluna_data: st.column_config.DatetimeColumn(
                        label=coluna_data, # Label dinâmico da data de emissão
                        format="DD/MM/YYYY HH:mm"
                    ),
                    'Dt. Término Prod.': st.column_config.DatetimeColumn( # CORRIGIDO: Adicionado ponto
                        label='Dt. Término Prod.', # CORRIGIDO: Adicionado ponto
                        format="DD/MM/YYYY"
                    )
                }
                # --- FIM DA CORREÇÃO ---
                
                # 3. Exibir Tabela de PEDIDOS AUSENTES (A MAIS IMPORTANTE)
                st.subheader("Pedidos Ausentes na Pasta")
                
                if pedidos_ausentes.empty:
                    if uploaded_file_list: # Só mostra sucesso se a lista foi carregada
                        st.success(f"Tudo ok! Nenhum pedido pendente **ausente da pasta** encontrado (emitido antes de {hoje_dt.strftime('%d/%m/%Y')} E sem Dt. Término Prod.).")
                    else:
                        st.info("Carregue o arquivo 'lista_arquivos.txt' para verificar os pedidos ausentes.")
                else:
                    total_pedidos_ausentes = len(pedidos_ausentes)
                    st.warning(f"Atenção: {total_pedidos_ausentes} pedido(s) pendentes **ausentes da pasta** encontrados.")
                    
                    pedidos_ausentes_ordenados = pedidos_ausentes.sort_values(by=coluna_data, na_position='first')
                    st.dataframe(pedidos_ausentes_ordenados[colunas_alerta], column_config=config_tabela_alerta)
                
                
                # 4. Exibir Tabela de PEDIDOS NA PASTA
                st.subheader("Pedidos Pendentes (mas já na pasta)")
                
                if pedidos_na_pasta.empty:
                    if uploaded_file_list: # Só mostra se a lista foi carregada
                        st.info("Nenhum pedido pendente (com arquivo já na pasta) foi encontrado.")
                else:
                    total_pedidos_na_pasta = len(pedidos_na_pasta)
                    st.info(f"{total_pedidos_na_pasta} pedido(s) pendentes foram encontrados, mas seus arquivos já estão na pasta.")
                    
                    pedidos_na_pasta_ordenados = pedidos_na_pasta.sort_values(by=coluna_data, na_position='first')
                    st.dataframe(pedidos_na_pasta_ordenados[colunas_alerta], column_config=config_tabela_alerta)
                
                # --- FIM DA ALTERAÇÃO ---


            except Exception as e:
                st.error(f"Ocorreu um erro ao analisar os pedidos pendentes: {e}")
        # --- FIM DA ALTERAÇÃO 10 ---

    except Exception as e:
        st.error(f"Ocorreu um erro ao ler o arquivo: {e}")
