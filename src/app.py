import streamlit as st
import requests
import json
import logging
import os
from pathlib import Path
from database.db_connection import load_symptoms, load_syndromes
import ast
from openai import OpenAI
from anthropic import Anthropic

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

# Deve ser o primeiro comando Streamlit
st.set_page_config(layout="wide", page_title="Louis - Sistema de Análise Neurológica")

def initialize_openai_client():
    try:
        if "OPENAI_API_KEY" not in st.secrets:
            st.error("OPENAI_API_KEY não encontrada nos secrets.")
            st.stop()
            
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        return client
    except Exception as e:
        st.error(f"Erro ao inicializar cliente OpenAI: {e}")
        st.stop()

# Inicializar o cliente Anthropic com sua API key
anthropic_client = Anthropic(
    api_key=st.secrets["CLAUDE_API_KEY"]
)


def test_openai_connection(client):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Test connection"}],
            max_tokens=5
        )
        if response:
            logging.info("Conexão com a OpenAI estabelecida com sucesso.")
            return True
    except Exception as e:
        logging.error(f"Erro ao conectar com a OpenAI: {e}")
        st.error("Não foi possível conectar com a OpenAI. Verifique sua chave da API.")
        return False

# Inicialização
client = initialize_openai_client()
if not test_openai_connection(client):
    st.stop()

# URL da API do Ollama
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def get_llm_symptoms(texto_caso, lista_sintomas, normalized_symptoms_list, normalized_to_original):
    logging.info("Enviando texto para o OpenAI GPT-4 para extração de sintomas")
    try:
        # Garante que a lista de sintomas esteja formatada corretamente
        formatted_symptom_list = '\n'.join(f"- {symptom}" for symptom in lista_sintomas)
        
        logging.info(f"Lista de sintomas enviada:\n{formatted_symptom_list}")  # Log para debug

        system_prompt = f"""You are a specialist in vascular neurological syndromes. 
        IMPORTANT: Extract ALL matching symptoms that appear in the case from the following list. 
        Output as comma-separated values.
        
        Available symptoms list:
        {formatted_symptom_list}
        
        RESPONSE FORMAT EXAMPLE:
        Hemiparesis / Hemiplegia, Oculomotor palsy (III), Ataxia
        
        RULES:
        1. Use ONLY symptoms EXACTLY as they appear in the provided list
        2. Output ALL matching symptoms, separated by commas
        3. NO additional text or explanations
        4. Maintain EXACT same formatting as in the list
        5. Do not modify or abbreviate the symptoms
        6. Include ALL symptoms that match, not just one"""

        user_prompt = f"""Extract ALL matching symptoms from this case:
        {texto_caso}"""

        logging.info(f"Sintomas enviados para análise: {texto_caso}")  # Log para debug

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,  # Reduzido para maior consistência
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        llm_output = response.choices[0].message.content.strip()
        logging.info(f"Resposta da OpenAI: {llm_output}")  # Log para debug

        extracted_symptoms = [s.strip() for s in llm_output.split(',')]
        logging.info(f"Sintomas extraídos: {extracted_symptoms}")  # Log para debug

        # Mantém o case original e a formatação exata
        matched_symptoms = []
        for symptom in extracted_symptoms:
            # Procura correspondência exata na lista original
            matching_original = next(
                (s for s in lista_sintomas if s.lower().strip() == symptom.lower().strip()),
                None
            )
            if matching_original:
                matched_symptoms.append(matching_original)

        matched_symptoms = list(dict.fromkeys(matched_symptoms))  # Remove duplicatas mantendo a ordem
        logging.info(f"Sintomas finais após matching: {matched_symptoms}")  # Log para debug

        return matched_symptoms

    except Exception as e:
        logging.error(f"Erro ao processar sintomas: {str(e)}")
        return []

@st.cache_data
def get_claude_response(prompt):
    logging.info("Enviando prompt para o Claude para gerar resumo comparativo")
    try:
        response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.6,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return response.content[0].text

    except Exception as e:
        logging.error(f"Erro ao conectar com o Claude: {str(e)}")
        return None

