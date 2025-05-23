# import

import tkinter as tk
from tkinter import simpledialog
from datetime import datetime
import random as rd
import json
import os

# grille

timer_id = None 
row = 9
column = 9
grille = [[0 for col in range(column)] for ligne in range(row)]

erreurs = 0
duree = 0

def num_valide(num, r, c):
    for i in range(9):
        if grille[r][i] == num or grille[i][c] == num:
            return False
    start_row, start_col = 3 * (r // 3), 3 * (c // 3)
    for i in range(3):
        for j in range(3):
            if grille[start_row + i][start_col + j] == num:
                return False
    return True

def solve(r=0, c=0):
    if r == 9:
        return True
    if c == 9:
        return solve(r + 1, 0)
    nums = list(range(1, 10))
    rd.shuffle(nums)
    for num in nums:
        if num_valide(num, r, c):
            grille[r][c] = num
            if solve(r, c + 1):
                return True
            grille[r][c] = 0
    return False

def copier_grille(g):
    return [row[:] for row in g]

def enlever_nombres(grille):
    positions = [(i, j) for i in range(9) for j in range(9)]
    rd.shuffle(positions)

    tableau = copier_grille(grille)
    num_to_remove = 40

    for i in range(num_to_remove):
        r, c = positions[i]
        tableau[r][c] = 0

    return tableau

solve()
solution=copier_grille(grille)
tableau=enlever_nombres(grille)

def creation_grille():
    global entries, entry
    case_taille = 50
    entries = []

    space = 5

    def validate_input(value):
        return value == "" or (value.isdigit() and len(value) == 1 and value != "0")

    valid_com = window.register(validate_input)

    for row in range(9):
        y_space = row * case_taille + (row // 3) * space
        row_entries = []
        for col in range(9):
            x_space = col * case_taille + (col // 3) * space
            x = 2 + x_space + case_taille / 2
            y = 2 + y_space + case_taille / 2

            entry = tk.Entry(window, justify="center", font=("Tekton Pro", 20),
                             fg='black', bg="#f2f2f2", validate="key", validatecommand=(valid_com, "%P"))

            canva.create_window(x, y, window=entry, width=case_taille, height=case_taille)
            row_entries.append(entry)

            if tableau[row][col] != 0:
                entry.insert(tk.END, str(tableau[row][col]))
                entry.config(state="readonly")

                entry.bind("<Button-1>", lambda e, val=tableau[row][col]: highlight_same_numbers(val))

            else:
                entry.bind("<FocusOut>", lambda e, r=row, c=col: check_entry(e, r, c))
                entry.config(fg="#03254c")
                entry.bind("<FocusIn>", lambda e, r=row, c=col: update_focus(r, c))
                entry.bind("<Button-1>", lambda e, r=row, c=col: on_click_editable(e, r, c))

        entries.append(row_entries)

def update_focus(r, c):
    global r1, c1
    r1 = r
    c1 = c

def check_entry(event, r, c):
    entries[r][c].config(bg="#f2f2f2", fg="#03254c", font=("Tekton Pro", 20))
    user_input = event.widget.get()
    if user_input.isdigit() and 1 <= int(user_input) <= 9:
        if int(user_input) != solution[r][c]:
            increment_erreurs()
            entries[r][c].config(bg="#F75C5C", fg="#f2f2f2", font=("Tekton Pro", 20, "bold"))
    fin_du_jeu()

def highlight_same_numbers(chiffre):
    for r in range(9):
        for c in range(9):
            val = entries[r][c].get()
            if val == str(chiffre):
                entries[r][c].config(highlightthickness=2, highlightbackground="#03254c")
            else:
                entries[r][c].config(highlightthickness=0)

def on_click_editable(event, r, c):
    val = entries[r][c].get()
    if val.isdigit():
        highlight_same_numbers(val)
    else:
        highlight_same_numbers(None)

# "paramètres de la grille" : erreurs, aides, temps

def increment_erreurs():
    global erreurs
    erreurs += 1
    erreur_label.config(text=f"fautes: {erreurs}")

def aide():
    global r1, c1
    entries[r1][c1].insert(tk.END, str(solution[r1][c1]))
    entries[r1][c1].config(bg="#fccf55", fg="#03254c", font=("Tekton Pro", 20, "bold"))

def format_timer(time: int):
    h = time // 3600
    m = (time % 3600) // 60
    s = (time % 3600) % 60
    return f"{h}:{m:0>2}:{s:0>2}"

def update_timer():
    global duree, timer_id
    duree += 1
    timer_label.config(text=format_timer(duree))
    timer_id = window.after(1000, update_timer)

def stop_timer():
    global timer_id
    if timer_id is not None:
        window.after_cancel(timer_id)
        timer_id = None

# re-générer

def reset_grille():
    global tableau, duree, erreurs
    stop_timer()
    duree = 0
    erreurs = 0

    solve()
    copier_grille(grille)
    tableau = enlever_nombres(grille)

    for row in range(9):
        for col in range(9):
            entries[row][col].config(state="normal", bg="#f2f2f2", fg="#03254c")
            entries[row][col].delete(0, tk.END)
            if tableau[row][col] != 0:
                entries[row][col].insert(tk.END, str(tableau[row][col]))
                entries[row][col].config(state="readonly")

    erreur_label.config(text="fautes: 0")
    timer_label.config(text="0:00:00")

    parametre.destroy()
    update_timer()

def reset_game():
    global duree, erreurs
    duree = 0
    erreurs = 0
    timer_label.config(text="0:00:00")
    erreur_label.config(text="Erreurs: 0")
    reset_grille()

# fin

def fin_du_jeu():
    for r in range(9):
        for c in range(9):
            if tableau[r][c] == 0:
                val = entries[r][c].get()
                if not val.isdigit() or int(val) != solution[r][c]:
                    return False
    message_final()
    return True

def message_final():
    global final
    
    final = tk.Canvas(window, width=350, height=275, bg='#005f63', highlightthickness=0)
    final.place(relx=0.5, rely=0.5, anchor="center")

    msg = f"🎉 Bravo !\nVous avez terminé\n avec {erreurs} faute(s) en {format_timer(duree)}"
    message = tk.Label(final, text=msg, font=("Tekton Pro", 14, "bold"), fg="#f2f2f2", bg="#005f63", justify="center")

    menu_button = tk.Button(final, text="Menu", font=("Tekton Pro", 15, "bold"), command=menu_bouton,
                          bg="#005f63", fg="#f2f2f2", activebackground="#005f63", activeforeground="#f2f2f2", borderwidth=0)
    sauvegarde_grille=tk.Button(final,text="Sauvegarder",font=("Tekton Pro", 15, "bold"), command=sauvegarder_grille,
                                  bg="#005f63", fg="#f2f2f2", activebackground="#005f63", activeforeground="#f2f2f2", borderwidth=0)
    
    message.place(relx= 0.5, rely=0.15, anchor="n")
    sauvegarde_grille.place(relx=0.5,rely=0.55,anchor="n")
    menu_button.place(relx=0.5, rely=0.7, anchor="n")

# sauvegarder

def sauvegarder_grille():
    nom = simpledialog.askstring("Nom de la sauvegarde", "Choisissez un nom pour la sauvegarde :")
    if not nom:
        return
    
    if not os.path.exists("saves"):
        os.makedirs("saves")

    nom_fichier = f"saves/{nom}.json"

    etat = {
        "cases": [],
        "solution": solution,
        "erreurs": erreurs,
        "duree": duree
    }

    for row in entries:
        ligne = []
        for entry in row:
            val = entry.get()
            couleur = entry.cget("bg")
            ligne.append({"val": val, "bg": couleur})
        etat["cases"].append(ligne)

    with open(nom_fichier, "w") as fichier:
        json.dump(etat, fichier)

def charger_sauvegarde():
    if not os.path.exists("saves"):
        return
    
    fichiers = os.listdir("saves")
    fichiers = [f for f in fichiers if f.endswith(".json")]

    if not fichiers:
        return
    
    # Demander à l'utilisateur de choisir dans une liste
    nom = simpledialog.askstring("Charger une sauvegarde", "Nom du fichier à charger :\n" + "\n".join(fichiers))
    if not nom:
        return
    if not nom.endswith(".json"):
        nom += ".json"
    
    chemin = os.path.join("saves", nom)

    if not os.path.exists(chemin):
        print("Fichier introuvable.")
        return

    with open(chemin, "r") as fichier:
        etat = json.load(fichier)
        charger_donnees(etat)

def charger_donnees(etat):
    global erreurs, duree, solution
    erreurs = etat["erreurs"]
    duree = etat["duree"]
    solution = etat["solution"]

    erreur_label.config(text=f"fautes: {erreurs}")
    timer_label.config(text=format_timer(duree))

    for i in range(9):
        for j in range(9):
            entry = entries[i][j]
            entry.config(state="normal")
            entry.delete(0, tk.END)
            case = etat["cases"][i][j]
            val = case["val"]
            couleur = case["bg"]

            if val != "":
                entry.insert(0, val)
            entry.config(bg=couleur)

            if val != "" and couleur == "#f2f2f2":
                entry.config(state="readonly")

    update_timer()

# généralisation du jeu

def menu_bouton():
    global final
    final.destroy()
    menu()

def menu():
    global parametre
    
    parametre = tk.Canvas(window, width=300, height=400, bg='#005f63', highlightthickness=0)
    parametre.place(relx=0.5, rely=0.5, anchor="center")

    nouvelle_grille = tk.Button(parametre, text="Nouvelle grille", font=("Tekton Pro", "15", "bold"), borderwidth=0,command=reset_grille,
                       bg="#005f63", fg="#f2f2f2", activebackground= "#005f63", activeforeground="#f2f2f2")
    sauvegarde=tk.Button(parametre,text="Sauvegarder l'état de la grille",font=("Tekton Pro","15","bold"), borderwidth=0,
                              command=sauvegarder_grille,bg="#005f63", fg="#f2f2f2", activebackground= "#005f63", activeforeground="#f2f2f2")
    ancienne_grille=tk.Button(parametre,text="Continuer une ancienne grille",font=("Tekton Pro","15","bold"), borderwidth=0,
                              command=charger_sauvegarde,bg="#005f63", fg="#f2f2f2", activebackground= "#005f63", activeforeground="#f2f2f2")
    fermer_menu=tk.Button(parametre,text="Fermer le menu", font=("Tekton Pro","15","bold"), borderwidth=0,
                          command=parametre.destroy,bg="#005f63", fg="#f2f2f2", activebackground= "#005f63", activeforeground="#f2f2f2")
    quitter = tk.Button(parametre, text="Quitter", font=("Tekton Pro", "15", "bold"), borderwidth=0, command=premiere_page,
                        bg="#005f63", fg="#f2f2f2", activebackground= "#005f63", activeforeground="#f2f2f2")

    nouvelle_grille.place(relx=0.5, rely=0.2, anchor="center")
    sauvegarde.place(relx=0.5,rely=0.35,anchor="center")
    ancienne_grille.place(relx=0.5,rely=0.5,anchor="center")
    fermer_menu.place(relx=0.5,rely=0.65,anchor="center")
    quitter.place(relx=0.5, rely=0.8, anchor="center")

def premiere_page():
    window.geometry("550x750")
    window.minsize(480, 360)
    window.config(background='#047274')
    window.iconbitmap("tools/logo.ico")

    global canva, sudoku_titre, rules, astuce, version, goodluck, play_button

    canva = tk.Canvas(window, width=460, height=650, bg='#f2f2f2')

    sudoku_titre = tk.Label(canva, text="SUDOKU", font=("Tekton Pro", "50", "bold"), fg="#047274")
    goodluck = tk.Label(canva, text="Bonne chance!", font=("Tekton Pro", "15", "bold"), fg="#047274")

    regles = "Le but du jeu est de remplir des cases\n avec des chiffres" \
             " allant de 1 à 9 en veillant\n toujours à ce qu'un même chiffre ne figure\n" \
             "qu'une seule fois par colonne, par ligne,\n et par carré de neuf cases 9x9."

    rules = tk.Label(canva, text=regles, font=("Tekton Pro", "15", "bold"), fg="black")

    astuce = tk.Label(canva, text="🎯 Astuce : Utilisez les touches 1 à 9 pour remplir les cases !",
                      font=("Tekton Pro", "10"), fg="black")
    version = tk.Label(canva, text="version 1.5.2", font=("Tekton Pro", "12"), fg="black")

    canva.place(relx=0.5, rely=0.07, anchor="n")
    sudoku_titre.place(relx=0.5, rely=0.2, anchor="center")
    goodluck.place(relx=0.5, rely=0.5, anchor="center")
    rules.place(relx=0.5, rely=0.65, anchor="center")
    astuce.place(relx=0.5, rely=0.8, anchor="center")
    version.place(relx=0.5, rely=0.9, anchor="center")

    play = tk.PhotoImage(file="tools/play.png")
    play_button = tk.Button(window, image=play, command=deuxieme_page, borderwidth=0)
    play_button.image = play
    play_button.place(relx=0.5, rely=0.39, anchor="center")

def deuxieme_page():
    sudoku_titre.destroy()
    rules.destroy()
    play_button.destroy()
    astuce.destroy()
    version.destroy()
    goodluck.destroy()

    canva.config(width=460, height=460, bg="#047274")
    canva.place(relx=0.5, rely=0.2, anchor="n")

    global timer_label, duree, erreur_label
    duree = 0
    erreur_label = tk.Label(window, text="fautes: 0", font=("Tekton Pro", 16), bg="#047274", fg="#f2f2f2")
    erreur_label.place(relx=0.5, rely=0.91, anchor="center")

    timer_label = tk.Label(window, text="0:00:00", font=("Tekton Pro", 16), bg="#047274", fg="#f2f2f2")
    timer_label.place(relx=0.5, rely=0.11, anchor="center")

    aideP = tk.PhotoImage(file="tools/hint.png")
    aideP_button = tk.Button(window, image=aideP, borderwidth=0, command=aide)
    aideP_button.image = aideP
    aideP_button.place(relx=0.2, rely=0.08)

    menuP = tk.PhotoImage(file="tools/menu.png")
    menuP_button = tk.Button(window, image=menuP, borderwidth=0, command=menu)
    menuP_button.image = menuP
    menuP_button.place(relx=0.12, rely=0.08)

    stop_timer()
    update_timer()

    creation_grille()

window = tk.Tk()
window.title("Sudoku")
window.resizable(False, False)

premiere_page()

window.mainloop()