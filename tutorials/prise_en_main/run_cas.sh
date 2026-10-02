#!/usr/bin/env bash
# Lance un cas (ou tous) du tutoriel de prise en main.
# Usage :
#   bash run_cas.sh F01          # un seul cas
#   bash run_cas.sh F01 F02 D00  # plusieurs cas
#   bash run_cas.sh all          # tous les cas presents (dossiers F* et D*)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v openfast &>/dev/null; then
  echo "ERREUR : openfast introuvable. Avez-vous fait 'micromamba activate s9gm-fowt' ?" >&2
  exit 1
fi

if [ ! -f "$HERE/../../models/oc4_rtest/5MW_Baseline/ServoData/DISCON.so" ]; then
  echo "ERREUR : le controleur DISCON n'est pas compile." >&2
  echo "Lancez d'abord, depuis la racine du depot : bash scripts/build_discon.sh" >&2
  exit 1
fi

CASES=("$@")
if [ "${CASES[0]:-}" = "all" ]; then
  CASES=()
  for d in "$HERE"/[FD][0-9][0-9]; do
    [ -d "$d" ] && CASES+=("$(basename "$d")")
  done
fi
if [ ${#CASES[@]} -eq 0 ]; then
  echo "Usage : bash run_cas.sh <cas1> [cas2 ...] | all" >&2
  exit 1
fi

for cas in "${CASES[@]}"; do
  dir="$HERE/$cas"
  if [ ! -d "$dir" ]; then
    echo "Cas inconnu : $cas (dossier $dir absent)" >&2
    continue
  fi
  echo "=== $cas ==="
  t0=$(date +%s)
  ( cd "$dir" && openfast main.fst > run.log 2>&1 )
  rc=$?
  t1=$(date +%s)
  if [ $rc -eq 0 ]; then
    echo "  OK en $((t1-t0)) s -> $dir/main.outb"
  else
    echo "  ECHEC (voir $dir/run.log)"
  fi
done
