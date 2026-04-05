import streamlit as st
import pandas as pd
import io
from datetime import date

# Oldal beállításai (reszponzív, mobilbarát kinézet)
st.set_page_config(page_title="Napi Riport", layout="centered")
st.title("📱 Napi Riport Generáló")

# Felejtő memória a napi termékeknek
if 'termekek' not in st.session_state:
    st.session_state.termekek = []

# --- 1. ALAPADATOK ---
st.header("1. Alapadatok")
col1, col2 = st.columns(2)
with col1:
    nev = st.text_input("Név", value="Danyi Róbert")
    uzlet = st.text_input("Üzlet", value="MM Westend")
    datum = st.date_input("Dátum", value=date.today())
    het = st.number_input("Hét", min_value=1, max_value=52, step=1)
with col2:
    nap = st.selectbox("Nap", ["hétfő", "kedd", "szerda", "csütörtök", "péntek", "szombat", "vasárnap"])
    oraszam = st.number_input("Ledolgozott óraszám", min_value=1, value=8)
    megszolitott = st.number_input("Megszólított vásárlók száma", min_value=0, value=0)

# --- 2. TERMÉKEK RÖGZÍTÉSE ---
st.header("2. Eladott termékek rögzítése")

# A terméklista beolvasása a feltöltött Fókusz.csv-ből
try:
    # A felhőben a kód mellé kell tenni a Fókusz.csv fájlt
    fokusz_df = pd.read_csv("Fókusz.csv", header=None)
    termek_lista = fokusz_df[0].dropna().tolist()
    if "Típus" in termek_lista: 
        termek_lista.remove("Típus")
except FileNotFoundError:
    # Ha esetleg hiányzik a fájl, egy alap lista töltődik be
    termek_lista = ["Redmi 15 C", "Xiaomi 14T", "Xiaomi Smart Band 10", "OTHER AIOT"]

t_col1, t_col2 = st.columns([2, 1])
with t_col1:
    kivalasztott_tipus = st.selectbox("Termék típusa", termek_lista)
    darab = st.number_input("Darabszám", min_value=1, value=1, step=1)
with t_col2:
    ar = st.number_input("Polcár (Ft)", min_value=0, step=1000)
    
# Dinamikus hozzáadás a memóriához
if st.button("➕ Hozzáadás"):
    st.session_state.termekek.append({"Típus": kivalasztott_tipus, "Ár": ar, "Darab": darab})
    st.success(f"{darab}x {kivalasztott_tipus} rögzítve!")

# Rögzített termékek mutatása
if st.session_state.termekek:
    st.dataframe(pd.DataFrame(st.session_state.termekek))
    if st.button("🗑️ Lista törlése (Újrakezdés)"):
        st.session_state.termekek = []
        st.rerun()

# --- 3. SZÖVEGES RÉSZ ---
st.header("3. Szöveges összefoglaló")
hiany = st.text_area("Milyen termék hiányzik / mit rendeltetnél?", value="-")
konkurencia = st.text_area("Konkurencia infók", value="-")
kihelyezes = st.text_area("Kihelyezés", value="Minden remek")
egyeb = st.text_area("Napi összefoglaló / Egyéb", placeholder="A szerdai nap valami elképesztő volt...")

# --- 4. EXPORTÁLÁS ÉS TÖRLÉS ---
st.header("4. Exportálás")
if st.button("🚀 Excel Generálása"):
    if not st.session_state.termekek:
        st.warning("Még nem adtál hozzá eladott terméket!")
    else:
        sorok = []
        for i, termek in enumerate(st.session_state.termekek):
            sorok.append({
                "Név": nev,
                "Üzlet": uzlet,
                "Dátum": datum.strftime("%Y-%m-%d"),
                "Hét": het,
                "Nap": nap,
                "Ledolgozott óraszám": oraszam,
                "Megszólított vásárlók száma": megszolitott,
                "Eladott darabszám": termek["Darab"],
                "Eladott termék polcár": termek["Ár"],
                "Eladott típus": termek["Típus"],
                "Milyen termék hiányzik/mit rendeltetnél?": hiany if i == 0 else "",
                "Konkurencia": konkurencia if i == 0 else "",
                "Kihelyezés": kihelyezes if i == 0 else "",
                "OTHER AIOT...": egyeb if i == 0 else ""
            })
        
        df = pd.DataFrame(sorok)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Napi_Riport')
        
        # Letöltés gomb, amire rányomva a telefon böngészője lementi az .xlsx fájlt
        st.download_button(
            label="📥 Excel letöltése",
            data=buffer.getvalue(),
            file_name=f"Riport_{datum}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
