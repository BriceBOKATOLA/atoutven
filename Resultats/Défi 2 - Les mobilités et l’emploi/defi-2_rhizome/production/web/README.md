# EcloWork — interface du récit

Application de storytelling en français pour le projet de l’équipe Rhizome. Next.js, TypeScript et CSS natif. Aucun backend et aucun service externe ne sont nécessaires.

## Démarrage

Prérequis pour le développement, les tests et l’export : Node.js 22.18 ou plus récent dans la branche 22, ou Node.js 24 ou plus récent, et npm. Le contrat `engines.node` est `^22.18.0 || >=24.0.0`. Depuis la racine du projet :

```sh
cd production/web
npm install
npm run dev
```

Ouvrir http://localhost:3000.

## Vérification et export statique

Les scripts ESLint et Prettier sont configurés. Leurs dépendances restent à installer : l'accès à `registry.npmjs.org` était bloqué dans l'environnement de préparation. Depuis `production/web`, lancer une fois :

```sh
npm install --save-dev --save-exact eslint@9 eslint-config-next@16.4.6 eslint-config-prettier@10 prettier@3.10.1
```

Cette commande met à jour `package.json` et `package-lock.json`. Les scripts ci-dessous fonctionnent après cette installation :

```sh
npm run lint
npm run format:check
```

ESLint recherche les problèmes de code avec les règles Next.js, React et TypeScript. Prettier vérifie le format des fichiers. Ces vérifications n'ont pas pu être exécutées dans l'environnement de préparation. Elles peuvent signaler des problèmes déjà présents.

Pour appliquer les corrections automatiques, utiliser `npm run lint:fix`. Pour reformater les fichiers, utiliser `npm run format`. Ces commandes modifient les fichiers. Vérifier les différences avant de les conserver. Pour limiter le formatage à un fichier, utiliser par exemple `npm exec -- prettier --write components/Brand.tsx`.

Les configurations suivent les [instructions ESLint de Next.js](https://nextjs.org/docs/app/api-reference/config/eslint) et les [instructions d'installation de Prettier](https://prettier.io/docs/install). Elles excluent uniquement les fichiers générés. Aucun formatage global n'a été appliqué lors de leur ajout.

```sh
npm run typecheck
npm run build
```

Les tests du graphique 2 nécessitent Node.js 22.18 ou plus récent :

```sh
node --test tests/graphique-2/*.test.mjs
```

L’export statique est produit dans `out/`. Pour le consulter localement :

```sh
python3 -m http.server 3000 --directory out
```

`next start` ne sert pas l’export statique ; utiliser le serveur de fichiers ci-dessus ou un hébergement statique.

## Structure

- `app/(story)/page.tsx` : récit et textes de contexte, fondés sur `../docs/visualisation.md`.
- `app/(story)/globals.css` : palette, typographie système, styles responsives, focus et mouvement réduit.
- `components/NetworkMap.tsx` et `public/data/rail-network.json` : carte interactive du réseau et données utilisées pour sa légende et ses chiffres clés.
- `app/(graphique-2)` et `app/(graphique-3)` : sources des deux visualisations, intégrées directement au récit. Les données des graphiques 2 et 3 sont respectivement dans `public/data/jobseekers-employment-zones.json` et `public/data/employment-centers-departments.json`. Les graphiques utilisent les polices système et la dépendance npm Highcharts. Leurs styles utilisent `@scope` et les requêtes de conteneur CSS ; un navigateur moderne compatible est nécessaire.
- `components/StoryNavigation.tsx` : ancres natives et indication du chapitre en cours. Le récit et la navigation restent lisibles sans JavaScript.
- `components/Brand.tsx` : mot-symbole typographique et éléments de marque.

Les [spécifications du site](docs/specifications.md) décrivent les vues et leurs limites. Le [catalogue des données web](docs/donnees.md) distingue les instantanés utilisés des sources nécessaires à leur reproduction.

Les contenus restent descriptifs. La desserte d’une commune ne mesure pas un trajet réel et ne prouve pas l’effet d’une ouverture sur l’emploi. Les champs, périodes et précautions de chaque indicateur doivent rester visibles lors de l’intégration.

## Direction visuelle

Palette du support : bleu sourd, rose pâle, fond blanc cassé, prune et vert clair. Le motif de lignes et de stations évoque les transports sans représenter de données géographiques. Les polices système évitent tout chargement distant.
