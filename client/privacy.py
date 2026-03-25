import tenseal as ts
import numpy as np

def create_context():
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    context.global_scale = 2**40
    context.generate_galois_keys()
    return context

def apply_dp_noise(params, sigma=0.1, C=1.0):
    """Applique le clipping et le bruit gaussien sur les paramètres du modèle."""
    noisy_params = []
    for p in params:
        p_float = p.astype(np.float32)
        # Clipping (limiter l'influence d'un nœud)
        norm = np.linalg.norm(p_float)
        if norm > C:
            p_float = p_float * (C / norm)
        # Ajout du bruit
        noise = np.random.normal(0, sigma * C, size=p_float.shape)
        # Retour au format attendu par Flower (uint8 pour la sérialisation LightGBM)
        noisy_params.append((p_float + noise).astype(np.uint8))
    return noisy_params