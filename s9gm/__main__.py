"""Ligne de commande `s9gm` (ou `python -m s9gm`) :

    s9gm doctor                     vérifie votre poste (environnement, version d'OpenFAST, clone, contrôleur…)
    s9gm copie <nom>                crée votre copie de `fatigue`, `ancrage` ou `structure` sous results/mon_s9gm/ (sans jamais écraser)
    s9gm tester <nom> [--squelette] lance les tests du dépôt sur votre copie (ou sur le squelette du dépôt)

Les commandes marchent depuis n'importe quel dossier."""
import sys

AIDE = __doc__


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a or a[0] in ("-h", "--help", "--aide", "aide"):
        print(AIDE)
        return 0
    cmd, reste = a[0], a[1:]
    if cmd == "doctor":
        from . import doctor
        return doctor.main()
    from . import copies
    if cmd == "copie" and len(reste) == 1:
        try:
            f = copies.creer_copie(reste[0])
        except ValueError as e:
            print(e)
            return 2
        n = copies.trous(reste[0])
        print(f"chemin : {f}\ntrous à programmer : {n} (`raise NotImplementedError` dans le fichier)")
        return 0
    if cmd == "tester" and reste and reste[0] != "--squelette":
        try:
            code, sortie = copies.tester(reste[0], squelette="--squelette" in reste[1:])
        except ValueError as e:
            print(e)
            return 2
        print(sortie)
        return code
    print(AIDE)
    return 2


if __name__ == "__main__":
    sys.exit(main())
