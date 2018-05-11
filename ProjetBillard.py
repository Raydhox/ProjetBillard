#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Nom:          Projet billard
# Auteur:       UNG Harry (Terminale-SSI)
# Objectifs:    Reproduire le fonctionnement d'un billard. Tester.
# Date:         28/09/2017 - 11/05/2018
# Licence:      Faites en ce que vous voulez.
#-------------------------------------------------------------------------------

#On import les modules nécessaires
from tkinter import *
import tkinter.filedialog as tkFileDialog
import math, csv

class Table:
    def __init__(self, x, y):
        #On crée une fenêtre tkinter 'fenetre'
        self.fenetre = Tk()
        self.fenetre.title("Projet Billard")

        #On crée un menu
        self.menubar = Menu(self.fenetre)
        self.menubar.add_command(label="Aide ?", command=self.tutoriel)
        self.fenetre.config(menu=self.menubar)

        #On crée un Canvas 'jeu'
        self.canvas = Canvas(self.fenetre, width=x, height=y, bg="DarkGreen")
        self.canvas.pack()

    def tutoriel(self):
        popup = Toplevel()
        popup.title("A propos de Projet Billard")
        tuto = Label(popup, text="Click gauche: change la position de la boule rouge.\n\
Click milieu: change la position de la boule jaune.\n\
Click droit: change la position de la boule blanche.\n\
Entrée: Tirer.\n\
Espace: Tir droit (0°).\n\
Ctrl (droit): change la boule tirée.\n\
Ctrl+S: Sauvegarde les donées du tir dans un *.csv\n\
Les coordonnées en bas à gauche sont en mètres.")
        tuto.pack()

    def afficher(self):
        #Lancement de la fenètre (boucle principale)
        self.fenetre.mainloop()











class Ball:
    def __init__(self, fenetre, canvas, x, y, limx, limy, metre, temps, couleur):
        #Fenêtre et canvas
        self.fenetre = fenetre
        self.canvas = canvas
        #Positions
        self.coordx = x
        self.coordy = y
        #Taille du terrain
        self.limx = limx
        self.limy = limy
        #Vitesse (et composantes)
        self.vitesse = 0
        self.vitx = 0
        self.vity = 0
        #Directions (angle = boule; theta = angle pour viser)
        self.angle = 0
        self.theta = 0
        self.focus = False
        self.dir_x = self.coordx + 20 + 32*math.cos(self.angle)
        self.dir_y = self.coordy + 20 - 32*math.sin(self.angle)
        self.dir = self.canvas.create_line(self.coordx, self.coordy,
                            self.coordx, self.coordy, width=2)
        self.flag = True
        #Le mètre vaut 'metre' px
        self.metre = metre
        #Temps de rafraichissement
        self.temps = temps
        #Pour afficher la trajectoire
        self.couleur = couleur
        self.save = []
        #Pour la sauvegarde des données
        self.savex = []
        self.savey = []
        self.savit = []
        self.sava = []
        #Création et affichage de l'objet
        self.objet = self.canvas.create_oval(self.coordx, self.coordy,
                            self.coordx+30, self.coordy+30, fill=couleur)
        self.centre = self.canvas.create_oval(self.coordx+14, self.coordy+14,
                            self.coordx+16, self.coordy+16, fill='black')

    def test_collision(self):
        #Si la balle cogne un bord (ou la dépasse), elle rebondit
        #... sauf si elle s'est trop enfoncée (and)
        #Et on ralentit (*0.5 (trouvé expérimentalement))
        """Collision boule-bord."""
