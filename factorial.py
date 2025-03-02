import math
from typing import Union

def factorial(n: Union[int, float]) -> int:
    """
    Calcule la factorielle d'un nombre en utilisant la bibliothèque math pour une performance optimale.
    
    Args:
        n (Union[int, float]): Le nombre dont on veut calculer la factorielle
        
    Returns:
        int: La factorielle du nombre
        
    Raises:
        ValueError: Si le nombre est négatif ou n'est pas un entier
        OverflowError: Si le résultat est trop grand pour être représenté
    """
    # Vérification que n est un nombre positif et entier
    if not float(n).is_integer():
        raise ValueError("Le nombre doit être un entier")
    if n < 0:
        raise ValueError("Le nombre doit être positif ou nul")
    
    # Conversion en entier
    n = int(n)
    
    try:
        # Utilisation de math.factorial pour une performance optimale
        return math.factorial(n)
    except OverflowError:
        raise OverflowError("Le résultat est trop grand pour être calculé")

# Exemple d'utilisation
if __name__ == "__main__":
    # Tests avec différentes valeurs
    test_values = [0, 5, 10, 20]
    
    for value in test_values:
        try:
            result = factorial(value)
            print(f"Factorielle de {value} = {result}")
        except (ValueError, OverflowError) as e:
            print(f"Erreur pour {value}: {str(e)}") 