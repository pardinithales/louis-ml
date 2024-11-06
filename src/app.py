import streamlit as st
import requests
import json
import logging
import ast
import os
from pathlib import Path
from database.db_connection import load_symptoms, load_syndromes
from dotenv import load_dotenv
import openai

# Carregar variáveis de ambiente do arquivo .env
load_dir = Path(__file__).resolve().parent.parent
load_dotenv(load_dir / '.env')

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Configura��es do Streamlit para Vercel
os.environ["STREAMLIT_SERVER_PORT"] = "8080"
os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"


# Configurar a chave de API da OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logging.error("OPENAI_API_KEY n�o encontrada nas vari�veis de ambiente")

# URL da API do Ollama
# OLLAMA_API_URL = "http://localhost:11434/api/generate"

def get_llm_symptoms(texto_caso, lista_sintomas):
    logging.info("Enviando texto para o OpenAI GPT-4 para extra��o de sintomas")
    try:
        # Formatar a lista de sintomas para exibi��o no prompt
        formatted_symptom_list = '\n'.join(lista_sintomas)

        # Construir o prompt conforme seu exemplo
        system_prompt = f"""Extract the symptoms present in the following clinical case (that will be inputted in any language). Use only the symptoms from the provided list and do not include symptoms that are not on the list.

Available symptoms list:
{formatted_symptom_list}

Respond with the identified symptoms separated by commas, NO OTHER ADDITIONAL TEXT! MUST BE IN ENGLISH."""

        user_prompt = f"""Clinical case:
{texto_caso}
"""

        # Chamada � API da OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        llm_output = response.choices[0].message.content.strip()

        # Processar a sa�da para extrair os sintomas
        extracted_symptoms = [s.strip() for s in llm_output.split(',')]

        # Normalizar os sintomas para compara��o
        lista_sintomas_normalized = [s.lower().strip() for s in lista_sintomas]
        extracted_symptoms_normalized = [s.lower().strip() for s in extracted_symptoms]

        # Filtrar sintomas que est�o na lista
        matched_symptoms = []
        for symptom in extracted_symptoms_normalized:
            if symptom in lista_sintomas_normalized:
                # Obter a forma original do sintoma
                index = lista_sintomas_normalized.index(symptom)
                matched_symptoms.append(lista_sintomas[index])

        # Remover duplicatas
        matched_symptoms = list(set(matched_symptoms))

        return matched_symptoms

    except Exception as e:
        logging.error(f"Erro ao conectar com a OpenAI GPT-4: {e}")
        return []

def get_llm_response(prompt):
    logging.info("Enviando prompt para o LLaMA via Ollama para gerar resumo comparativo")
    try:
        # Verificar se o resultado para este prompt j� est� em cache
        cache_key = f"llm_response_{hash(prompt)}"
        if cache_key in st.session_state:
            return st.session_state[cache_key]

        # Chamada � API do Ollama
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "temperature": 0.7,  # Temperatura padr�o para gera��o de texto
                "stream": False
            }
        )
        response.raise_for_status()
        llm_response = response.json().get('response', '').strip()

        # Cachear o resultado no session_state
        st.session_state[cache_key] = llm_response
        return llm_response

    except Exception as e:
        logging.error(f"Erro ao conectar com o Ollama LLaMA: {e}")
        return None

def analyze_symptoms_progressive(symptoms_list, syndromes):
    # Cachear o resultado desta fun��o
    cache_key = f"analyze_{','.join(symptoms_list)}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    logging.info(f"Analisando lista de sintomas: {symptoms_list}")

    # Normalizar sintomas da lista atual
    symptoms_list_lower = [s.strip('"\' ').lower() for s in symptoms_list]

    matched_syndromes = []
    for syndrome in syndromes:
        syndrome_signs_lower = [s.strip('"\' ').lower() for s in syndrome['signs']]
        matches = sum(1 for symptom in symptoms_list_lower if symptom in syndrome_signs_lower)
        total_signs = len(syndrome_signs_lower)
        if matches > 0:
            match_score = matches / total_signs
            matched_syndromes.append({
                'syndrome': syndrome,
                'score': match_score,
                'matched_count': matches
            })

    matched_syndromes.sort(key=lambda x: x['score'], reverse=True)
    # Cachear o resultado
    st.session_state[cache_key] = matched_syndromes[:4]
    return matched_syndromes[:4]

