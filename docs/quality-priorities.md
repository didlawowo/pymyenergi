# Second lot — priorites pour Solar Monitoring

Cette PR est empilee sur le lot qualite #3. Elle ne fait pas partie de la
contribution upstream minimale CJNE/pymyenergi#83 et ne doit pas entrer dans la
premiere adoption Solar par inadvertance.

## P1 — transport et commandes

**Client HTTP par connexion.** Chaque Connection possede son client implicite
et expose aclose ainsi qu'un contexte async. Un client injecte reste propriete
de l'appelant. Solar devra adapter le cycle de vie de ses connexions avant
d'adopter ce second lot.

**Statuts HTTP et timeouts.** Les erreurs 429/500/503 ne sont plus presentees
comme des erreurs d'identifiants. Tous les timeouts HTTPX conservent leur cause.
Aucune commande n'est rejouee automatiquement.

**Valeurs Zappi inconnues.** Les enums invalides ne produisent plus IndexError
ni faux etat derive d'un index negatif. Le niveau minimum-green est valide entre
0 et 100 avant le reseau ; les valeurs texte CLI valides restent acceptees.

## P2 — coherence des donnees et CLI

Le numero configure est disponible avant refresh. Le flag vhub suit les
nouvelles donnees. L'energie boost utilise la cle produite par l'historique.
La comparaison Libbi corrigee dans le lot minimal #3 est preservee.

STOP actualise le mode local apres succes sans inventer une transition physique.
La CLI execute unlock et rejette les arguments boost manquants avant le reseau.

## Responsabilites Solar — PR #333

Modes texte conformes au SDK, suppression des appels a des methodes absentes,
rejet explicite des consignes en watts non supportees, collecte Zappi
independante de Harvi et des horaires boost, echec de collecte observable.
Les tests utilisent le vrai SDK et simulent uniquement la frontiere HTTP.

## Non termine — suivi Solar #334

Restent a qualifier : authentification Cognito entierement non bloquante,
renouvellement OAuth concurrent, historiques minute et fuseaux, validation
complete des parametres smart-boost. Le chemin Digest utilise par Solar ne
depend pas des identifiants OAuth.

Cote Solar restent la confirmation par relecture bornee, les timestamps de
mesure, le cycle de vie HTTP unifie entre API et service, les autres etats de
branchement et le rattrapage de l'arret de 6h. Ces points ne sont pas presentes
comme corriges. La politique metier de charge et les protections de causalite
et de fraicheur des mesures restent en place.
