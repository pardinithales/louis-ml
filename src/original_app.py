import streamlit as st
import sqlite3
import requests
import json
import logging
from pathlib import Path
from datetime import datetime
import re
import unicodedata

# Configuração do Logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logging.debug("Iniciando a aplicação Streamlit.")

# Função para obter resposta do LLaMA via Ollama
def get_llm_response(prompt):
    logging.debug("Preparando requisição para Ollama.")
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                "model": "llama3.2",  # Certifique-se de que o modelo está correto
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        logging.debug("Resposta recebida do Ollama.")
        return response.json().get('response', '')
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao conectar com Ollama: {e}")
        return "Erro ao conectar com o modelo de linguagem."

# Função para conectar ao banco de dados
def get_db_connection():
    logging.debug("Estabelecendo conexão com o banco de dados.")
    try:
        conn = sqlite3.connect(r"C:\Users\fagun\OneDrive\Desktop\louiS_2.0\syndrome_data.db")
        logging.debug("Conexão com o banco de dados estabelecida.")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Erro ao conectar com o banco de dados: {e}")
        return None

# Função para carregar sintomas do banco de dados (em inglês)
@st.cache_data
def load_symptoms():
    logging.debug("Carregando sintomas do banco de dados.")
    conn = get_db_connection()
    if conn:
        try:
            # Ajuste o nome da coluna conforme verificado (provavelmente 'signs')
            query = "SELECT DISTINCT signs FROM syndromes"
            cursor = conn.execute(query)
            all_signs = cursor.fetchall()
            conn.close()
            
            # Extrair e criar uma lista única de sintomas
            symptoms_set = set()
            for signs_tuple in all_signs:
                sign = signs_tuple[0].strip()
                # Normalizar para remover acentos e tornar case-insensitive
                normalized_sign = unicodedata.normalize('NFD', sign).encode('ascii', 'ignore').decode('utf-8').lower()
                symptoms_set.add((sign, normalized_sign))
            
            # Ordenar a lista baseada no original (com acentos)
            symptoms = sorted([s[0] for s in symptoms_set])
            logging.debug(f"{len(symptoms)} sintomas únicos carregados.")
            return symptoms
        except sqlite3.Error as e:
            logging.error(f"Erro ao executar a consulta: {e}")
            conn.close()
            return []
        except Exception as e:
            logging.error(f"Erro ao processar sintomas: {e}")
            conn.close()
            return []
    else:
        return []

# Função para carregar todas as síndromes com seus sintomas
@st.cache_data
def load_syndromes():
    logging.debug("Carregando todas as síndromes do banco de dados.")
    conn = get_db_connection()
    if conn:
        try:
            query = "SELECT syndrome_name, signs, locals, arteries, notes, is_ipsilateral, local_name, vessel_name FROM syndromes"
            cursor = conn.execute(query)
            syndromes = cursor.fetchall()
            conn.close()
            logging.debug(f"{len(syndromes)} síndromes carregadas.")
            # Processar síndromes para facilitar a filtragem
            processed_syndromes = []
            for row in syndromes:
                syndrome = {
                    "syndrome_name": row[0],
                    "signs": json.loads(row[1]),
                    "locals": row[2],
                    "arteries": row[3],
                    "notes": row[4],
                    "is_ipsilateral": row[5],
                    "local_name": row[6],
                    "vessel_name": row[7]
                }
                processed_syndromes.append(syndrome)
            return processed_syndromes
        except sqlite3.Error as e:
            logging.error(f"Erro ao executar a consulta: {e}")
            conn.close()
            return []
        except json.JSONDecodeError as e:
            logging.error(f"Erro ao decodificar JSON dos sintomas: {e}")
            conn.close()
            return []
        except Exception as e:
            logging.error(f"Erro ao processar síndromes: {e}")
            conn.close()
            return []
    else:
        return []

# Função para filtrar e classificar as síndromes com base nos sintomas selecionados
def filter_and_rank_syndromes(selected_symptoms, syndromes):
    logging.debug("Filtrando e classificando as síndromes com base nos sintomas selecionados.")
    ranked_syndromes = []
    for syndrome in syndromes:
        matched_signs = set([symptom.lower() for symptom in syndrome["signs"]]).intersection(set([s.lower() for s in selected_symptoms]))
        match_count = len(matched_signs)
        if match_count > 0:
            ranked_syndromes.append({
                "syndrome": syndrome,
                "match_count": match_count
            })
    # Classificar as síndromes pelo número de correspondências (descendente)
    ranked_syndromes.sort(key=lambda x: x["match_count"], reverse=True)
    logging.debug(f"{len(ranked_syndromes)} síndromes correspondentes encontradas.")
    return ranked_syndromes