def normalize_symptoms(symptoms):
    """Normaliza a lista de sintomas"""
    normalized = set()
    for symptom in symptoms:
        if isinstance(symptom, str):
            # Remove aspas, colchetes e espa�os extras
            clean_symptom = symptom.strip('[]"\'').strip()
            # Remove aspas internas
            clean_symptom = clean_symptom.replace('"', '').replace("'", "")
            # Divide se houver m�ltiplos sintomas
            individual_symptoms = [s.strip() for s in clean_symptom.split(',')]
            normalized.update(individual_symptoms)
        else:
            normalized.add(symptom)
    return list(normalized)  # Remove duplicatas

@st.cache_data(show_spinner=False)
def get_symptoms():
    return normalize_symptoms(load_symptoms())

@st.cache_data(show_spinner=False)
def get_syndromes():
    return load_syndromes()

def main():
    st.set_page_config(layout="wide")  # Melhor utiliza��o do espa�o na tela
    st.title("Louis - Sistema de An�lise Neurol�gica")

    symptoms = get_symptoms()
    syndromes = get_syndromes()

    if not symptoms or not syndromes:
        st.error("Erro ao carregar banco de dados")
        return

    st.sidebar.success(f"Banco conectado - {len(syndromes)} s�ndromes")

    # Inicializar lista de sintomas no estado da sess�o
    if 'symptoms_list' not in st.session_state:
        st.session_state.symptoms_list = []

    # Layout em duas colunas
    col_main, col_info = st.columns([2, 1])

    with col_main:
        # Campo de texto para o caso cl�nico
        st.subheader("Digite o caso cl�nico do paciente:")
        clinical_case = st.text_area("Insira aqui o caso cl�nico do paciente.", key="clinical_case_input")
        if st.button("Extrair Sintomas"):
            if clinical_case:
                # Usar o OpenAI GPT-4 para extrair sintomas
                with st.spinner("Extraindo sintomas..."):
                    extracted_symptoms = get_llm_symptoms(clinical_case, symptoms)
                if extracted_symptoms:
                    # Adicionar sintomas extra�dos � lista de sintomas selecionados
                    for symptom in extracted_symptoms:
                        if symptom not in st.session_state.symptoms_list:
                            if len(st.session_state.symptoms_list) < 6:
                                st.session_state.symptoms_list.append(symptom)
                            else:
                                st.warning("Voc� pode adicionar no m�ximo 6 sintomas.")
                                break
                    st.success(f"Sintomas extra�dos: {', '.join(extracted_symptoms)}")
                else:
                    st.warning("Nenhum sintoma foi identificado no texto fornecido.")
            else:
                st.warning("Por favor, insira o caso cl�nico antes de extrair os sintomas.")

        # Multiselect para adicionar sintomas
        st.subheader("Ou selecione os sintomas manualmente:")
        cleaned_symptoms = [symptom.strip('[]"\'') for symptom in symptoms]
        selected_symptoms = st.multiselect(
            "Selecione os sintomas:",
            options=cleaned_symptoms,
            default=st.session_state.symptoms_list,
            key="symptoms_multiselect",
            help="Digite para filtrar os sintomas dispon�veis"
        )
        # Atualizar lista de sintomas com sele��o do multiselect
        if selected_symptoms != st.session_state.symptoms_list:
            st.session_state.symptoms_list = selected_symptoms[:6]  # Limita a 6 sintomas

        # Bot�o para limpar todos os sintomas
        if st.button("Limpar Todos"):
            st.session_state.symptoms_list = []
            st.experimental_rerun()

        # Mostrar sintomas atuais
        if st.session_state.symptoms_list:
            st.write("**Sintomas atuais:**", ", ".join(st.session_state.symptoms_list))

            # An�lise progressiva
            with st.spinner("Analisando s�ndromes..."):
                matched_syndromes = analyze_symptoms_progressive(
                    st.session_state.symptoms_list,
                    syndromes
                )

            # Dividir em duas colunas dentro da coluna principal
            col1, col2 = st.columns([1, 1])

            with col1:
                # Exibir resultados na primeira sub-coluna
                st.subheader("S�ndromes Prov�veis")
                for match in matched_syndromes:
                    syndrome = match['syndrome']
                    expander_key = f"expander_{syndrome['syndrome_name']}"
                    with st.expander(
                        f"{syndrome['syndrome_name']} ({match['matched_count']} sintomas em comum)",
                        expanded=False
                    ):
                        signs = syndrome['signs']
                        # Destacar sintomas que deram match em verde e negrito
                        signs_lower = [s.lower() for s in signs]
                        symptoms_list_lower = [s.lower() for s in st.session_state.symptoms_list]
                        highlighted_signs = [
                            f"<span style='color:green; font-weight:bold;'>{sign}</span>" if sign.lower() in symptoms_list_lower
                            else sign
                            for sign in signs
                        ]
                        # Processar 'locals' e 'arteries' para remover colchetes e aspas
                        locals_raw = syndrome['locals']
                        arteries_raw = syndrome['arteries']

                        # Converter strings que representam listas em listas reais
                        try:
                            locals_list = ast.literal_eval(locals_raw) if isinstance(locals_raw, str) else locals_raw
                        except:
                            locals_list = [locals_raw]

                        try:
                            arteries_list = ast.literal_eval(arteries_raw) if isinstance(arteries_raw, str) else arteries_raw
                        except:
                            arteries_list = [arteries_raw]

                        # Limpar e juntar
                        locals_clean = ', '.join([item.strip('[]"\'') for item in locals_list])
                        arteries_clean = ', '.join([item.strip('[]"\'') for item in arteries_list])

                        # Aumentar tamanho da fonte e exibir informa��es formatadas
                        st.markdown(
                            f"<p style='font-size:16px;'><strong>Sintomas:</strong> {', '.join(highlighted_signs)}</p>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"<p style='font-size:16px;'><strong>Localiza��o:</strong> {locals_clean}</p>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"<p style='font-size:16px;'><strong>Art�rias:</strong> {arteries_clean}</p>",
                            unsafe_allow_html=True
                        )

            with col2:
                # Gerar resumo comparativo das tr�s primeiras s�ndromes usando LLaMA
                st.subheader("Resumo Comparativo")
                if matched_syndromes:
                    # Preparar o prompt para o modelo de IA
                    cache_key = f"summary_{'_'.join([m['syndrome']['syndrome_name'] for m in matched_syndromes[:3]])}"
                    if cache_key in st.session_state:
                        ai_response = st.session_state[cache_key]
                    else:
                        syndrome_info = []
                        for match in matched_syndromes[:3]:
                            syndrome = match['syndrome']
                            syndrome_name = syndrome['syndrome_name']
                            locals_raw = syndrome['locals']
                            signs = syndrome['signs']
                            arteries_raw = syndrome['arteries']

                            # Limpar dados
                            try:
                                locals_list = ast.literal_eval(locals_raw) if isinstance(locals_raw, str) else locals_raw
                            except:
                                locals_list = [locals_raw]
                            locals_clean = ', '.join([item.strip('[]"\'') for item in locals_list])

                            try:
                                arteries_list = ast.literal_eval(arteries_raw) if isinstance(arteries_raw, str) else arteries_raw
                            except:
                                arteries_list = [arteries_raw]
                            arteries_clean = ', '.join([item.strip('[]"\'') for item in arteries_list])

                            signs_clean = ', '.join(signs)

                            syndrome_info.append(f"""S�ndrome: {syndrome_name}
Localiza��o: {locals_clean}
Sintomas principais: {signs_clean}
Art�ria afetada: {arteries_clean}""")

                        # Construir o prompt
                        prompt = f"""Como um neurologista experiente, compare e contraste as seguintes s�ndromes neurol�gicas, destacando suas semelhan�as e diferen�as cl�nicas e anat�micas em at� 15 linhas:

{"\n\n".join(syndrome_info)}

Use linguagem t�cnica e termos neurol�gicos avan�ados."""

                        # Obter a resposta do modelo de IA
                        with st.spinner("Gerando resumo..."):
                            ai_response = get_llm_response(prompt)
                        if ai_response:
                            st.session_state[cache_key] = ai_response
                        else:
                            st.error("Erro ao gerar resumo com IA.")

                    if ai_response:
                        st.markdown(f"<p style='font-size:14px;'>{ai_response}</p>", unsafe_allow_html=True)
                else:
                    st.write("Nenhuma s�ndrome encontrada para gerar resumo.")
        else:
            st.write("Nenhum sintoma adicionado.")

    with col_info:
        st.subheader("Consulta de S�ndromes")
        # Dropdown para selecionar uma s�ndrome para mais informa��es
        syndrome_names = [syndrome['syndrome_name'] for syndrome in syndromes]
        selected_syndrome = st.selectbox("Selecione uma s�ndrome para mais informa��es:", [""] + syndrome_names, key="syndrome_selectbox")

        if selected_syndrome:
            # Encontrar a s�ndrome selecionada
            syndrome = next((s for s in syndromes if s['syndrome_name'] == selected_syndrome), None)
            if syndrome:
                with st.expander(f"Detalhes da S�ndrome: {syndrome['syndrome_name']}", expanded=True):
                    # Processar e exibir informa��es de forma sint�tica
                    signs = syndrome['signs']
                    locals_raw = syndrome['locals']
                    arteries_raw = syndrome['arteries']

                    try:
                        locals_list = ast.literal_eval(locals_raw) if isinstance(locals_raw, str) else locals_raw
                    except:
                        locals_list = [locals_raw]
                    locals_clean = ', '.join([item.strip('[]"\'') for item in locals_list])

                    try:
                        arteries_list = ast.literal_eval(arteries_raw) if isinstance(arteries_raw, str) else arteries_raw
                    except:
                        arteries_list = [arteries_raw]
                    arteries_clean = ', '.join([item.strip('[]"\'') for item in arteries_list])

                    st.markdown(f"**Localiza��o:** {locals_clean}")
                    st.markdown(f"**Art�rias Afetadas:** {arteries_clean}")
                    st.markdown(f"**Sintomas Principais:** {', '.join(signs)}")
            else:
                st.error("S�ndrome n�o encontrada.")

    # Quadro informativo adicional: Lista completa de s�ndromes
    st.sidebar.header("Consulta R�pida de S�ndromes")
    with st.sidebar.expander("Ver todas as s�ndromes"):
        for syndrome in syndromes:
            st.markdown(f"### {syndrome['syndrome_name']}")
            try:
                locals_list = ast.literal_eval(syndrome['locals']) if isinstance(syndrome['locals'], str) else syndrome['locals']
            except:
                locals_list = [syndrome['locals']]
            locals_clean = ', '.join([item.strip('[]"\'') for item in locals_list])

            try:
                arteries_list = ast.literal_eval(syndrome['arteries']) if isinstance(syndrome['arteries'], str) else syndrome['arteries']
            except:
                arteries_list = [syndrome['arteries']]
            arteries_clean = ', '.join([item.strip('[]"\'') for item in arteries_list])

            st.markdown(f"- **Localiza��o:** {locals_clean}")
            st.markdown(f"- **Art�rias Afetadas:** {arteries_clean}")
            st.markdown(f"- **Sintomas Principais:** {', '.join(syndrome['signs'])}")
            st.markdown("---")

if __name__ == "__main__":
    main()

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
