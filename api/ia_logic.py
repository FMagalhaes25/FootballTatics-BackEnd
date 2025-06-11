import pandas as pd
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==============================================================================
# SEÇÃO 1: FUNÇÕES AUXILIARES (INTERNAS)
# ==============================================================================

def _predict_player_positions(player_df, scaler, model):
    posicoes_modelo = ['CAM', 'CB', 'CDM', 'CM', 'LB', 'LM', 'LW', 'RB', 'RM', 'RW', 'ST']
    input_scaled = scaler.transform(player_df)
    predictions = model.predict(input_scaled, verbose=0)
    return dict(zip(posicoes_modelo, predictions.flatten()))

def _mapear_posicao_para_grupo(posicao_str):
    posicao_upper = posicao_str.upper()
    if 'CB' in posicao_upper or 'LB' in posicao_upper or 'RB' in posicao_upper:
        return 'Defensor'
    if 'CDM' in posicao_upper:
        return 'Volante'
    if 'CM' in posicao_upper or 'CAM' in posicao_upper or 'LM' in posicao_upper or 'RM' in posicao_upper:
        return 'Meia'
    if 'LW' in posicao_upper or 'RW' in posicao_upper:
        return 'Ponta'
    if 'ST' in posicao_upper:
        return 'Atacante'
    return 'Outro'

# ==============================================================================
# LÓGICA DE AVALIAÇÃO DE TÁTICAS
# ==============================================================================

REQUISITOS_TATICAS = {
    'Tiki Taka': {
        'total_jogadores_linha': 10,
        'Defensor': {'min': 4, 'max': 4, 'ideal': 4}, 'Volante': {'min': 1, 'max': 2, 'ideal': 2},
        'Meia': {'min': 2, 'max': 3, 'ideal': 3}, 'Ponta': {'min': 2, 'max': 2, 'ideal': 2},
        'Atacante': {'min': 1, 'max': 1, 'ideal': 1},
        'prioridade': ['Meia', 'Volante', 'Defensor', 'Ponta', 'Atacante']
    },
    'Jogada pelas Pontas': {
        'total_jogadores_linha': 10,
        'Defensor': {'min': 4, 'max': 4, 'ideal': 4}, 'Volante': {'min': 1, 'max': 2, 'ideal': 1},
        'Meia': {'min': 2, 'max': 2, 'ideal': 2}, 'Ponta': {'min': 2, 'max': 2, 'ideal': 2},
        'Atacante': {'min': 1, 'max': 2, 'ideal': 1},
        'prioridade': ['Ponta', 'Defensor', 'Atacante', 'Meia', 'Volante']
    },
    'Contra-Ataque': {
        'total_jogadores_linha': 10,
        'Defensor': {'min': 4, 'max': 5, 'ideal': 4}, 'Volante': {'min': 1, 'max': 2, 'ideal': 2},
        'Meia': {'min': 1, 'max': 2, 'ideal': 1}, 'Ponta': {'min': 1, 'max': 2, 'ideal': 2},
        'Atacante': {'min': 1, 'max': 2, 'ideal': 1},
        'prioridade': ['Defensor', 'Ponta', 'Atacante', 'Volante', 'Meia']
    },
    'Pressão': {
        'total_jogadores_linha': 10,
        'Defensor': {'min': 4, 'max': 4, 'ideal': 4}, 'Volante': {'min': 2, 'max': 3, 'ideal': 2},
        'Meia': {'min': 2, 'max': 3, 'ideal': 3}, 'Ponta': {'min': 0, 'max': 2, 'ideal': 1},
        'Atacante': {'min': 1, 'max': 2, 'ideal': 1},
        'prioridade': ['Meia', 'Volante', 'Atacante', 'Defensor']
    },
    'Conexão Direta': {
        'total_jogadores_linha': 10,
        'Defensor': {'min': 3, 'max': 4, 'ideal': 4}, 'Volante': {'min': 1, 'max': 2, 'ideal': 1},
        'Meia': {'min': 1, 'max': 2, 'ideal': 1}, 'Ponta': {'min': 0, 'max': 2, 'ideal': 1},
        'Atacante': {'min': 2, 'max': 3, 'ideal': 2},
        'prioridade': ['Atacante', 'Defensor', 'Volante', 'Ponta', 'Meia']
    },
    'Retranca Total': {
        'total_jogadores_linha': 10,
        'Defensor': {'min': 5, 'max': 6, 'ideal': 5}, 'Volante': {'min': 2, 'max': 3, 'ideal': 3},
        'Meia': {'min': 0, 'max': 1, 'ideal': 0}, 'Ponta': {'min': 0, 'max': 1, 'ideal': 0},
        'Atacante': {'min': 0, 'max': 1, 'ideal': 1},
        'prioridade': ['Defensor', 'Volante', 'Atacante']
    },
}