def analyze_symptoms_progressive(symptoms_list_lower, syndromes):
    cache_key = f"analyze_{','.join(symptoms_list_lower)}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    logging.info(f"Analisando lista de sintomas: {symptoms_list_lower}")

    matched_syndromes = []
    symptoms_set = set(symptoms_list_lower)

    for syndrome in syndromes:
        syndrome_signs_lower = syndrome['normalized_signs']
        syndrome_signs_set = set(syndrome_signs_lower)
        matches = len(symptoms_set & syndrome_signs_set)
        total_signs = len(syndrome_signs_set)
        if matches > 0:
            match_score = matches / total_signs
            matched_syndromes.append({
                'syndrome': syndrome,
                'score': match_score,
                'matched_count': matches
            })

    matched_syndromes.sort(key=lambda x: x['score'], reverse=True)
    st.session_state[cache_key] = matched_syndromes[:4]
    return matched_syndromes[:4]

def normalize_symptoms(symptoms):
    normalized = set()
    for symptom in symptoms:
        if isinstance(symptom, str):
            clean_symptom = symptom.strip('[]"\'').strip()
            clean_symptom = clean_symptom.replace('"', '').replace("'", "")
            individual_symptoms = [s.strip() for s in clean_symptom.split(',')]
            normalized.update(individual_symptoms)
        else:
            normalized.add(symptom)
    return list(normalized)

@st.cache_data
def get_symptoms():
    symptoms_list = normalize_symptoms(load_symptoms())
    normalized_symptoms_list = [s.lower().strip('[]"\' ') for s in symptoms_list]
    normalized_to_original = dict(zip(normalized_symptoms_list, symptoms_list))
    return symptoms_list, normalized_symptoms_list, normalized_to_original

@st.cache_data(show_spinner=False)
def get_syndromes():
    syndromes_raw = load_syndromes()
    for syndrome in syndromes_raw:
        syndrome_signs = syndrome['signs']
        syndrome['normalized_signs'] = [s.lower().strip('[]"\' ') for s in syndrome_signs]
    return syndromes_raw

@st.cache_data
def generate_summary(syndrome_info):
    if not syndrome_info:
        logging.error("Nenhuma informação de síndrome fornecida para gerar resumo")
        return None
        
    prompt = f"""Como um neurologista experiente, compare e contraste as seguintes síndromes neurológicas, destacando suas semelhanças e diferenças clínicas e anatômicas em até 15 linhas:

{"\n\n".join(syndrome_info)}

Use linguagem técnica e termos neurológicos avançados."""
    
    ai_response = get_claude_response(prompt)
    
    if ai_response:
        return ai_response
    else:
        return None

