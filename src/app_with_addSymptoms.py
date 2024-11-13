import streamlit as st
import requests
import json
import logging
import os
import sqlite3
from typing import Dict
from pathlib import Path
from datetime import datetime
from database.db_connection import init_db, load_symptoms, load_syndromes, get_db_path, get_db_connection
import ast
from openai import OpenAI
from anthropic import Anthropic
from prompt_toolkit import PromptSession

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
    logging.info("Iniciando extração de sintomas...")
    try:
        # Log da lista completa de sintomas disponíveis
        logging.info(f"Total de sintomas disponíveis: {len(lista_sintomas)}")
        logging.info("Lista completa de sintomas disponíveis:")
        for s in lista_sintomas:
            logging.info(f"  - {s}")
            
        # Formata lista de sintomas
        formatted_symptom_list = '\n'.join(f"- {symptom}" for symptom in lista_sintomas)

        system_prompt = f"""You are a specialist in vascular neurological syndromes. 
        IMPORTANT: Extract ALL matching symptoms that appear in the case from the following list. 
        
        Available symptoms list:
        {formatted_symptom_list}
        
        RESPONSE FORMAT EXAMPLE:
        Hemiparesis / Hemiplegia, Oculomotor palsy (III), Ataxia
        
        RULES:
        1. Use ONLY symptoms EXACTLY as they appear in the provided list
        2. Output ALL matching symptoms from the list
        3. Separate symptoms by commas
        4. NO additional text"""

        user_prompt = f"""Extract ALL matching symptoms from this case:
        {texto_caso}"""

        # Log do texto enviado para análise
        logging.info(f"Texto para análise: {texto_caso}")

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )

        llm_output = response.choices[0].message.content.strip()
        logging.info(f"Resposta bruta da OpenAI: {llm_output}")

        extracted_symptoms = [s.strip() for s in llm_output.split(',')]
        logging.info(f"Total de sintomas extraídos: {len(extracted_symptoms)}")
        logging.info("Sintomas extraídos antes do matching:")
        for s in extracted_symptoms:
            logging.info(f"  - {s}")

        matched_symptoms = []
        for symptom in extracted_symptoms:
            if symptom.lower().strip() in [s.lower().strip() for s in lista_sintomas]:
                matched_symptoms.append(symptom)

        logging.info(f"Total de sintomas após matching: {len(matched_symptoms)}")
        logging.info("Sintomas finais após matching:")
        for s in matched_symptoms:
            logging.info(f"  - {s}")

        return matched_symptoms

    except Exception as e:
        logging.error(f"Erro ao processar sintomas: {str(e)}")
        return []

@st.cache_data
def get_claude_response(prompt):
    logging.info("Enviando prompt para o Claude para gerar resumo comparativo")
    try:
        response = anthropic_client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            temperature=0.6,
            messages=[{
                "role": "user",
                "content": prompt
            }]
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

