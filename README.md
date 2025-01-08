# GNS3
Projet GNS3

## Plan d'adressage
Préfixe IPv6 :
 - En bout en bout : 2001:X:Y::Z/64
 - Avec un switch : 2001:S:S::Z/64
 - Adresse loopback : 2001::Z/128

Légende :
- X : nom du routeur le plus petit
- Y : nom du routeur connecté à Y
- Z : numéro du routeur
- S : numéro du switch

Avec cette méthode, on peut :
- Brancher 9999 routeurs et les connecter entre eux en bout à bout
- Brancher 9999 switch pour connecter plusieurs routeurs entre eux

Cette méthode est donc facile à déployer, elle utilise le large panel d'adresses IPv6 disponibles et rend la supervision du réseau plus simple.