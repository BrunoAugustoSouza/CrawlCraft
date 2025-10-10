import pandas as pd
import scipy.stats as stats

# Função para calcular rating com média e desvio padrão
def get_rating_with_std(value: float, mean: float, std: float, inverted: bool = False) -> str:
    """
    Retorna o rating baseado na posição do value em relação à média (mean) e desvio padrão (std)
    usando uma distribuição normal. 
    Se inverted=True, inverte o sentido de Fear/Greed.
    """
    if std == 0:
        return 'Neutral'  # Evitar divisão por zero

    z = (value - mean) / std
    percentile = stats.norm.cdf(z) * 100

    if percentile <= 25:
        rating = 'Extreme Fear'
    elif percentile <= 45:
        rating = 'Fear'
    elif percentile <= 55:
        rating = 'Neutral'
    elif percentile <= 75:
        rating = 'Greed'
    else:
        rating = 'Extreme Greed'

    if inverted:
        # Inverter apenas os ratings relacionados a Fear/Greed
        inversion_map = {
            'Extreme Fear': 'Extreme Greed',
            'Fear': 'Greed',
            'Greed': 'Fear',
            'Extreme Greed': 'Extreme Fear',
            'Neutral': 'Neutral'
        }
        rating = inversion_map[rating]

    return rating

def get_rating_fixed(value: float) -> str:
    """
    Retorna o rating baseado em faixas fixas de 0 a 100:
    0-25: Extreme Fear
    25-45: Fear
    45-55: Neutral
    55-75: Greed
    75-100: Extreme Greed
    """
    if value <= 25:
        return 'Extreme Fear'
    elif value <= 45:
        return 'Fear'
    elif value <= 55:
        return 'Neutral'
    elif value <= 75:
        return 'Greed'
    else:
        return 'Extreme Greed'
