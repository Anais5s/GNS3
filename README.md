# GNS3
Projet GNS3

## Plan d'adressage
Préfixe IPv6 :
 - En bout en bout : 2001:X:Y::Z/64
 - Anticipation (pas développé dans le code) : Avec un switch : 2001:S:S::Z/64
 - Adresse loopback : 2001:FF::Z/128

Légende :
- X : nom du routeur le plus petit
- Y : nom du routeur connecté à Y
- Z : numéro du routeur
- S : numéro du switch

Avec cette méthode, on peut :
- Connecter 9999 routeurs et les connecter entre eux de bout à bout
- Connecter 9999 switch pour connecter plusieurs routeurs entre eux

Cette méthode est donc facile à déployer, elle rend la supervision du réseau plus simple. En revanche, elle utilise un large panel d'adresses IPv6, pas nécessairement attribuées aux opérateurs.
