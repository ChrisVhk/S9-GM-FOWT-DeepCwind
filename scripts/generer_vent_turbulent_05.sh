#!/usr/bin/env bash
# Regenere le champ de vent turbulent du cas 05 (FOWT) avec TurbSim, a partir du fichier
# d'entree .inp d'origine (conserve intact, cf tutorials/lheea/NOTICE).
#
# Pourquoi : le fichier .bts genere (~70 Mo) est gitignore (regle du cours : aucun fichier
# >50 Mo, aucun binaire genere suivi) et n'est donc jamais present apres un git clone. TurbSim
# est fourni par le meme paquet conda-forge qu'OpenFAST (cf env/README.md) : chaque etudiant
# regenere ce fichier chez lui, comme pour le controleur (scripts/build_discon.sh).
#
# Usage : depuis la racine du depot, apres avoir active l'environnement :
#   micromamba activate s9gm-fowt
#   bash scripts/generer_vent_turbulent_05.sh
#
# Duree : quelques minutes (calcul mono-cas, pas de dependance au reste du depot).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WIND_DIR="$HERE/tutorials/lheea/05_FOWT/1_Configuration/Wind"

if [ -z "${CONDA_PREFIX:-}" ]; then
  echo "ERREUR : aucun environnement conda/micromamba actif (lancez 'micromamba activate s9gm-fowt' d'abord)." >&2
  exit 1
fi

if [ -f "$WIND_DIR/turb12mps.bts" ]; then
  echo "Deja present : $WIND_DIR/turb12mps.bts (rien a faire)."
  exit 0
fi

echo "Generation de $WIND_DIR/turb12mps.bts avec TurbSim (quelques minutes)..."
( cd "$WIND_DIR" && turbsim turb12mps.inp )

if [ ! -f "$WIND_DIR/turb12mps.bts" ]; then
  echo "ERREUR : TurbSim n'a pas produit turb12mps.bts." >&2
  exit 1
fi

echo "OK : $WIND_DIR/turb12mps.bts genere."
