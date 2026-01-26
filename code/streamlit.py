import streamlit as st
import pandas as pd

# Titre de l'application
st.title("Bienvenue dans l'application Streamlit")

# Description
st.write("Ceci est une application de démonstration utilisant Streamlit.")

# 1. Champ de saisie pour le prénom
st.text_input("Entrez votre prénom :", key="name_input")
st.button("Soumettre")
# 2. Récupération du prénom
name = st.session_state.name_input

# 3. Condition : afficher un message si le prénom est renseigné
if name:
    st.write(f"Bonjour, {name}")
else:
    st.write("Veuillez entrer votre prénom ci-dessus.")


# 4. Print pour montrer que le script est relancé à chaque interaction
print("Streamlit application is running.")


df = pd.read_csv(r"..\Data\row\events.csv")
df_20 = df.sample(frac=0.2, random_state=42)
st.write('affichage du dataframe events.csv', df)
st.line_chart(df_20['itemid'].value_counts())
st.area_chart(df_20['event'].value_counts())