def main():

    st.title("Louis - Sistema de Análise Neurológica")

    symptoms_list, normalized_symptoms_list, normalized_to_original = get_symptoms()
    syndromes = get_syndromes()

    if not symptoms_list or not syndromes:
        st.error("Erro ao carregar banco de dados")
        return

    st.sidebar.success(f"Banco conectado - {len(syndromes)} síndromes")

    if 'symptoms_list' not in st.session_state:
        st.session_state.symptoms_list = []

    col_main, col_info = st.columns([2, 1])

    with col_main:
        st.subheader("Digite o caso clínico do paciente:")
        clinical_case = st.text_area("Insira aqui o caso clínico do paciente.", key="clinical_case_input")
        if st.button("Extrair Sintomas"):
            if clinical_case:
                with st.spinner("Extraindo sintomas..."):
                    extracted_symptoms = get_llm_symptoms(clinical_case, symptoms_list, normalized_symptoms_list, normalized_to_original)
                if extracted_symptoms:
                    for symptom in extracted_symptoms:
                        if symptom not in st.session_state.symptoms_list:
                            if len(st.session_state.symptoms_list) < 6:
                                st.session_state.symptoms_list.append(symptom)
                            else:
                                st.warning("Você pode adicionar no máximo 6 sintomas.")
                                break
                    st.success(f"Sintomas extraídos: {', '.join(extracted_symptoms)}")
                else:
                    st.warning("Nenhum sintoma foi identificado no texto fornecido.")
            else:
                st.warning("Por favor, insira o caso clínico antes de extrair os sintomas.")

        st.subheader("Ou selecione os sintomas manualmente:")
        cleaned_symptoms = [symptom.strip('[]"\'') for symptom in symptoms_list]
        selected_symptoms = st.multiselect(
            "Selecione os sintomas:",
            options=cleaned_symptoms,
            default=st.session_state.symptoms_list,
            key="symptoms_multiselect",
            help="Digite para filtrar os sintomas disponíveis"
        )
        if selected_symptoms != st.session_state.symptoms_list:
            st.session_state.symptoms_list = selected_symptoms[:6]

        if st.button("Limpar Todos"):
            st.session_state.symptoms_list = []
            st.experimental_rerun()

        if st.session_state.symptoms_list:
            st.write("**Sintomas atuais:**", ", ".join(st.session_state.symptoms_list))
            st.session_state.symptoms_list_lower = [s.lower().strip('[]"\' ') for s in st.session_state.symptoms_list]

            with st.spinner("Analisando síndromes..."):
                matched_syndromes = analyze_symptoms_progressive(
                    st.session_state.symptoms_list_lower,
                    syndromes
                )

            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("Síndromes Prováveis")
                for match in matched_syndromes:
                    syndrome = match['syndrome']
                    with st.expander(
                        f"{syndrome['syndrome_name']} ({match['matched_count']} sintomas em comum)",
                        expanded=False
                    ):
                        signs = syndrome['signs']
                        signs_lower = syndrome['normalized_signs']
                        symptoms_set = set(st.session_state.symptoms_list_lower)

                        highlighted_signs = [
                            f"<span style='color:green; font-weight:bold;'>{sign}</span>" if sign_lower in symptoms_set
                            else sign
                            for sign, sign_lower in zip(signs, signs_lower)
                        ]

                        locals_raw = syndrome['locals']
                        arteries_raw = syndrome['arteries']

                        try:
                            locals_list = ast.literal_eval(locals_raw) if isinstance(locals_raw, str) else locals_raw
                        except:
                            locals_list = [locals_raw]

                        try:
                            arteries_list = ast.literal_eval(arteries_raw) if isinstance(arteries_raw, str) else arteries_raw
                        except:
                            arteries_list = [arteries_raw]

                        locals_clean = ', '.join([item.strip('[]"\'') for item in locals_list])
                        arteries_clean = ', '.join([item.strip('[]"\'') for item in arteries_list])

                        st.markdown(
                            f"<p style='font-size:16px;'><strong>Sintomas:</strong> {', '.join(highlighted_signs)}</p>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"<p style='font-size:16px;'><strong>Localização:</strong> {locals_clean}</p>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"<p style='font-size:16px;'><strong>Artérias:</strong> {arteries_clean}</p>",
                            unsafe_allow_html=True
                        )

            with col2:
                st.subheader("Resumo Comparativo")
                if matched_syndromes:
                    syndrome_info = []
                    for match in matched_syndromes[:3]:
                        syndrome = match['syndrome']
                        syndrome_name = syndrome['syndrome_name']
                        locals_raw = syndrome['locals']
                        signs = syndrome['signs']
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

                        signs_clean = ', '.join(signs)

                        syndrome_info.append(f"""Síndrome: {syndrome_name}
Localização: {locals_clean}
Sintomas principais: {signs_clean}
Artéria afetada: {arteries_clean}""")

                    with st.spinner("Gerando resumo..."):
                        ai_response = generate_summary(syndrome_info)
                    if ai_response:
                        st.markdown(f"<p style='font-size:14px;'>{ai_response}</p>", unsafe_allow_html=True)
                    else:
                        st.error("Erro ao gerar resumo com IA.")
                else:
                    st.write("Nenhuma síndrome encontrada para gerar resumo.")
        else:
            st.write("Nenhum sintoma adicionado.")

    with col_info:
        st.subheader("Consulta de Síndromes")
        syndrome_names = [syndrome['syndrome_name'] for syndrome in syndromes]
        selected_syndrome = st.selectbox("Selecione uma síndrome para mais informações:", [""] + syndrome_names, key="syndrome_selectbox")

        if selected_syndrome:
            syndrome = next((s for s in syndromes if s['syndrome_name'] == selected_syndrome), None)
            if syndrome:
                with st.expander(f"Detalhes da Síndrome: {syndrome['syndrome_name']}", expanded=True):
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

                    st.markdown(f"**Localização:** {locals_clean}")
                    st.markdown(f"**Artérias Afetadas:** {arteries_clean}")
                    st.markdown(f"**Sintomas Principais:** {', '.join(signs)}")
            else:
                st.error("Síndrome não encontrada.")

    st.sidebar.header("Consulta Rápida de Síndromes")
    with st.sidebar.expander("Ver todas as síndromes"):
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

            st.markdown(f"- **Localização:** {locals_clean}")
            st.markdown(f"- **Artérias Afetadas:** {arteries_clean}")
            st.markdown(f"- **Sintomas Principais:** {', '.join(syndrome['signs'])}")
            st.markdown("---")

if __name__ == "__main__":
    main()
