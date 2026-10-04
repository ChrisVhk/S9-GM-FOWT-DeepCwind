#!/usr/bin/env bash
# Recupere libdiscon.so (controleur ROSCO, conda-forge, licence Apache-2.0) pour le modele
# models/iea15_monopile/. Meme principe que build_discon.sh : un .so est un binaire, jamais
# suivi dans ce depot (.gitignore: *.so) ; chacun le reconstruit sur sa machine.
#
# On installe `rosco` dans un environnement SEPARE (--no-deps : on ne veut que la bibliotheque,
# pas son Python) pour ne pas toucher a s9gm-fowt (openfast=5.0.0 epingle), puis on copie
# libdiscon.so a l'endroit que lit ServoDyn (models/iea15_monopile/ServoData/).
#
# Version epinglee (2.10.6) : c'est celle avec laquelle les resultats livres ont ete produits.
# Non teste sur une machine vierge (le .so dependrait de libgfortran du systeme).
#
# Usage : depuis la racine du depot, apres micromamba (aucune activation requise) :
#   bash scripts/installer_rosco.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$HERE/models/iea15_monopile/ServoData"
MM="${MAMBA_EXE:-$(command -v micromamba || true)}"
if [ -z "$MM" ]; then
  echo "ERREUR : micromamba introuvable (voir README.md, installation)." >&2
  exit 1
fi
ENV_NAME="s9gm-rosco"
"$MM" create -y -q -n "$ENV_NAME" -c conda-forge rosco=2.10.6 --no-deps
PREFIX="$("$MM" env list --json | python3 -c "import json,sys; print([p for p in json.load(sys.stdin)['envs'] if p.endswith('/$ENV_NAME')][0])")"
mkdir -p "$OUT_DIR"
cp "$PREFIX/lib/libdiscon.so" "$OUT_DIR/libdiscon.so"
VERSION="$("$MM" list -n "$ENV_NAME" --json | python3 -c "import json,sys; print([p['version'] for p in json.load(sys.stdin)['packages'] if p['name']=='rosco'][0])")"
echo "OK : $OUT_DIR/libdiscon.so (ROSCO $VERSION)"
