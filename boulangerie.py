import streamlit as st
import sqlite3
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Caisse Boulangerie", page_icon="🛒", layout="wide")

# Connexion à la base de données
conn = sqlite3.connect("vente_boulangerie.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        produit TEXT,
        quantite INTEGER,
        prix_unitaire REAL,
        total REAL
    )
""")
conn.commit()

# Produits disponibles
produits = {
    "🥖 Baguette": 100,
    "🥐 Croissant": 300,
    "🍫 Pain au chocolat": 400,
    "🍇 Pain aux raisins": 300,
    "🍞 Pain complet": 150,
    "🍞 Pain de campagne": 300,
    "🍞 Brioche": 300,
    "🌾 Pain aux céréales": 200
}

# Initialisation des variables de session
if "panier" not in st.session_state:
    st.session_state.panier = {}
if "montant_recu" not in st.session_state:
    st.session_state.montant_recu = 0

# 🎨 **Style et Mise en Page**
st.markdown(
    """
    <style>
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        border-radius: 10px;
        padding: 10px;
    }
    .stTable {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 🏠 **Titre principal**
st.title("🛒 Caisse Boulangerie")
st.markdown("**Gérez facilement vos ventes avec une interface intuitive et moderne !**")

# 📌 **Onglets pour la navigation**
tabs = st.tabs(["🛍️ Vente", "📜 Historique des Ventes"])

# ============================== #
# 🎯 **ONGLET 1: Gestion des Ventes** #
# ============================== #
with tabs[0]:
    col1, col2 = st.columns([2, 1])

    # 📦 **Sélection des Produits**
    with col1:
        st.subheader("📦 Sélection des Produits")
        for produit, prix in produits.items():
            quantite = st.number_input(f"{produit} ({prix} FCFA)", min_value=0, max_value=100, value=0, step=1, key=produit)
            if quantite > 0:
                st.session_state.panier[produit] = (quantite, prix)
            elif produit in st.session_state.panier:
                del st.session_state.panier[produit]

    # 🛍️ **Affichage du Panier**
    with col2:
        st.subheader("🛍️ Panier")
        if st.session_state.panier:
            total = 0
            panier_data = []
            for produit, (quantite, prix) in st.session_state.panier.items():
                sous_total = quantite * prix
                total += sous_total
                panier_data.append([produit, quantite, prix, sous_total])

            # Afficher le panier avec un style amélioré
            st.table(panier_data)

            # Affichage du total
            st.markdown(f"### 💰 Total: `{total} FCFA`")

            # Montant reçu et monnaie
            st.session_state.montant_recu = st.number_input("💵 Montant reçu", min_value=0, value=st.session_state.montant_recu, step=100)
            monnaie = st.session_state.montant_recu - total
            if monnaie >= 0:
                st.success(f"💰 Monnaie à rendre: `{monnaie} FCFA`")
            else:
                st.error("❌ Montant insuffisant")

            # Boutons interactifs
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("✅ Valider la vente"):
                    for produit, (quantite, prix) in st.session_state.panier.items():
                        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute("INSERT INTO ventes (date, produit, quantite, prix_unitaire, total) VALUES (?, ?, ?, ?, ?)",
                                       (date, produit, quantite, prix, quantite * prix))
                        conn.commit()
                    st.session_state.panier.clear()
                    st.success("🎉 Vente enregistrée avec succès !")
                    st.experimental_rerun()

            with col_btn2:
                if st.button("🔄 Nouvelle Vente"):
                    st.session_state.panier.clear()
                    st.session_state.montant_recu = 0
                    st.experimental_rerun()

# ==================================== #
# 🏷 **ONGLET 2: Affichage des Ventes** #
# ==================================== #
with tabs[1]:
    st.subheader("📜 Historique des Ventes")

    # Bouton pour afficher les ventes
    if st.button("🔍 Afficher les ventes"):
        cursor.execute("SELECT date, produit, quantite, prix_unitaire, total FROM ventes ORDER BY date DESC")
        ventes = cursor.fetchall()
        if ventes:
            st.dataframe(ventes, columns=["Date", "Produit", "Quantité", "Prix Unitaire", "Total"])
        else:
            st.write("Aucune vente enregistrée.")

# ============================== #
# 🎯 **FIN** #
# ============================== #