class SymptomAnalyzer:
    def __init__(self, api_key: str, db_path: str):
        self.api_key = api_key
        self.db_path = str(Path(db_path).absolute())
        self.model = "claude-3-5-haiku-20241022"
        self.session = PromptSession()
        self.init_db()

    def init_db(self):
        """Initialize database and create tables if needed"""
        try:
            # Create database directory
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Create syndromes table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS syndromes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    syndrome_name TEXT NOT NULL UNIQUE,
                    signs TEXT,
                    locals TEXT,
                    arteries TEXT, 
                    notes TEXT,
                    is_ipsilateral TEXT,
                    local_name TEXT,
                    vessel_name TEXT,
                    registered_at TEXT,
                    updated_at TEXT
                )
            """)
            
            self.conn.commit()
            logging.info(f"✓ Banco de dados inicializado em: {self.db_path}")
            
        except Exception as e:
            logging.error(f"Erro ao inicializar banco de dados: {str(e)}")
            raise

    def analyze_symptoms(self, symptoms_text: str) -> dict:
        """Analisa sintomas e sinais com Claude"""
        try:
            response = anthropic_client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": f'''Você é um especialista em síndromes neurológicas vasculares.
                    IMPORTANTE: Responda APENAS com o formato JSON solicitado, identificando TODAS as síndromes possíveis relacionadas aos sintomas descritos.

                    [ANÁLISE REQUERIDA]
                    Analise o texto fornecido e identifique TODAS as síndromes vasculares possíveis, considerando:
                    1. Território vascular afetado exato
                    2. Sinais e sintomas neurológicos específicos
                    3. Localizações anatômicas precisas
                    4. Detalhes do suprimento arterial
                    5. Lateralidade dos sintomas
                    6. Notas clínicas importantes
                    7. Referências de imagem anatômica

                    [FORMATO DE SAÍDA OBRIGATÓRIO]
                    {{
                        "syndromes": [
                            {{
                                "syndrome_data": {{
                                    "syndrome_name": "nome da síndrome",
                                    "signs": ["sinal 1", "sinal 2"],
                                    "locals": ["local 1", "local 2"],
                                    "arteries": ["artéria 1", "artéria 2"],
                                    "notes": ["Observação clínica 1", "Característica importante 2"],
                                    "is_ipsilateral": {{"sinal1": "sim/não"}},
                                    "local_name": ["imagem1.png"],
                                    "vessel_name": ["vaso1.png"],
                                    "registered_at": ["2024-01-01 00:00:00"],
                                    "updated_at": ["2024-01-01 00:00:00"]
                                }}
                            }}
                        ]
                    }}

                    IMPORTANTE: 
                    1. O campo "notes" é OBRIGATÓRIO e deve conter observações clínicas relevantes
                    2. Retorne TODAS as síndromes relacionadas
                    3. Mantenha EXATAMENTE este formato JSON

                    [TEXTO PARA ANÁLISE]
                    {symptoms_text}'''
                }]
            )
            
            response_text = response.content[0].text
            logging.info(f"Resposta bruta do Claude: {response_text}")
            
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_text = response_text[json_start:json_end]
                
                analysis = json.loads(json_text)
                logging.info(f"JSON parseado: {json.dumps(analysis, indent=2)}")
                
                if 'syndrome_data' in analysis:
                    analysis = {'syndromes': [{'syndrome_data': analysis['syndrome_data']}]}
                
                logging.info(f"Estrutura final retornada: {json.dumps(analysis, indent=2)}")
                
                return analysis
                
            except json.JSONDecodeError as e:
                logging.error(f"Erro no parse do JSON: {str(e)}")
                logging.error(f"Texto JSON problemático: {json_text}")
                return None
                
        except Exception as e:
            logging.error(f"Erro na requisição: {str(e)}")
            return None

    def add_syndrome_to_db(self, syndrome_data: Dict):
        """Adiciona nova síndrome ao banco"""
        try:
            logging.info(f"Processando síndrome para adicionar ao banco: {syndrome_data}")
            
            # Garantir que todos os campos são strings JSON válidas
            signs = json.dumps(syndrome_data.get('signs', []))
            locals_ = json.dumps(syndrome_data.get('locals', []))
            arteries = json.dumps(syndrome_data.get('arteries', []))
            notes = json.dumps(syndrome_data.get('notes', []))
            is_ipsilateral = json.dumps(syndrome_data.get('is_ipsilateral', {}))
            local_name = json.dumps(syndrome_data.get('local_name', []))
            vessel_name = json.dumps(syndrome_data.get('vessel_name', []))
            
            # Usar timestamps fornecidos ou gerar novos
            registered_at = syndrome_data.get('registered_at', [datetime.now().strftime("%Y-%m-%d %H:%M:%S")])[0]
            updated_at = syndrome_data.get('updated_at', [datetime.now().strftime("%Y-%m-%d %H:%M:%S")])[0]

            self.cursor.execute("""
                INSERT INTO syndromes (
                    syndrome_name,
                    signs,
                    locals,
                    arteries,
                    notes,
                    is_ipsilateral,
                    local_name,
                    vessel_name,
                    registered_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                syndrome_data['syndrome_name'],
                signs,
                locals_,
                arteries,
                notes,
                is_ipsilateral,
                local_name,
                vessel_name,
                registered_at,
                updated_at
            ))
            
            self.conn.commit()
            logging.info(f"✓ Síndrome adicionada com sucesso: {syndrome_data['syndrome_name']}")
            
        except Exception as e:
            logging.error(f"Erro ao adicionar síndrome: {str(e)}")
            logging.error(f"Dados da síndrome: {syndrome_data}")
            self.conn.rollback()
            raise

