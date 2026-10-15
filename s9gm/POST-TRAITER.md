<!-- destinations: github -->
# Post-traiter : d'un `.outb` aux statistiques, aux figures, au DEL

**Une seule façon de post-traiter dans ce cours : le paquet `s9gm`.** Cette page va du fichier de sortie d'OpenFAST
(`main.outb`) jusqu'au dommage de fatigue, avec les fonctions qui existent dans `s9gm/` et rien d'autre. Toutes les
consignes de séance renvoient ici.

Les commandes se lancent **depuis n'importe quel dossier**, environnement `s9gm-fowt` activé (`s9gm doctor` vérifie le poste). L'exemple fil rouge est le
cas `F01` (séance 0a), déjà lancé par `bash cas/run_cas.sh F01` (sorties sous `results/F01/`) ; il ne donne aucune valeur-réponse : les chiffres sont à lire chez vous.

**Où vit ce que vous produisez.** `s9gm/`, `cas/` et `modeles/` sont des fichiers suivis par git : vous les lisez et
vous les utilisez, **vous ne les modifiez pas**. Vos figures, vos tableaux et vos copies de modules vivent sous
`results/` (ignoré par git).

| Étape | Fonction | Pour quoi faire |
|---|---|---|
| 1 | `s9gm.lire.lire` | lire un `.outb` en tableau, avec les unités |
| 2 | `s9gm.lire.debut_regime`, `visu.tracer_series` | regarder la courbe, choisir et justifier `t_transitoire` |
| 3 | `s9gm.lire.statistiques` | moyenne, écart-type, min, max, transitoire écarté |
| 4 | `s9gm.visu.tracer_series`, `tracer_statistiques`, `tracer_courbes` | figures à la charte du cours |
| 5 | `scipy.signal.welch` | spectre d'un canal (`s9gm` n'a pas de fonction spectre) |
| 6 | `s9gm.fatigue` | rainflow, S-N, Miner, DEL (squelette : quatre fonctions sont à écrire par vous) |

## 1. Lire le fichier de sortie

```python
from s9gm import lire

df, unites = lire.lire("results/F01/main.outb")
print(list(df.columns))      # les canaux disponibles (liste de sorties : annexes/lheea/practicals/OutListParameters.xlsx)
print(unites["RotSpeed"])    # l'unité d'un canal
print(len(df), df["Time"].iloc[-1])
```

**Vous devez voir** : la liste des canaux (`Time`, `Wind1VelX`, `RotSpeed`, `BldPitch1`, `TwrBsMyt`, …), une unité par
canal (`RotSpeed` en tr/min, `TwrBsMyt` en kN·m), le nombre de pas et la durée simulée. Un `.outb` absent veut dire que
le cas n'a pas tourné : lisez la fin de `run.log` du cas.

## 2. Choisir et justifier `t_transitoire`

Le début d'une simulation n'est pas de la physique : le rotor part de l'arrêt. **Regardez la courbe, puis choisissez, puis
écrivez la raison — dans cet ordre.**

```python
import matplotlib.pyplot as plt
df.plot(x="Time", y="RotSpeed"); plt.show()
```

Repérez l'instant où `RotSpeed` cesse d'évoluer systématiquement. Si vous voulez un critère écrit à l'avance plutôt qu'un
coup d'œil, `debut_regime` l'applique tel que vous le donnez (il ne dit pas que le régime est « le bon ») :

```python
t0 = lire.debut_regime(df, nominal=<vitesse de référence, tr/min>, tol_rel=<tolérance relative>,
                       stab_pas=<variation de pas admise, degrés>, duree=<durée de stabilité, s>)
print(t0)    # None si aucun instant ne convient (calcul trop court, ou critère jamais satisfait)
```

**Vous devez voir** un instant (en s), ou `None` : dans ce cas, c'est le critère ou la durée du calcul qu'il faut revoir,
pas la fonction. Écrivez `t_transitoire` **et sa raison** dans votre rendu.

## 3. Statistiques

```python
canaux = ["RotSpeed", "TwrBsMyt"]
print(lire.statistiques(df, canaux, t_transitoire=<votre valeur, en s>))
print(lire.statistiques(df, canaux, t_transitoire=0))     # pour mesurer ce que le transitoire change
```

`statistiques` **refuse** de tourner sans `t_transitoire` : c'est voulu. **Vous devez voir** un tableau (moyenne,
écart-type, min, max, nombre de points) par canal. Sans transitoire écarté, la moyenne est tirée vers les conditions
initiales et l'écart-type est gonflé : l'écart entre les deux tableaux mesure ce que vous évitez en écartant le début.
L'écart-type est celui de la population (dénominateur `N`).

**Ce que ces statistiques ne disent pas** : sur une seule réalisation de vent turbulent, une moyenne n'est pas la moyenne
du processus, et un maximum est le maximum *de cette réalisation*, pas un extrême de dimensionnement.

## 4. Figures à la charte

Toute figure porte sa **provenance** (`cas`, `modele`, `etat`), incrustée en pied : une figure sans provenance est
refusée.

```python
from s9gm import visu

fig = visu.tracer_series(df, ["RotSpeed", "TwrBsMyt"], cas="F01", modele="fixe",
                         etat="rejoué le JJ/MM", t_transitoire=<votre valeur>)
fig.savefig("results/F01_series.png", dpi=150, facecolor="white")
```

