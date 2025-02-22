a = []
pouce = ["pouce", 2, 2]
indexx = ["index", 5,6]
majeur = ["majeur", 7, 8]
annulaire = ["annulaire", 9, 5]
auriculaire = ["auriculaire", 11, 3]

a.append(pouce)
a.append(indexx)
a.append(majeur)
a.append(annulaire)
a.append(auriculaire)

#trouver x minimum et maximum
xMin = a[0][1]
xMax = a[0][1]
doigtGauche = a[0]
doigtDroite = a[0]
for i in range(0,len(a)):
    if a[i][1] < xMin:
        doigtGauche = a[i]
        xMin = a[i][1]

    if a[i][1] > xMax:
        doigtDroite = a[i]
        xMax = a[i][1]

#trouver le point max et min
yMax = a[0][2]
yMin = a[0][2]
for i in range(0,len(a)):
    if a[i][2] < yMin:
        yMin = a[i][2]

    if a[i][2] > yMax:
        yMax = a[i][2]

print("Doigt le plus à gauche : ", doigtGauche)
print("Doigt le plus à droite : ", doigtDroite)
print("plus haut point: ", yMax)
print("plus bas point : ", yMin)

