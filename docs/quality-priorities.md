# Second lot — priorites pour Solar Monitoring

Cette PR est empilee sur le lot qualite #1. Elle ne fait pas partie de la
contribution upstream minimale CJNE/pymyenergi#84 et ne doit pas entrer dans la
premiere adoption Solar par inadvertance.

| Priorite | Correction de cette PR | Effet |
| --- | --- | --- |
| P1 | Client HTTP propre a chaque Connection, aclose et contexte async | Fin du client implicite partage ; le client injecte reste propriete de l'appelant. |
| P1 | Statut HTTP traite avant ASN | 429/500/503 ne sont plus presentes comme de faux mauvais identifiants. |
| P1 | Tous les timeouts HTTPX, causes preservees | Solar peut distinguer une indisponibilite d'une erreur de programmation ; aucune commande n'est rejouee automatiquement. |
| P1 | Enums Zappi inconnues | Aucun IndexError ou faux etat provenant d'un index negatif. |
| P1 | Validation minimum-green 0..100 | Rejet avant reseau ; valeurs texte CLI valides toujours acceptees. |
| P2 | Serial avant refresh, flag vhub rafraichi | Etat coherent sans attendre une lecture complete. |
| P2 | Cle energie boost et comparaison Libbi | Correction des lectures/aggregations, pas de nouvelle formule energetique. |
| P2 | CLI unlock et arguments boost manquants | Plus de commande silencieusement ignoree ou IndexError. |

## Responsabilites Solar (PR suivante, pas dans la librairie)

P1 : modes texte conformes au SDK, suppression des appels a des methodes qui
n'existent pas, rejet explicite d'une consigne en watts non supportee, collecte
Zappi independante de Harvi et des horaires boost, echec de collecte visible.
Tests avec le vrai Zappi et seulement la frontiere HTTP simulee.

## Non termine / a qualifier avant changement de comportement

P2 : authentification Cognito entierement non bloquante et renouvellement OAuth
concurrent ; sans impact sur le chemin Digest utilise par Solar. P2 : validation
des contrats des historiques minute/fuseau et des parametres smart-boost avant
modification des URLs. P2 Solar : confirmation par relecture bornee, cycle de vie
HTTP unifie entre API/service et extension de la fenetre de rattrapage de 6h.
Ces points ne sont pas presentes comme corriges. La politique metier de charge,
la causalite des mesures et les garanties de fraicheur de Solar restent en place.