**Vous devez voir** : un panneau par canal, temps partagé, la zone de transitoire teintée (on *voit* ce que les
statistiques ignorent), la ligne de provenance en bas. Pour comparer plusieurs cas sur un canal :
`visu.tracer_statistiques({"F03": st3, "F04": st4}, "RotSpeed", modele="fixe", etat="…")` (un cas par barre : moyenne,
± écart-type, min–max) ; pour des courbes y(x) superposées (main / OpenFAST / valeurs publiées),
`visu.tracer_courbes(...)`. Entre 1 et 6 canaux ou panneaux par figure. Enregistrez avec `fig.savefig` sous `results/` :
`visu.enregistrer` est réservé aux figures de référence du dépôt (elles passent par un registre).

## 5. Spectre d'un canal

`s9gm` n'a pas de fonction spectre : on prend celle de SciPy, déjà dans l'environnement, après avoir écarté le
transitoire.

```python
import numpy as np
from scipy.signal import welch

t0 = <votre valeur>
y = df.loc[df["Time"] >= t0, "RootMyb1"].to_numpy(dtype=float)
dt = float(np.median(np.diff(df["Time"])))
f, P = welch(y - y.mean(), fs=1 / dt, nperseg=512)
plt.semilogy(f, P); plt.xlabel("f (Hz)"); plt.ylabel("densité spectrale"); plt.show()
```

**Vous devez voir** un pic à la fréquence de rotation 1P (`RotSpeed / 60`, en Hz) ; la tour, elle, montre 3P. Le choix de
`nperseg` fixe la résolution en fréquence : à justifier si vous le changez.

## 6. Fatigue : rainflow, S-N, Miner, DEL

Le module `s9gm/fatigue.py` est un **squelette** : il fournit la lecture d'une série (`lire_serie`), la liste des pics et
creux (`inversions`), la courbe S-N (`CourbeSN`) et la vérification du facteur de sécurité (`dff_verif`). **Quatre
fonctions sont à écrire par vous en phase 3** : `rainflow`, `miner`, `del_court_terme`, `del_long_terme`
(formules : lexique de l'[`ENONCE.md`](../ENONCE.md), section 7). Toutes les grandeurs de contrainte y sont des
**étendues** `Δσ = σmax − σmin` (deux fois l'amplitude), jamais des amplitudes.

Comme `s9gm/` est suivi par git, **vous complétez une copie**, sous `results/mon_s9gm/` (créée par une commande, jamais écrasée) :

```bash
s9gm copie fatigue                   # crée results/mon_s9gm/fatigue.py (les quatre trous)
# complétez results/mon_s9gm/fatigue.py (les fonctions qui lèvent NotImplementedError)
s9gm tester fatigue --squelette      # avant de commencer : les tests des trous sont « xfailed »
s9gm tester fatigue                  # votre autocontrôle : ils doivent passer
```

**Vous devez voir** : tant que les quatre trous ne sont pas complétés, les tests qui les appellent échouent
(`NotImplementedError`) ; une fois complétés, ils passent. C'est votre autocontrôle avant de déclarer le DEL juste.

La chaîne, sur un cas de votre LCT :

```python
from s9gm import ma_copie

fatigue = ma_copie("fatigue")        # VOTRE copie, rechargée depuis le fichier à chaque appel
serie = fatigue.lire_serie("results/phase3/<votre cas>/main.outb", "TwrBsMyt", t_transitoire=<votre valeur>)
pics = fatigue.inversions(serie)           # fournie
# cycles = fatigue.rainflow(serie)          # à écrire : DataFrame etendue, moyenne, compte (1 ou 0,5)
# Se = fatigue.del_court_terme(...)         # à écrire
# Set = fatigue.del_long_terme(Se_j, O_j, m)  # à écrire : les O_j de VOTRE LCT, de somme égale à 1
```

Passez d'abord du moment à la contrainte (aire, inertie de la section) : c'est le point 2 de la
[phase 3](../seances/phase3/README.md). Un écart entre votre DEL et celui de l'outil d'`openfast_toolbox` doit être
expliqué.

## 7. Animation

Animer un calcul (rotor qui tourne, tour, surface libre) est décrit à part : [`ANIMER.md`](ANIMER.md). Une animation
repère un mouvement incohérent ; ce n'est pas une validation du modèle.

## 8. Les autres façons, devenues annexes historiques

Un autre outil existe encore dans le dépôt, **hors du chemin principal** : les scripts MATLAB `post_process.m` du
tutoriel d'origine (`annexes/lheea/0*/3_Exploitation/`). Il est conservé pour mémoire ; aucune consigne ne le demande.

## Symptômes courants

| Symptôme | Cause | Geste |
|---|---|---|
| `ModuleNotFoundError: No module named 's9gm'` | environnement non activé, ou paquet non installé | `micromamba activate s9gm-fowt`, puis `s9gm doctor` (il donne la commande exacte) |
| `ValueError: t_transitoire est obligatoire` | `t_transitoire=None` | regarder la courbe, choisir une valeur (0 seulement si vous l'assumez) |
| `KeyError: canal inconnu` | nom de canal absent de la sortie | `print(list(df.columns))` ; la liste dépend de l'`OutList` du cas |
| `ValueError: provenance incomplète` | `cas`, `modele` ou `etat` vide | les trois sont obligatoires |
| `NotImplementedError: trou : …` | fonction de `fatigue` pas encore écrite | complétez votre copie sous `results/mon_s9gm/` (`s9gm copie fatigue` la crée) |
| `FileNotFoundError` sur un `.outb` | le cas n'a pas tourné, ou mauvais dossier | `bash cas/run_cas.sh <cas>`, puis lisez `run.log` |