def get_last_syndrome():
    """Retorna a última síndrome adicionada ao banco"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT syndrome_name, signs, locals, arteries, notes, updated_at 
            FROM syndromes 
            ORDER BY updated_at DESC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        
        if result:
            try:
                return {
                    "syndrome_name": result[0],
                    "signs": json.loads(result[1]) if result[1] else [],
                    "locals": json.loads(result[2]) if result[2] else [],
                    "arteries": json.loads(result[3]) if result[3] else [],
                    "notes": json.loads(result[4]) if result[4] else [],
                    "updated_at": result[5] if result[5] and result[5] != '[]' else "Não disponível"
                }
            except json.JSONDecodeError as e:
                logging.error(f"Erro ao decodificar JSON: {e}")
                return None
        
        st.warning("Nenhuma síndrome encontrada")
        return None
        
    except Exception as e:
        logging.error(f"Erro ao buscar última síndrome: {e}")
        return None
    finally:
        if conn:
            conn.close()

def add_syndrome(sd: Dict):
    """Função de callback para adicionar síndrome ao banco"""
    try:
        # Verificar se já existe
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM syndromes WHERE syndrome_name = ?", 
            (sd['syndrome_name'],)
        )
        count = cursor.fetchone()[0]
        
        if count > 0:
            logging.warning(f"Síndrome {sd['syndrome_name']} já existe no banco")
            st.warning(f"Síndrome {sd['syndrome_name']} já existe no banco")
            return
            
        # Preparar dados para inserção
        syndrome_data = {
            'syndrome_name': sd['syndrome_name'],
            'signs': sd.get('signs', []),
            'locals': sd.get('locals', []),
            'arteries': sd.get('arteries', []),
            'notes': sd.get('notes', []),
            'is_ipsilateral': sd.get('is_ipsilateral', {}),
            'local_name': sd.get('local_name', []),
            'vessel_name': sd.get('vessel_name', []),
            'registered_at': sd.get('registered_at', []),
            'updated_at': sd.get('updated_at', [])
        }
        
        # Tentar adicionar
        analyzer = SymptomAnalyzer(
            api_key=st.secrets["CLAUDE_API_KEY"],
            db_path=get_db_path()
        )
        analyzer.add_syndrome_to_db(syndrome_data)
        
        # Verificar se foi adicionada
        cursor.execute(
            "SELECT COUNT(*) FROM syndromes WHERE syndrome_name = ?", 
            (sd['syndrome_name'],)
        )
        new_count = cursor.fetchone()[0]
        
        if new_count > count:
            logging.info(f"✓ Síndrome {sd['syndrome_name']} adicionada com sucesso")
            st.success(f"✓ Síndrome {sd['syndrome_name']} adicionada!")
            
            # Limpar cache do Streamlit
            st.cache_data.clear()
            
            # Recarregar dados
            st.rerun()  # Atualizado de experimental_rerun para rerun
        else:
            logging.error("Erro: síndrome não foi adicionada")
            st.error("Erro: síndrome não foi adicionada")
            
    except Exception as e:
        logging.error(f"Erro ao adicionar síndrome: {str(e)}")
        st.error(f"Erro ao adicionar síndrome: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    st.title("Louis - Sistema de Análise Neurológica")
    
    # Carrega os dados
    symptoms_list, normalized_symptoms_list, normalized_to_original = get_symptoms()
    syndromes = get_syndromes()
    
    if not symptoms_list or not syndromes:
        st.error("Erro ao carregar banco de dados")
        return
        
    st.sidebar.success(f"Banco conectado - {len(syndromes)} síndromes")
    
    # Adiciona tabs no topo
    tab1, tab2 = st.tabs(["Análise de Sintomas", "Análise com Claude"])
    
    with tab1:
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
                st.rerun()  # Atualizado de experimental_rerun para rerun

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

    with tab2:
        st.subheader("Análise de Síndromes com Claude")
        
        syndrome_text = st.text_area("Cole aqui o texto para análise de síndromes:", height=300)
        
        if st.button("Analisar com Claude"):
            if not syndrome_text:
                st.warning("Por favor, insira um texto para análise.")
                return
            
            try:
                analyzer = SymptomAnalyzer(
                    api_key=st.secrets["CLAUDE_API_KEY"],
                    db_path=get_db_path()
                )
                
                analysis = analyzer.analyze_symptoms(syndrome_text)
                logging.info(f"Resultado da análise: {json.dumps(analysis, indent=2)}")
                
                if not analysis:
                    st.error("Erro na análise.")
                    return
                    
                if 'syndromes' not in analysis:
                    st.error("Formato de resposta inválido")
                    return
                    
                # Mostrar síndromes encontradas
                for idx, syndrome in enumerate(analysis['syndromes']):
                    sd = syndrome['syndrome_data']
                    st.write("---")
                    st.subheader(sd['syndrome_name'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Sinais e Sintomas:**")
                        for sign in sd['signs']:
                            st.write(f"- {sign}")
                        
                        st.write("**Localização:**")
                        for local in sd['locals']:
                            st.write(f"- {local}")
                    
                    with col2:
                        st.write("**Artérias:**")
                        for artery in sd['arteries']:
                            st.write(f"- {artery}")
                        
                        st.write("**Notas:**")
                        for note in sd['notes']:
                            st.write(f"- {note}")
                    
                    # Botão de adicionar com callback
                    button_key = f"add_{idx}"
                    st.button(
                        "Adicionar ao Banco",
                        key=button_key,
                        on_click=add_syndrome,
                        args=(sd,)
                    )
            except Exception as e:
                st.error(f"Erro: {e}")

if __name__ == "__main__":
    main()