# Função para identificar sintomas a partir da entrada livre do usuário usando LLaMA
def identify_symptoms(user_input, known_symptoms):
    logging.debug("Identificando sintomas do texto livre usando LLaMA.")
    # Preparar o prompt em inglês com instruções claras e exemplo de saída
    prompt = f"""
    You have the following list of available symptoms in the database (in English):
    
    {', '.join(known_symptoms)}
    
    The user has provided the following symptoms in any language:
    
    "{user_input}"
    
    Please identify and list **exactly** the symptoms from the available list that are present in the user's description. Respond **only** with a JSON list of symptoms in English, for example:
    
    ["headache", "nausea"]
    
    Do not add explanations or any other text.
    
    Response:
    """
    response = get_llm_response(prompt)
    logging.debug(f"LLaMA response for symptom identification: {response}")

    # Processar a resposta
    identified_symptoms = []
    if response:
        # Tentar interpretar a resposta como uma lista JSON
        try:
            symptoms = json.loads(response)
            if isinstance(symptoms, list):
                # Filtrar sintomas válidos (comparação insensível a maiúsculas/minúsculas)
                identified_symptoms = [symptom.strip() for symptom in symptoms if symptom.strip().lower() in [s.lower() for s in known_symptoms]]
                logging.debug(f"Sintomas identificados: {identified_symptoms}")
        except json.JSONDecodeError:
            logging.warning("Resposta do LLaMA não está em formato JSON. Usando fallback de divisão por vírgulas.")

        if not identified_symptoms:
            # Fallback: usar regex para encontrar sintomas na entrada
            for symptom in known_symptoms:
                # Normalizar sintomas para comparação
                normalized_symptom = unicodedata.normalize('NFD', symptom).encode('ascii', 'ignore').decode('utf-8').lower()
                pattern = re.compile(re.escape(normalized_symptom), re.IGNORECASE)
                if re.search(pattern, user_input):
                    identified_symptoms.append(symptom)
            logging.debug(f"Sintomas identificados via regex: {identified_symptoms}")
    else:
        logging.warning("Nenhuma resposta recebida do LLaMA para identificação de sintomas.")

    return list(set(identified_symptoms))

def main():
    st.title("Louis - Sistema de Análise Neurológica")
    logging.debug("Título da aplicação definido.")

    # Carregar sintomas e síndromes
    symptoms = load_symptoms()
    syndromes = load_syndromes()
    logging.debug("Sintomas e síndromes carregados.")

    # Interface principal
    st.header("Digite os sintomas do paciente")
    logging.debug("Interface principal exibida.")

    # Entrada livre de sintomas
    free_text = st.text_area(
        "Digite os sintomas livremente:",
        placeholder="Exemplo: nausea, dizziness, and sensitivity alteration",
        help="Digite os sintomas que o paciente apresenta. Pode ser em qualquer idioma."
    )
    logging.debug(f"Sintomas inseridos via texto livre: {free_text}")

    # Botão para processar
    if st.button("Analisar Sintomas"):
        logging.debug("Botão 'Analisar Sintomas' pressionado.")
        user_input = free_text.strip()

        if user_input:
            # Identificar sintomas usando LLaMA
            identified_symptoms = identify_symptoms(user_input, symptoms)
            logging.debug(f"Sintomas identificados pelo LLaMA: {identified_symptoms}")

            # Remover duplicatas
            final_symptoms = list(set(identified_symptoms))
            logging.debug(f"Sintomas finais após validação: {final_symptoms}")

            if final_symptoms:
                # Filtrar e classificar as síndromes
                ranked_syndromes = filter_and_rank_syndromes(final_symptoms, syndromes)

                if ranked_syndromes:
                    # Selecionar as 3 síndromes mais prováveis
                    top_syndromes = ranked_syndromes[:3]
                    logging.debug(f"Top 3 síndromes selecionadas: {[s['syndrome']['syndrome_name'] for s in top_syndromes]}")

                    # Preparar detalhes para exibição
                    display_syndromes = [s["syndrome"] for s in top_syndromes]

                    # Gerar prompt para LLaMA para resumir e sugerir outras síndromes
                    symptoms_text = ", ".join(final_symptoms)
                    top_syndromes_text = "; ".join([s["syndrome_name"] for s in display_syndromes])
                    llm_prompt = f"""Based on the following symptoms: {symptoms_text}, the top three most probable syndromes are: {top_syndromes_text}.

1. Provide a concise summary of the main characteristics of these three syndromes.
2. Suggest other possible syndromes that could also be associated with these symptoms but are not among the top three most probable.

Respond in a clear and structured manner."""
                    logging.debug(f"Prompt para LLaMA para resumo e sugestões: {llm_prompt}")

                    # Obter resposta da IA
                    with st.spinner("Processando com IA..."):
                        llm_analysis = get_llm_response(llm_prompt)
                        logging.debug("Análise da IA recebida.")

                    # Exibir as três síndromes mais prováveis
                    st.subheader("Top 3 Síndromes Mais Prováveis")
                    for idx, syndrome in enumerate(display_syndromes, 1):
                        with st.expander(f"{idx}. {syndrome['syndrome_name']}", expanded=(idx==1)):
                            st.write(f"**Nome da Síndrome:** {syndrome['syndrome_name']}")
                            st.write(f"**Localização:** {syndrome['locals']}")
                            st.write(f"**Artérias Envolvidas:** {syndrome['arteries']}")
                            st.write(f"**Notas Importantes:** {syndrome['notes']}")
                            st.write(f"**Is Ipsilateral:** {syndrome['is_ipsilateral']}")
                            st.write(f"**Nome Local:** {syndrome['local_name']}")
                            st.write(f"**Nome do Vaso:** {syndrome['vessel_name']}")

                    # Exibir análise da IA
                    st.subheader("Análise da IA")
                    st.write(llm_analysis)
                    logging.debug("Resultados exibidos na interface.")
                else:
                    st.warning("Nenhuma síndrome encontrada para os sintomas fornecidos.")
                    logging.debug("Nenhuma síndrome correspondente encontrada.")
            else:
                st.warning("Nenhum sintoma válido identificado na entrada fornecida.")
                logging.debug("Nenhum sintoma válido identificado na entrada do usuário.")
        else:
            st.warning("Por favor, insira pelo menos um sintoma para análise.")
            logging.debug("Nenhum texto inserido pelo usuário.")

if __name__ == "__main__":
    logging.debug("Executando a função main.")
    main()
    logging.debug("Aplicação finalizada.")
