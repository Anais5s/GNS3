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

Cette méthode est donc facile à déployer, elle utilise le large panel d'adresses IPv6 disponibles et rend la supervision du réseau plus simple.

Communities:
Pour la route map out appliquee sur les peer et provider on a fait un deny PEER et deny PROVIDER + permit le reste (pour propager le prefixe de notre propre AS).
On aurait voulu faire un permit CLIENT, permit PREFIX (prefixe-list avec le prefixe de notre AS) + deny le reste mais il y a eu des erreurs que nous n'avons pas su regler.