##        if (self.coordx <= 0) and (self.vitx < 0):
##            self.vitx = - 0.5*self.vitx
##
##        elif (self.coordy <= 0) and (self.vity < 0):
##            self.vity = - 0.5*self.vity
##
##        elif (self.coordx +30 >= self.limx) and (self.vitx > 0):
##            self.vitx = - 0.5*self.vitx
##
##        elif (self.coordy +30 >= self.limy) and (self.vity >0):
##            self.vity = - 0.5*self.vity

        #Changement de la gestion des rebonds sur les bords
        #car plus efficace sur de faible vitesse.
        pi = math.pi
        if (self.coordx <= 0) and (self.vitx < 0):
            self.vitesse = self.vitesse/2
            self.angle = pi - self.angle

        elif (self.coordy <= 0) and (self.vity < 0):
            self.vitesse = self.vitesse/2
            self.angle = 2*pi - self.angle

        elif (self.coordx +30 >= self.limx) and (self.vitx > 0):
            self.vitesse = self.vitesse/2
            self.angle = pi - self.angle

        elif (self.coordy +30 >= self.limy) and (self.vity > 0):
            self.vitesse = self.vitesse/2
            self.angle = 2*pi - self.angle

        """ON TESTE POUR LES COLLISIONS boule-boule!!!"""
        for k in range(len(main.Boules)):
            #Distance avec la boule k
            dist = math.sqrt((self.coordx - main.Boules[k].coordx)**2 +
                        (self.coordy - main.Boules[k].coordy)**2)
            #Si il y a collision <=> distance entre les boules <= 2*rayons
            #(Comme on vérifie pour chaque boule, on le fait dans le cas générale,
            #d'où "dist != 0" <=> "dist"):
            #   Il y aura rebond
            if (dist <= 30) and (dist != 0):
                self.collision(main.Boules[k])
            if (self.flag == False) and (main.Boules[k].flag == False):
                self.collision(main.Boules[k])

    def viser(self, event):
        """Direction sens.==="""
        #Trigo et Pythagore
        adj = event.x - self.coordx
        hypo = math.sqrt((event.x - self.coordx)**2 + (event.y - self.coordy)**2)
        if hypo == 0:
            hypo = 0.01
        angle = math.acos(adj/hypo)
        #Angle obtus ou angle aigus?
        if event.y > self.coordy:
            angle = - angle
        #Calcul des positions du "segment directionnelle"
        self.theta = angle
        self.dir_x = self.coordx + 15 + 32*math.cos(self.theta)
        self.dir_y = self.coordy + 15 - 32*math.sin(self.theta)
        #Affichage
        self.canvas.coords(self.dir, self.coordx+15, self.coordy+15, self.dir_x, self.dir_y)

    def tirer(self, vitesse):
        #On supprime les anciennes trajectoires et données:
        def supprsave(boule):
            count = 0
            for k in range(len(boule.save)):
                count += 1
                self.canvas.delete(self.canvas, boule.save[k])
            boule.save = []
            boule.savex = []
            boule.savey = []
            boule.savit = []
            boule.sava = []
        for k in range(len(main.Boules)):
            supprsave(main.Boules[k])
        #
        for k in range(len(main.Boules)):
            main.Boules[k].flag = True
        #On converit la vitesse en dm/s en px/cs
        #vitesse = entier(dm/s=>m/s=>px/s)
        self.vitesse = int(vitesse/10*self.metre)
        self.angle = self.theta

    def move(self):
        #Ralentissement
        if main.loi.get() == "Coulomb":
            self.ralentissement()
        else:
            self.ralentissement2()
        #Changement des positions
        self.coordx += self.vitx*self.temps/1000
        self.coordy += self.vity*self.temps/1000
        self.test_collision()
        #Il bouge...
        self.canvas.coords(self.objet, self.coordx, self.coordy,
                            self.coordx+30, self.coordy+30)
        self.canvas.coords(self.centre, self.coordx+14, self.coordy+14,
                            self.coordx+16, self.coordy+16)
        #Affichage de la direction de tir
        if self.focus == True:
            #Calcul des positions du "segment directionnelle"
            self.dir_x = self.coordx + 15 + 32*math.cos(self.theta)
            self.dir_y = self.coordy + 15 - 32*math.sin(self.theta)
            #Affichage
            self.canvas.coords(self.dir, self.coordx+15, self.coordy+15,
                                self.dir_x, self.dir_y)
        else:
            self.canvas.coords(self.dir, self.coordx+15, self.coordy+15,
                                self.coordx+15, self.coordy+15)


    def ralentissement(self):
        #Ralentissement (Loi de Coulomb)
        #vitesse(t) = -f*g*t + v0
        #En programmant cela dans une boucle de [delta t] ms,
        #on a une suite définie par récurence:
        #vitesse(t + [delta t]ms) = convertion(-f*g*[delta t], m/s en px/s) + v(t)

        #On récupère le coefficient de frottement f
        #et on calcule le temps delta t
        f = float(main.frottement.get())
        t = self.temps/1000
        #Calcul de la nouvelle vitesse et des ses composantes.
        self.vitesse = (-f*9.81*t)/10*self.metre + self.vitesse
        if self.vitesse < 0:
            self.vitesse = 0
        self.vitx = self.vitesse*math.cos(-self.angle)
        self.vity = self.vitesse*math.sin(-self.angle)

    def ralentissement2(self):
        #Ralentissement (-f*v)
        #vitesse(t + t0) = -f*vitesse(t)/m *t0 + v0
        #On programme cela dans une boucle de 20 ms,
        #mais est-ce-que c'est exact?

        #On récupère le coefficient de frottement f
        #et on calcule le temps delta t
        f = float(main.frottement.get())
        t = self.temps/1000
        #Calcul de la nouvelle vitesse et des ses composantes.
        self.vitesse = -f*self.vitesse/0.169*t + self.vitesse
        if self.vitesse < 0:
            self.vitesse = 0
        self.vitx = self.vitesse*math.cos(-self.angle)
        self.vity = self.vitesse*math.sin(-self.angle)

    def collision(self, boule2):
        #Boule1 = boule de l'objet
        if (self.flag) and (boule2.flag):
            pi = math.pi
            #Pour empêcher qu'il est une collision à l'infini
            self.flag, boule2.flag = False, False
            #Division par zéro
            if boule2.coordx != self.coordx:
                angle = math.atan(abs(boule2.coordy-self.coordy)/abs(boule2.coordx-self.coordx))
            else:
                angle = pi/2
            #Angle déterminé de manière à être sur un repère "classique"
            if boule2.coordx < self.coordx:
                angle = angle + pi/2
            if self.coordy < boule2.coordy:
                angle = -angle
            #Dans le cas où les deux billes sont en mouvement
            #(Non développés)
            vitesse = math.sqrt(self.vitx**2+self.vity**2)
            #Boule2
            boule2.vitesse = math.cos( abs( abs(angle)-abs(self.angle) ) )*vitesse
            boule2.angle = angle
            #Boule1
            self.vitesse = math.sqrt( abs(self.vitesse**2-boule2.vitesse**2) )
            #Directions boule1:
            if (math.cos(self.angle) < 0):
                if(math.cos(boule2.angle + pi/2) < 0):
                        self.angle = boule2.angle + pi/2
                else:
                        self.angle = boule2.angle - pi/2
            else:
                if(math.cos(boule2.angle + pi/2) > 0):
                        self.angle = boule2.angle + pi/2
                else:
                        self.angle = boule2.angle - pi/2
        #Pour gérer les "flags"
        if  math.sqrt((self.coordx - boule2.coordx)**2 + (self.coordy - boule2.coordy)**2) >= 30:
            self.flag, boule2.flag = True, True


    def deplacement(self, event):
        #On déplace la balle au coordonnnées du click...
        #...sauf si elle rentre dans une autre bille
        voixlibre = True
        for k in range(len(main.Boules)):
            if (main.Boules[k].couleur != self.couleur) and\
            ( math.sqrt((event.x-15 - main.Boules[k].coordx)**2 + (event.y-15 - main.Boules[k].coordy)**2) <= 30 ):
                voixlibre = False
        if voixlibre:
            self.coordx = event.x - 15
            self.coordy = event.y - 15











