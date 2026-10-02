#!/usr/bin/env bash
# Compile les deux controleurs Bladed-DLL (DISCON generique, DISCON_OC3Hywind) depuis leurs
# sources (OpenFAST, tag v5.0.0, licence Apache-2.0 - cf PROVENANCE.md), avec le gfortran
# installe par conda-forge dans l'environnement s9gm-fowt (PAS celui du systeme : c'est celui
# qui garantit l'ABI compatible avec le openfast=5.0.0 de ce meme environnement).
#
# Pourquoi compiler soi-meme : un .so est un binaire compile, jamais suivi dans ce depot (regle
# du cours). Chaque etudiant le reconstruit en quelques secondes, sur sa propre machine.
#
# Usage : depuis la racine du depot, apres avoir active l'environnement :
#   micromamba activate s9gm-fowt
#   bash scripts/build_discon.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$HERE/models/oc4_rtest/5MW_Baseline/ServoData"
OUT_DIR="$SRC_DIR"

if [ -z "${CONDA_PREFIX:-}" ]; then
  echo "ERREUR : aucun environnement conda/micromamba actif." >&2
  echo "Lancez d'abord : micromamba activate s9gm-fowt" >&2
  exit 1
fi

GFORTRAN="$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-gfortran"
if [ ! -x "$GFORTRAN" ]; then
  # nom alternatif selon la plateforme du paquet conda-forge compilers
  GFORTRAN="$(command -v gfortran || true)"
fi
if [ -z "$GFORTRAN" ] || [[ "$GFORTRAN" != "$CONDA_PREFIX"* ]]; then
  echo "ERREUR : gfortran de conda-forge introuvable dans l'environnement actif ($CONDA_PREFIX)." >&2
  echo "Verifiez que 'compilers' (ou 'gfortran') est bien dans environment.yml et installe." >&2
  exit 1
fi
echo "Compilateur utilise : $GFORTRAN"

build_one () {
  local src="$1" out="$2"
  echo "Compilation : $src -> $out"
  "$GFORTRAN" -shared -O2 -fPIC -o "$out" "$src"
  if ! nm -D "$out" | grep -q " T DISCON$"; then
    echo "ERREUR : le symbole DISCON n'est pas exporte par $out" >&2
    exit 1
  fi
  echo "  OK, symbole DISCON verifie."
}

build_one "$SRC_DIR/DISCON/DISCON.F90"             "$OUT_DIR/DISCON.so"
build_one "$SRC_DIR/DISCON_OC3/DISCON_OC3Hywind.F90" "$OUT_DIR/DISCON_OC3Hywind.so"

echo
echo "Termine. Les deux fichiers .so sont dans : $OUT_DIR"
echo "Ils ne sont jamais suivis par git (voir .gitignore) : a refaire apres un 'git clone'."
