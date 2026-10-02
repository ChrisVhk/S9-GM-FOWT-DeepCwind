#!/usr/bin/env bash
# Installe l'environnement du cours, SANS DROITS ADMINISTRATEUR (tout reste dans $HOME).
# Idempotent : peut etre relance sans risque.
set -euo pipefail

if ! command -v micromamba &>/dev/null; then
  echo "Installation de micromamba (dans ~/.local, pas besoin de sudo)..."
  "${SHELL}" <(curl -L micro.mamba.pm/install.sh)
  export MAMBA_EXE="$HOME/.local/bin/micromamba"
  export MAMBA_ROOT_PREFIX="$HOME/micromamba"
fi
export MAMBA_EXE="${MAMBA_EXE:-$HOME/.local/bin/micromamba}"
export MAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-$HOME/micromamba}"
eval "$("$MAMBA_EXE" shell hook --shell bash --root-prefix "$MAMBA_ROOT_PREFIX")"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Creation de l'environnement s9gm-fowt (depuis $HERE/environment.yml)..."
micromamba create -y -f "$HERE/environment.yml"

echo
echo "Verification :"
micromamba run -n s9gm-fowt openfast -v | grep -i "OpenFAST-v" || {
  echo "ERREUR : openfast -v n'affiche pas la version attendue." >&2
  exit 1
}

echo
echo "Installation terminee. Pour l'utiliser a chaque nouvelle session :"
echo "  micromamba activate s9gm-fowt"
echo
echo "Puis, a chaque fois (le controleur n'est jamais suivi par git) :"
echo "  bash scripts/build_discon.sh"
