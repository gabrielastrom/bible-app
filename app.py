import time
import pandas as pd
import numpy as np
import streamlit as st
import requests
import json
import re
from streamlit_extras.streaming_write import write
from streamlit_card import card

st.set_page_config(page_title="Läs Bibeln", 
                   page_icon=":open_book:",
                   layout="wide",
                   initial_sidebar_state="expanded")


def stream_text(sentence): # Streama text, får se när det används...
    for letter in sentence:
        yield letter
        time.sleep(0.01)


with open('books.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

# Main Page, 3 tabs
st.title("Bibeln", anchor=False)
tab1, tab2, tab3 = st.tabs(["Bibliotek", "Text", "Anteckningar"])

with tab1:
    num_columns = 4
    columns = st.columns(num_columns)
    for i, book in enumerate(books):
        with columns[i % num_columns]:
            card(
                key=book["title"],
                title=book["name"].upper() if "name" in book and book["name"] else book["title"].upper(),
                text=book["text"],
                image=book["image"],
                styles={
                    "card": {
                        "margin": "10px",
                        "width": "100",
                        "border": "1px solid rgba(255, 255, 255, 0.18)",
                        "box-shadow": "0 4px 20px rgba(255, 255, 255, 0.5)"
                    },
                    "title": {
                        "font-family": "serif",
                    },
                    "text": {
                        "font-family": "serif",
                    }
                }
            )

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.vald_bok = st.selectbox("Välj bok i Bibeln:", options=[book["title"] for book in books])
    with col2:
        st.session_state.kapitel = st.number_input("Kapitel", 1)

    
    # Hämta text från Bible API
    if st.session_state.vald_bok and st.session_state.kapitel:
        st.header(f"{st.session_state.vald_bok.upper()}, Kapitel {st.session_state.kapitel}", divider=True)
        bok_text = requests.get(f"https://cdn.jsdelivr.net/gh/wldeh/bible-api/bibles/sv-skb/books/{st.session_state.vald_bok.lower()}/chapters/{st.session_state.kapitel}.json")
        data = bok_text.json()
        with st.container():
            # Formatera texten
            formatted_verses = []
            for verse in data["data"]:
                # Originalversen
                verse_text = verse['text']

                # Färga texten inom [] och ()
                verse_text = re.sub(r'\[(.*?)\]', r"<span style='color: gray;'><em>[\1]</em></span>", verse_text)  # Text inom []
                verse_text = re.sub(r'\((.*?)\)', r"<span style='color: gray;'><em>(\1)</em></span>", verse_text)  # Text inom ()

                # Sammansätt versen med versnumret
                formatted_verse = f"<span style='font-size: 0.7em; color: lightgray;'>{verse['verse']}:</span> <span style='color: lightgray;'>{verse_text}</span>"
                formatted_verses.append(formatted_verse)

            # Sammansätt all text
            text = "<br>".join(formatted_verses)
            st.markdown(text, unsafe_allow_html=True)  # Visa den sammanslagna texten med HTML

with tab3:
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.header("Anteckningar", anchor=False)
        with st.form("post_form", clear_on_submit=True):
            st.write("Skriv en anteckning:")
            post_author = st.text_input("Namn")
            post_title = st.text_input("Rubrik")
            post_text = st.text_input("Text")
            
            submitted = st.form_submit_button("Publicera")
            if submitted:
                new_post = {
                    "id": f"post{len(posts) + 1}",
                    "author": post_author,
                    "title": post_title,
                    "text": post_text
                }
                posts.append(new_post)
                with open("posts.json", "w", encoding="utf-8") as file:
                    json.dump(posts, file, ensure_ascii=False, indent=4)
                st.success("Anteckning publicerad.")

    with col2:
        num_columns = 3
        columns = st.columns(num_columns)
        for i, post in enumerate(reversed(posts)):
            with columns[i % num_columns]:
                card(
                    key=post["id"],
                    title=post["title"],
                    text=post["text"] + " || Skrivet av " + post["author"],
                    styles={
                        "card": {
                            "margin": "10px",
                            "width": "350px",
                            "height": "400px",
                            "padding": "24px",
                            "border": "1px solid rgba(255, 255, 255, 0.18)"
                        }
                    }
                )




"---"
st.caption("Made with :heart: by Gabriel :beach_with_umbrella:", )



# Balloons!!
# st.balloons()