class Simu:
    def __init__(self, dim, temps):
        #terrain = Table de billard
        self.terrain = Table(dim[0], dim[1])
        #Ici, 500 px = 1 mètre
        self.metre = 500
        #Temps entre deux images
        self.temps = temps

        #Billes
        self.Alpha = Ball(self.terrain.fenetre, self.terrain.canvas,
                     250, 250, dim[0], dim[1], self.metre, self.temps, 'red')
        self.Beta = Ball(self.terrain.fenetre, self.terrain.canvas,
                     750, 30, dim[0], dim[1], self.metre, self.temps, 'yellow')
        self.Gamma = Ball(self.terrain.fenetre, self.terrain.canvas,
                     750, 440, dim[0], dim[1], self.metre, self.temps, 'white')
        self.Boules = [self.Alpha, self.Beta, self.Gamma]

        #Note: \t = tab

        #Input vitesse
        self.label = Label(self.terrain.fenetre, text="Vitesse (en dm/s):")
        self.label.pack(side=LEFT)
        self.vitesse = Scale(self.terrain.fenetre, from_=0, to=50,  orient=HORIZONTAL)
        self.vitesse.set(25)
        self.vitesse.pack(side=LEFT)

        #Type frottement
        self.label = Label(self.terrain.fenetre, text="\t Loi de frottement:")
        self.label.pack(side=LEFT)

        self.loi = StringVar(self.terrain.fenetre)
        self.loi.set("Coulomb")
        self.choix = OptionMenu(self.terrain.fenetre, self.loi, "Coulomb", "-k*v")
        self.choix.pack(side=LEFT)

        #Input frottement
        self.label = Label(self.terrain.fenetre, text="\t Coefficient de frottement:")
        self.label.pack(side=LEFT)
        self.frottement = Spinbox(self.terrain.fenetre, width=8, value=0.1875)
        self.frottement.pack(side=LEFT)

        #Positions souris
        self.posx = Label(self.terrain.fenetre, text="\t X:")
        self.posx.pack(side=LEFT)
        self.posy = Label(self.terrain.fenetre, text="; Y:")
        self.posy.pack(side=LEFT)

    def switch(self, event): #Comme la console ;-)
        #Change la boule que l'on tire
        for k in range(0, len(self.Boules)):
            if self.Boules[k].focus:
                self.Boules[k].focus = False
                self.Boules[k-1].focus = True
                break

    def quivise(self, event):
        #Quelle boule on dirige:
        for k in range(len(self.Boules)):
            if self.Boules[k].focus:
                self.Boules[k].viser(event)
        #Affichage des positions
        self.posx.config(text='\t X: '+str(event.x/self.metre) )
        self.posy.config(text='; Y: '+str(event.y/self.metre) )

    def tirdroit(self, event):
        #Angle à 0
        for k in range(len(self.Boules)):
            self.Boules[k].theta = 0
        self.tir(event)

    def tir(self, event):
        #Tir en fonction la vitesse rentrée
        for k in range(len(self.Boules)):
            if self.Boules[k].focus:
                self.Boules[k].tirer(float(self.vitesse.get()))

    def savedata(self, event):
        #Sauvegarde les positions et les vitesses dans un fichier *.csv .
        filename = tkFileDialog.asksaveasfilename(defaultextension='*.csv', filetypes=[('supported', ('*.csv'))])
        with open(filename, 'w', newline='') as fichier:
            file = csv.writer(fichier)
            file.writerow(["Temps [s]", "Xred [m]", "Yred [m]", "Xjaune [m]", "Yjaune [m]", "Xblanc [m]", "Yblanc [m]",
            "Vred [dm/s]", "Vjaune [dm/s]", "Vblanc [dm/s]",
            "Dir(red) [rad]", "Dir(jaune) [rad]", "Dir(blanc) [rad]"])
            t = self.temps/1000
            for k in range(len(self.Alpha.savit)):
                file.writerow([ str(round(k*t, 3)), str(round(self.Alpha.savex[k]/self.metre, 3)), str(round(self.Alpha.savey[k]/self.metre, 3)),
                str(round(self.Beta.savex[k]/self.metre, 3)), str(round(self.Beta.savey[k]/self.metre, 3)),
                str(round(self.Gamma.savex[k]/self.metre, 3)), str(round(self.Gamma.savey[k]/self.metre, 3)),
                str(round(self.Alpha.savit[k], 3)), str(round(self.Beta.savit[k], 3)), str(round(self.Gamma.savit[k], 3)),
                str(round(self.Alpha.sava[k], 3)), str(round(self.Beta.sava[k], 1)), str(round(self.Gamma.sava[k], 1)) ])

    def lancer(self):
        #On contrôle par défaut la boule rouge
        self.Alpha.focus = True

        """Evènements"""
        #Click Gauche qui change le position de le balle Alpha
        self.terrain.canvas.bind('<Button-1>', self.Alpha.deplacement)
        #Click Mileu qui change le position de le balle Beta
        self.terrain.canvas.bind('<Button-2>', self.Beta.deplacement)
        #Click Droit qui change le position de le balle Gama
        self.terrain.canvas.bind('<Button-3>', self.Gamma.deplacement)
        #Mouvement souris = direction
        self.terrain.canvas.bind('<Motion>', self.quivise)
        #Touche ctrl pour changer la boule que l'on tire
        self.terrain.fenetre.bind('<Control_R>', self.switch)
        #Touche entrée pour tirer
        self.terrain.fenetre.bind('<Return>', self.tir)
        #Touche espace pour un tir droit
        self.terrain.fenetre.bind('<space>', self.tirdroit)
        #Touche 'S' majuscule pour enregistrer Alpha.savit
        self.terrain.fenetre.bind('<Control-s>', self.savedata)
        self.terrain.fenetre.bind('<Control-S>', self.savedata)

        #On lance la boucle
        self.boucle()
        #Affichage
        self.terrain.afficher()

    def boucle(self):
        #Mouvement des boules
        for k in range(len(self.Boules)):
            self.Boules[k].move()
        #Pour savoir si les billes sont immobiles...
        sigma = 0
        for k in range(len(self.Boules)):
            sigma += self.Boules[k].vitesse
        #...si elles ne le sont pas, alors on enregistre les données
        for k in range(len(self.Boules)):
            if sigma:
                #Positions
                self.Boules[k].savex.append(self.Boules[k].coordx)
                self.Boules[k].savey.append(self.Boules[k].coordy)
                #Vitesse
                self.Boules[k].savit.append(self.Boules[k].vitesse/self.metre*10)
                #Angle
                self.Boules[k].sava.append(self.Boules[k].angle)
            if sigma and self.Boules[k].vitesse:
                #Marqueur de la trajectoire
                self.Boules[k].save.append(self.Boules[k].canvas.create_oval(self.Boules[k].coordx+13,
                self.Boules[k].coordy+13, self.Boules[k].coordx+17, self.Boules[k].coordy+17, width=0, fill=self.Boules[k].couleur))
        #On répète la boucle tous les self.temps ms
        self.terrain.fenetre.after(self.temps, self.boucle)


if __name__ == '__main__':
    #On lance la simulation qui tourne en boucle.
    #Ici, on peut changer la taille du terrain (L*l, en px)
    #et le taux de rafraichissement des images et donc, la précision (en ms).
    #Le billard faisant 2*1 mètres² et pour plus de précision, on a mis 10 ms,
    #mais sur les vieux PC (ceux de mon lycée), mettait au moins 20 ms.
    main = Simu([1000, 500], 10)
    main.lancer()






