def _avaliar_fit_tatica(tactic_name, group_counts):
    logging.debug(f"Iniciando _avaliar_fit_tatica para tática: '{tactic_name}' com group_counts: {group_counts}")
    
    requisitos = REQUISITOS_TATICAS.get(tactic_name)
    if not requisitos:
        logging.warning(f"Tática desconhecida: {tatic_name}")
        return None, "Tática desconhecida."

    score = 0
    justificativa_partes = []
    current_total = sum(group_counts.values())
    justificativa_final = f"Seu elenco se encaixa bem na tática {tactic_name}." 

    if current_total != requisitos['total_jogadores_linha']:
        score += abs(current_total - requisitos['total_jogadores_linha']) * 10
        justificativa_partes.append(f"Número total de jogadores de linha ({current_total}) não é o ideal ({requisitos['total_jogadores_linha']}).")
        
    for group in requisitos['prioridade']:
        current_count = group_counts.get(group, 0)
        ideal_count = requisitos[group]['ideal']
        min_count = requisitos[group]['min']
        max_count = requisitos[group]['max']

        diff = abs(current_count - ideal_count)
        score += diff

        if not (min_count <= current_count <= max_count):
            score += 5
            if current_count < min_count:
                justificativa_partes.append(f"Poucos {group}s ({current_count}/{min_count}-{max_count} ideais).")
            elif current_count > max_count:
                justificativa_partes.append(f"Muitos {group}s ({current_count}/{min_count}-{max_count} ideais).")
        else:
            if current_count == ideal_count:
                justificativa_partes.append(f"Número ideal de {group}s ({current_count}).")
            else:
                justificativa_partes.append(f"Bom número de {group}s ({current_count}/{ideal_count} ideal).")
                
    if justificativa_partes:
        justificativa_final = f"Adaptação para {tactic_name}: " + ", ".join(justificativa_partes) + "."

    logging.debug(f"Finalizando _avaliar_fit_tatica para '{tactic_name}'. Score: {score}, Justificativa: {justificativa_final}") # Log de depuração final
    return score, justificativa_final

def _sugerir_taticas_por_fit(group_counts, num_sugestoes=3, tolerancia_score=10):
    logging.info(f"Iniciando sugestão de táticas para contagens de grupo: {group_counts}")
    resultados_taticas = []
    for tatic_name in REQUISITOS_TATICAS.keys():
        score, justificativa = _avaliar_fit_tatica(tatic_name, group_counts)
        if score is not None:
            resultados_taticas.append({
                'nome': tatic_name,
                'score': score,
                'justificativa': justificativa
            })
            logging.info(f"Tática: {tatic_name}, Score: {score}, Justificativa: {justificativa}")
    
    resultados_taticas.sort(key=lambda x: x['score'])
    logging.info(f"Resultados de táticas ordenados: {resultados_taticas}")
    
    sugestoes_finais = {}
    
    if resultados_taticas:
        best_score = resultados_taticas[0]['score']
        logging.info(f"Melhor score inicial: {best_score}")
        for tatic in resultados_taticas:
            if tatic['score'] <= best_score + tolerancia_score:
                sugestoes_finais[tatic['nome']] = {
                    'sugerida': True,
                    'justificativa': tatic['justificativa']
                }
            if len(sugestoes_finais) >= num_sugestoes:
                break
    
    logging.info(f"Sugestões finais geradas: {sugestoes_finais}")
    return sugestoes_finais

