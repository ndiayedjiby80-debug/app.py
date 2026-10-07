import streamlit as st
import pandas as pd
import random

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="SenColis - Gestion de Colis",
    layout="wide"
)

# --- TITRE DÉFILANT (De gauche à droite) ---
st.markdown("""
    <style>
    .defilant {
        background-color: #00853F;
        color: #FDEF42;
        padding: 10px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 5px;
        white-space: nowrap;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .defilant span {
        display: inline-block;
        padding-left: 100%;
        animation: defilement 15s linear infinite;
    }
    @keyframes defilement {
        0%   { transform: translate(0, 0); }
        100% { transform: translate(-100%, 0); }
    }
    </style>
    <div class="defilant">
        <span> Bienvenue A KEUR-SODA - La solution logistique et de transport de colis sur tout le territoire sénégalais (Dakar, Thiès, Saint-Louis, Touba, Louga, Ziguinchor...) </span>
    </div>
""", unsafe_allow_html=True)

# --- INITIALISATION DE LA "BASE DE DONNÉES" EN SESSION ---
if "colis_list" not in st.session_state:
    st.session_state.colis_list = []

if "code_recherche" not in st.session_state:
    st.session_state.code_recherche = ""

# --- MENU LATÉRAL ---
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Aller vers :", ["Envoyer un colis", "Suivre un colis", "Espace Livreur / Admin"])

# --- VILLES ET COORDONNÉES GPS ---
coords_villes = {
    "Dakar": {"lat": 14.6928, "lon": -17.4467},
    "Thiès": {"lat": 14.7910, "lon": -16.9259},
    "Mbour": {"lat": 14.4184, "lon": -16.9622},
    "Saint-Louis": {"lat": 16.0179, "lon": -16.4896},
    "Touba": {"lat": 14.8675, "lon": -15.8833},
    "Louga": {"lat": 15.6187, "lon": -16.2244},
    "Ziguinchor": {"lat": 12.5605, "lon": -16.2719}
}

