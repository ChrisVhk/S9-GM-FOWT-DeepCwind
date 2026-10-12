#!/usr/bin/env bash
# Lance un cas de référence (ou plusieurs, ou tous), SUR UNE COPIE sous results/ : cas/ est suivi par git et n'est jamais
# modifié, les sorties (main.outb, run.log, *.sum...) vivent donc dans results/<cas>/.
# Usage :
#   bash cas/run_cas.sh F01             # copie cas/F01 vers results/F01, puis lance
#   bash cas/run_cas.sh F01 F02 D00     # plusieurs cas
#   bash cas/run_cas.sh all             # tous les cas de référence (dossiers E*, F*, D*)
#   bash cas/run_cas.sh results/F01_essai   # un dossier qui contient un main.fst (le vôtre) : lancé sur place
# La copie est faite directement sous results/ (même profondeur que cas/) : les chemins relatifs du main.fst
# (../../modeles/...) restent valables.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RACINE="$(cd "$HERE/.." && pwd)"

if ! command -v openfast &>/dev/null; then
  echo "ERREUR : openfast introuvable. Avez-vous fait 'micromamba activate s9gm-fowt' ?" >&2
  exit 1
fi

if [ ! -f "$RACINE/modeles/oc4_rtest/5MW_Baseline/ServoData/DISCON.so" ]; then
  echo "ERREUR : le controleur DISCON n'est pas compile." >&2
  echo "Lancez d'abord, depuis la racine du depot : bash scripts/build_discon.sh" >&2
  exit 1
fi

CASES=("$@")
if [ "${CASES[0]:-}" = "all" ]; then
  CASES=()
  for d in "$HERE"/[EFD][0-9][0-9]; do
    [ -d "$d" ] && CASES+=("$(basename "$d")")
  done
fi
if [ ${#CASES[@]} -eq 0 ]; then
  echo "Usage : bash cas/run_cas.sh <cas1> [cas2 ...] | all | <dossier avec main.fst>" >&2
  exit 1
fi

status=0
for cas in "${CASES[@]}"; do
  if [[ "$cas" == */* ]]; then          # un dossier à vous : lancé sur place
    dir="$(cd "$cas" 2>/dev/null && pwd)" || { echo "Dossier inconnu : $cas" >&2; status=1; continue; }
    [ -f "$dir/main.fst" ] || { echo "Pas de main.fst dans $cas" >&2; status=1; continue; }
  else                                   # un cas de référence : copie sous results/
    src="$HERE/$cas"
    if [ ! -d "$src" ]; then
      echo "Cas inconnu : $cas (dossier $src absent)" >&2; status=1; continue
    fi
    mkdir -p "$RACINE/results"
    dir="$RACINE/results/$cas"
    mkdir -p "$dir"
    cp -r "$src"/. "$dir"/
  fi
  echo "=== $cas ==="
  t0=$(date +%s)
  rc=0
  ( cd "$dir" && openfast main.fst > run.log 2>&1 ) || rc=$?
  t1=$(date +%s)
  if [ $rc -eq 0 ]; then
    echo "  OK en $((t1-t0)) s -> $dir/main.outb"
  else
    echo "  ECHEC (voir $dir/run.log)"
    status=1
  fi
done
exit $status