# ==============================================================================
# FUNÇÃO PRINCIPAL
# ==============================================================================

def recomendar_formacao_com_ia(lista_jogadores, model, scaler):
    """
    Recebe uma lista de jogadores, usa um modelo de IA para prever posições,
    e retorna sugestões de tática E a lista de jogadores com posições sugeridas.
    """
    jogadores_de_linha = [p for p in lista_jogadores if not p.get('goleiro', False)]
    
    logging.info(f"Total de jogadores de linha recebidos: {len(jogadores_de_linha)}")

    jogadores_com_posicao = []

    if len(jogadores_de_linha) == 0:
        logging.warning("Nenhum jogador de linha encontrado para classificação de IA.")
        return {
            'sugestoes': {},
            'no_match': True,
            'message': 'Nenhum jogador de linha encontrado para análise. Adicione jogadores ao seu elenco.',
            'jogadores_classificados': []
        }

    nomes_features_treino = [
        'weight', 'height', 'wh', 'movement', 'finishing_acc', 'skills', 'defensive_rating'
    ]

    for jogador in jogadores_de_linha:
        altura = jogador['altura']
        peso = jogador['peso']
        wh = (peso + altura) / 2.0
        
        try:
            jogador_df = pd.DataFrame([[
                peso, altura, wh,
                jogador['velocidade'], jogador['chute'], jogador['passe'], jogador['defesa']
            ]], columns=nomes_features_treino)
            
            probabilidades = _predict_player_positions(jogador_df, scaler, model)
            melhor_posicao_prevista = max(probabilidades, key=probabilidades.get)
            grupo_principal = _mapear_posicao_para_grupo(melhor_posicao_prevista)
        except Exception as e:
            logging.error(f"Erro ao classificar jogador {jogador.get('nome', 'desconhecido')}: {e}")
            melhor_posicao_prevista = 'Sem Sugestão (Erro AI)'
            grupo_principal = 'Outro'
        
        jogadores_com_posicao.append({
            'nome': jogador['nome'],
            'posicao_sugerida': melhor_posicao_prevista,
            'grupo_tatico': grupo_principal
        })
        logging.info(f"Jogador: {jogador['nome']}, Posição AI: {melhor_posicao_prevista}, Grupo Tático: {grupo_principal}")


    contagem_grupos = Counter([p['grupo_tatico'] for p in jogadores_com_posicao])
    logging.info(f"Contagem final de grupos táticos: {contagem_grupos}")
    
    sugestoes_taticas = _sugerir_taticas_por_fit(contagem_grupos)
    
    formacao_sugerida_principal = None
    if sugestoes_taticas:
        melhor_tatica_nome = next(iter(sugestoes_taticas), None)
        if melhor_tatica_nome:
            formacao_sugerida_principal = melhor_tatica_nome

    response_data = {
        'jogadores_classificados': jogadores_com_posicao,
        'formacao_sugerida_principal': formacao_sugerida_principal
    }

    if len(jogadores_de_linha) < 10:
        logging.warning("Número insuficiente de jogadores de linha para uma sugestão de tática completa.")
        response_data.update({
            'sugestoes': sugestoes_taticas,
            'no_match': True,
            'message': 'Para sugestões de táticas mais precisas, tenha 10 jogadores de linha no elenco.'
        })
    elif not sugestoes_taticas:
        logging.info("Nenhuma tática adequada foi encontrada após a avaliação de fit.")
        response_data.update({
            'sugestoes': {},
            'no_match': True,
            'message': 'Nenhuma tática adequada foi encontrada com os critérios atuais.'
        })
    else:
        response_data.update({
            'sugestoes': sugestoes_taticas,
            'no_match': False,
            'message': 'Táticas sugeridas com base no seu elenco:'
        })
        
    return response_data