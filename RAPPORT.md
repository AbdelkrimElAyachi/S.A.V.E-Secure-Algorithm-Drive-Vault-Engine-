# Rapport de TP — S.A.V.E (Secure Algorithm Vault Engine)

**Étudiant :** Abdelkrim El Ayachi  
**Langage :** Python 3  
**Librairies :** customtkinter, darkdetect, packaging  

---

## 1. Choix et Conception de l'Application *(4 points)*

### Q : Définissez le contexte et le rôle de votre application.

J'ai développé **S.A.V.E** (Secure Algorithm Vault Engine), un **gestionnaire de mots de passe local** avec interface graphique. L'application permet à un utilisateur de :

- Créer un coffre-fort chiffré protégé par un mot de passe maître
- Stocker des identifiants (site, nom d'utilisateur, mot de passe) de façon chiffrée dans un fichier `vault.json`
- Se ré-authentifier à chaque lancement pour déverrouiller le coffre
- Copier un mot de passe déchiffré vers le presse-papiers d'un clic
- Verrouiller le coffre et effacer les clés de la mémoire à tout moment

Tout est local — aucune communication réseau.

---

### Q : Justifiez l'utilisation de chacun des trois algorithmes dans votre application.

| Algorithme | Rôle dans S.A.V.E | Justification |
|---|---|---|
| **Mini-MD5** | Hachage du mot de passe maître | Le mot de passe n'est jamais stocké en clair. À chaque login, le hash de l'entrée utilisateur est comparé au hash stocké. |
| **Mini-RSA** | Chiffrement (key-wrapping) de la clé S-DES | La clé symétrique ne doit jamais être stockée en clair. RSA la chiffre avec la clé publique ; seule la clé privée peut la récupérer. |
| **Mini-DES (S-DES)** | Chiffrement symétrique de chaque credential | Chaque champ (site, username, password) est chiffré avant d'être écrit dans le fichier JSON. |

---

### Q : Décrivez l'architecture logicielle et les interactions entre les différents modules.

```
src/
├── app.py                      # Point d'entrée
├── controllers/
│   └── vault_controller.py     # Orchestrateur : logique métier + crypto
├── crypto/
│   ├── mini_md5.py             # Fonction de hachage
│   ├── mini_rsa.py             # Chiffrement asymétrique
│   └── mini_des.py             # Chiffrement symétrique
└── ui/
    ├── login_window.py         # Fenêtre d'authentification
    ├── signin_window.py        # Fenêtre de création de coffre
    ├── main_window.py          # Tableau de bord principal
    └── add_password_window.py  # Dialogue d'ajout de credential
```

**Flux général :**

```
UI → VaultController → modules crypto (mini_md5, mini_rsa, mini_des) → vault.json
```

L'UI ne touche jamais directement aux modules crypto. Tout passe par le `VaultController` qui orchestre les opérations.

---

## 2. Implémentation du Mini-DES *(6 points)*

### Q : Implémentez une version simplifiée du DES pour chiffrer et déchiffrer des blocs de données.

Le module `src/crypto/mini_des.py` implémente **S-DES** avec :
- Clé de **10 bits**
- Blocs de **8 bits**
- **2 rounds** de Feistel
- 2 S-boxes (S0 et S1) de taille 4×4

---

### Q : Votre implémentation devra inclure la génération des sous-clés à partir d'une clé principale.

À partir de la clé de 10 bits, deux sous-clés de 8 bits (K1, K2) sont générées :

1. Appliquer **P10** (permutation de 10 bits)
2. Diviser en deux moitiés de 5 bits
3. Rotation circulaire gauche de 1 → appliquer **P8** → **K1**
4. Rotation circulaire gauche de 2 supplémentaires → appliquer **P8** → **K2**

Tables utilisées : `P10 = [3,5,2,7,4,10,1,9,8,6]`, `P8 = [6,3,7,4,8,5,10,9]`

---

### Q : Les opérations de permutation, de substitution (S-Box) et de mixage.

Chaque round applique la **fonction de Feistel fK** :

1. **Expansion** : le demi-bloc droit passe de 4 à 8 bits via la table **EP**
2. **XOR** avec la sous-clé (mixage)
3. **Substitution S-Box** : les 8 bits sont divisés en deux groupes de 4 bits, chacun passant par S0 ou S1 pour donner 2 bits → sortie de 4 bits
4. **Permutation P4** sur les 4 bits résultants
5. **XOR** avec le demi-bloc gauche

Structure complète d'un bloc : `IP → fK(K1) → SW (swap) → fK(K2) → IP_INV`

---

### Q : Démontrez le fonctionnement avec des exemples de chiffrement/déchiffrement.

Clé = `0b0111111101` (509), Texte clair = `"Gmail"`

| Champ | Avant chiffrement | Après chiffrement (hex) | Après déchiffrement |
|---|---|---|---|
| site | `"Gmail"` | `a3f1...` | `"Gmail"` ✓ |
| username | `"alice@gmail.com"` | `9c4b...` | `"alice@gmail.com"` ✓ |
| password | `"secret42"` | `7e2d...` | `"secret42"` ✓ |

**Déchiffrement = chiffrement avec sous-clés inversées (K2, K1)** — propriété de la structure Feistel.

---

## 3. Implémentation du Mini-RSA *(6 points)*

### Q : Implémentez une version simplifiée de RSA pour la génération de paires de clés et les opérations de chiffrement/déchiffrement.

Le module `src/crypto/mini_rsa.py` implémente RSA avec de petits premiers. Il est utilisé pour **chiffrer la clé S-DES** avant de la stocker dans le vault.

---

### Q : La génération de deux nombres premiers de petite taille.

Les premiers sont choisis aléatoirement dans une liste prédéfinie :

```
SMALL_PRIMES = [61, 53, 59, 67, 71, 73, 79, 83, 89, 97]
```

Deux premiers distincts `p` et `q` sont sélectionnés aléatoirement.

---

### Q : Le calcul de la clé publique et de la clé privée.

1. `n = p × q`
2. `φ(n) = (p-1) × (q-1)`
3. Choisir `e` tel que `1 < e < φ(n)` et `pgcd(e, φ(n)) = 1`
4. Calculer `d = e⁻¹ mod φ(n)` via l'algorithme d'Euclide étendu

- **Clé publique :** `(e, n)`
- **Clé privée :** `(d, n)`

---

### Q : Le chiffrement et le déchiffrement d'un message. Démontrez avec un exemple concret.

- **Chiffrement :** `C = M^e mod n`
- **Déchiffrement :** `M = C^d mod n`

Exponentiation modulaire rapide (square-and-multiply) utilisée pour la performance.

**Exemple :** `p=61, q=53 → n=3233, φ=3120, e=17, d=2753`

| Message M | Chiffrement | Déchiffrement |
|---|---|---|
| `65` | `65^17 mod 3233 = 2790` | `2790^2753 mod 3233 = 65` ✓ |
| Clé DES `509` | `509^17 mod 3233 = X` | `X^2753 mod 3233 = 509` ✓ |

**Dans l'application :** la clé S-DES de 2 octets est convertie en entier, chiffrée avec RSA, et stockée en hexadécimal dans `vault.json`. Au login, elle est déchiffrée avec `d` pour reconstruire la session S-DES.

---

## 4. Implémentation du Mini-MD5 *(4 points)*

### Q : Implémentez une version simplifiée de MD5 pour calculer l'empreinte numérique d'un message.

Le module `src/crypto/mini_md5.py` implémente MD5 complet (RFC 1321) avec :
- Sortie **128 bits** (32 caractères hex)
- **4 rounds** (FF, GG, HH, II), **64 étapes** au total
- Table de constantes K basée sur les sinus, table de décalages S

---

### Q : Le padding du message.

Avant traitement, le message est complété selon la règle MD5 standard :

```
message | 0x80 | zéros | longueur originale en bits (64 bits, little-endian)
```
Le padding est ajusté pour que la longueur totale soit ≡ 0 mod 64 octets.

---

### Q : Le découpage en blocs et les opérations de compression.

Le message paddé est découpé en blocs de **512 bits (64 octets)**. Chaque bloc est traité comme 16 mots de 32 bits (little-endian). Les 4 variables d'état `(a, b, c, d)` sont mises à jour à chaque étape via les fonctions F, G, H, I et accumulées.

---

### Q : Testez sur différentes chaînes et vérifiez la résistance aux collisions.

| Entrée | Hash mini-MD5 |
|---|---|
| `""` | `d41d8cd98f00b204e9800998ecf8427e` |
| `"password123"` | `482c811da5d5b4bc6d497ffa98491e38` |
| `"password124"` | hash totalement différent (effet avalanche) |
| `"Password123"` | hash différent (sensible à la casse) |
| `"MonMotDePasse!"` | hash unique et déterministe |

**Résistance aux collisions :** deux entrées différentes produisent systématiquement des hashs différents dans nos tests. L'effet avalanche est bien présent : un seul caractère de différence change l'intégralité du hash.

---

## 5. Intégration et Démonstration *(5 points)*

### Q : Intégrez les trois modules dans votre application.

Le `VaultController` est le point d'intégration central. Il importe et utilise les trois modules crypto de façon coordonnée :

```python
from src.crypto.mini_md5 import mini_md5
from src.crypto.mini_rsa import SimplifiedRSA
from src.crypto.mini_des import SimplifiedDES
```

---

### Q : Présentez un scénario de bout en bout illustrant l'utilisation combinée des trois algorithmes.

**Scénario : Création du coffre + ajout d'un credential + re-login**

**Phase 1 — Création du coffre (`initialize_vault`)**

```
Mot de passe maître "MonMotDePasse!"
        │
        ├─► [mini-MD5] ──────────────────► password_hash → vault.json
        │
        ├─► [mini-RSA] génère (e,n),(d,n) → vault.json
        │
        └─► random 10-bit key (509)
                │
                └─► [mini-RSA encrypt_key] ─► encrypted_des_key → vault.json
```

**Phase 2 — Ajout d'un credential (`add_password_entry`)**

```
{"site": "Gmail", "username": "alice@gmail.com", "password": "secret42"}
        │
        └─► [mini-DES(509)] encrypt chaque champ
                │
                └─► entrée chiffrée (hex) → vault.json["entries"]
```

**Phase 3 — Re-login (`handle_login`)**

```
Mot de passe "MonMotDePasse!"
        │
        ├─► [mini-MD5] → comparer avec password_hash → ✓ OK
        │
        ├─► [mini-RSA decrypt_key] → récupère session_key = 509
        │
        └─► [mini-DES(509)] decrypt toutes les entrées → affichage en clair
```

**Structure de vault.json après le scénario :**

```json
{
  "password_hash": "a3f29c1d...",
  "rsa_public_key":  { "e": 17,   "n": 3233 },
  "rsa_private_key": { "d": 2753, "n": 3233 },
  "encrypted_des_key": ["0x1a3f"],
  "entries": [
    {
      "site":     "f3a1...",
      "username": "9c4b...",
      "password": "7e2d..."
    }
  ]
}
```

---

### Q : Réalisez une démonstration claire et commentée de votre application.

**Lancement :**
```bash
pip install -r requirements.txt
python -m src.app
```

**Déroulement :**
1. Au premier lancement → fenêtre **"Initialize Secure Vault"** : saisie et confirmation du mot de passe maître (min. 8 caractères)
2. Après création → **tableau de bord** : liste vide, bouton "+ Add Password" et "Lock Vault"
3. Clic "+ Add Password" → modal : saisie site / username / password → "Save Password" → credential chiffré et affiché
4. Bouton "Copy" → mot de passe déchiffré copié dans le presse-papiers
5. Bouton "Lock Vault" → clés effacées de la mémoire, application fermée
6. Au relancement → fenêtre **"Master Vault Login"** : saisie du mot de passe → déverrouillage et affichage des credentials

---

## 6. Qualité du Code et Documentation *(5 points)*

### Q : Votre code devra être propre, bien structuré et commenté.

- **Architecture MVC** : séparation nette UI / Controller / Crypto
- **Constantes nommées** : toutes les valeurs magiques (dimensions, polices, couleurs, longueurs min/max) sont définies comme constantes en tête de chaque fichier
- **Docstrings** sur toutes les méthodes publiques
- **Gestion d'erreurs** : blocs `try/except` avec logs préfixés (`[Controller]`, `[Crypto]`, `[UI]`)
- **Validation des entrées** : longueur min/max vérifiée dans chaque fenêtre UI

---

### Q : Tests effectués et leurs résultats.

| Test | Résultat |
|---|---|
| Création du coffre → vault.json valide | ✓ |
| Login avec le bon mot de passe | ✓ Accès accordé |
| Login avec un mauvais mot de passe | ✓ Accès refusé |
| Ajout d'un credential → visible dans la liste | ✓ |
| Credentials identiques après redémarrage | ✓ |
| S-DES : decrypt(encrypt(x)) == x | ✓ |
| RSA : unwrap(wrap(clé)) == clé originale | ✓ |
| MD5 : même input → même hash | ✓ |
| MD5 : effet avalanche observable | ✓ |

---

### Q : Les éventuelles difficultés rencontrées et les solutions apportées.

**Difficulté 1 — Table IP_INV incorrecte (S-DES)**  
La première table `IP_INV` était erronée, causant un déchiffrement incorrect. **Solution :** recalcul mathématique de l'inverse de `IP` et vérification par des tests unitaires encrypt/decrypt.

**Difficulté 2 — Perte des zéros de tête en RSA**  
Une clé S-DES de faible valeur (ex: `5 = 0x0005`) perdait son zéro de tête lors de la conversion entier → bytes. **Solution :** forcer `to_bytes(key_length=2, ...)` lors du déchiffrement RSA.

**Difficulté 3 — Reconstruction de l'objet RSA sans régénération**  
Au re-login, il fallait restaurer les clés RSA depuis le vault sans recalculer de nouveaux premiers. **Solution :** utiliser `SimplifiedRSA.__new__(SimplifiedRSA)` pour créer l'instance vide, puis injecter `n`, `e`, `d` manuellement.

---

## Conclusion

**S.A.V.E** illustre concrètement l'utilisation combinée des trois piliers de la cryptographie :

- **Mini-MD5** → authentification sans stocker le mot de passe
- **Mini-RSA** → protection de la clé symétrique au repos
- **Mini-DES** → chiffrement performant des données utilisateur

Ce schéma hybride (hash + asymétrique pour l'échange de clé + symétrique pour les données) est le même paradigme que TLS/HTTPS, ce qui valide l'approche architecturale du projet.