# ==========================================
# 1. ESPACE CLIENT : ENVOYER UN COLIS
# ==========================================
if menu == "Envoyer un colis":
    st.header(" Créer une nouvelle expédition")
    
    with st.form("colis_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            expediteur = st.text_input("Nom de l'expéditeur", placeholder="Ex: MOUSTAPHA BA")
            destinataire = st.text_input("Nom du destinataire", placeholder="Ex: BAYE YORO WADE")
            telephone = st.text_input("Téléphone du destinataire", placeholder="Ex: 77 123 45 67")
            
        with col2:
            depart = st.selectbox("Ville de Départ", list(coords_villes.keys()))
            arrivee = st.selectbox("Ville d'Arrivée", list(coords_villes.keys()))
            poids = st.number_input("Poids du colis (kg)", min_value=0.5, max_value=50.0, value=2.0)
            paiement = st.selectbox("Moyen de Paiement", ["Carte prépayée", "Orange Money", "Free Money", "Cash à la livraison"])

        submit_btn = st.form_submit_button("Valider et Obtenir mon Code de Suivi")

        if submit_btn:
            if expediteur and destinataire and telephone:
                prix = 1500 + (poids * 500)
                if depart != arrivee:
                    prix += 3000  # Frais interurbains
                
                tracking_code = f"SN-{random.randint(100000, 999999)}"
                
                nouveau_colis = {
                    "code": tracking_code,
                    "expediteur": expediteur,
                    "destinataire": destinataire,
                    "telephone": telephone,
                    "depart": depart,
                    "arrivee": arrivee,
                    "trajet": f"{depart} ➔ {arrivee}",
                    "poids": poids,
                    "prix": int(prix),
                    "paiement": paiement,
                    "statut": "En attente de ramassage"
                }
                
                st.session_state.colis_list.append(nouveau_colis)
                st.success(f"Colis enregistré avec succès ! \n\n **Votre Code de Suivi :** `{tracking_code}` |  **Prix :** {int(prix)} FCFA")
            else:
                st.warning("Veuillez remplir tous les champs obligatoires.")

    st.subheader("Historique récent sur cette session")
    if st.session_state.colis_list:
        df_clients = pd.DataFrame(st.session_state.colis_list)
        st.dataframe(df_clients[["code", "trajet", "destinataire", "prix", "statut"]], use_container_width=True)
    else:
        st.info("Aucun colis enregistré pour l'instant.")

# ==========================================
# 2. ESPACE SUIVI : TRACKING & CARTE
# ==========================================
elif menu == "Suivre un colis":
    st.header(" Suivi de colis en temps réel")
    
    # Utilisation d'un formulaire pour la recherche pour éviter les pertes de focus/bugs de rechargement
    with st.form("search_form"):
        code_input = st.text_input("Entrez votre code de suivi (ex: SN-123456)", value=st.session_state.code_recherche)
        search_btn = st.form_submit_button("Rechercher")
        
        if search_btn:
            st.session_state.code_recherche = code_input

    if st.session_state.code_recherche:
        trouve = next((c for c in st.session_state.colis_list if c["code"] == st.session_state.code_recherche), None)
        
        if trouve:
            st.success("Colis trouvé !")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Code de suivi :** {trouve['code']}")
                st.write(f"**Trajet :** {trouve['trajet']}")
                st.write(f"**Destinataire :** {trouve['destinataire']} ({trouve['telephone']})")
            with col2:
                st.write(f"**Poids :** {trouve['poids']} kg")
                st.write(f"**Montant :** {trouve['prix']} FCFA ({trouve['paiement']})")
                st.markdown(f"**Statut Actuel :** :orange[{trouve['statut']}]")
            
            st.subheader("Localisation du Trajet (Départ)")
            pos = coords_villes.get(trouve['depart'], {"lat": 14.6928, "lon": -17.4467})
            df_map = pd.DataFrame([{"lat": pos["lat"], "lon": pos["lon"]}])
            st.map(df_map, zoom=7)
            
        else:
            st.error(f"Aucun colis ne correspond au code `{st.session_state.code_recherche}`.")

# ==========================================
# 3. ESPACE LIVREUR & ADMIN
# ==========================================
elif menu == "Espace Livreur / Admin":
    st.header(" Gestion des Missions / Administration")
    
    if not st.session_state.colis_list:
        st.info("Aucune mission de transport disponible pour le moment. Veuillez d'abord créer un colis dans l'onglet 'Envoyer un colis'.")
    else:
        # Bouton d'exportation CSV
        df_admin = pd.DataFrame(st.session_state.colis_list)
        csv = df_admin.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=" Télécharger le rapport complet (CSV/Excel)",
            data=csv,
            file_name="rapport_sen_colis.csv",
            mime="text/csv",
        )
        
        st.divider()
        st.subheader("Liste des missions à mettre à jour")
        
        for idx, colis in enumerate(st.session_state.colis_list):
            with st.expander(f"Colis : {colis['code']} ({colis['trajet']}) - Statut : {colis['statut']}"):
                st.write(f"**Expéditeur :** {colis['expediteur']} | **Destinataire :** {colis['destinataire']} ({colis['telephone']})")
                st.write(f"**Paiement :** {colis['paiement']} | **Prix :** {colis['prix']} FCFA")
                
                # Encapsuler chaque modification dans un mini-formulaire pour éviter les conflits de clés
                with st.form(key=f"form_status_{idx}"):
                    statuts_possibles = ["En attente de ramassage", "En cours de route", "Livré avec succès"]
                    current_index = statuts_possibles.index(colis['statut']) if colis['statut'] in statuts_possibles else 0
                    
                    nouveau_statut = st.selectbox(
                        "Modifier le statut",
                        statuts_possibles,
                        index=current_index,
                        key=f"select_status_{idx}"
                    )
                    
                    update_btn = st.form_submit_button("Mettre à jour le statut")
                    
                    if update_btn:
                        st.session_state.colis_list[idx]['statut'] = nouveau_statut
                        st.success(f"Statut du colis {colis['code']} mis à jour avec succès !")
                        st.rerun()