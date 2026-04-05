import streamlit as st
import pandas as pd
import io
from datetime import date
import os

# Oldal beállításai
st.set_page_config(page_title="Napi Riport", page_icon="📝", layout="centered")
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
    
    # Automatikus Hét és Nap számolás a dátumból
    het = datum.isocalendar()[1]
    magyar_napok = ["hétfő", "kedd", "szerda", "csütörtök", "péntek", "szombat", "vasárnap"]
    nap = magyar_napok[datum.weekday()]
    
with col2:
    # Kék infó doboz, ami mutatja a kiszámolt napot és hetet
    st.info(f"📅 Automatikus dátum:\n**{het}. hét, {nap}**")
    oraszam = st.number_input("Ledolgozott óraszám", min_value=1, value=8)
    megszolitott = st.number_input("Megszólított vásárlók száma", min_value=0, value=0)

# --- 2. TERMÉKEK RÖGZÍTÉSE ---
st.header("2. Eladott termékek rögzítése")

# Okosabb fájlkeresés (ékezettel és anélkül is megpróbálja)
lehetseges_nevek = ["fokusz.csv", "Fokusz.csv", "Fókusz.csv", "FÓKUSZ.csv"]
termek_lista = []

for nev_verzio in lehetseges_nevek:
    if os.path.exists(nev_verzio):
        try:
            fokusz_df = pd.read_csv(nev_verzio, header=None)
            termek_lista = fokusz_df[0].dropna().tolist()
            if "Típus" in termek_lista: 
                termek_lista.remove("Típus")
            break  # Ha megtalálta és beolvasta, kilép a keresésből
        except Exception:
            pass

if not termek_lista:
    termek_lista = ["Kérlek töltsd fel a fokusz.csv fájlt a GitHubra!"]

# "No sales" hozzáadása a lista legelejére
if "No sales" not in termek_lista:
    termek_lista.insert(0, "No sales")

t_col1, t_col2 = st.columns([2, 1])
with t_col1:
    kivalasztott_tipus = st.selectbox("Termék típusa", termek_lista)
    alap_darab = 0 if kivalasztott_tipus == "No sales" else 1
    darab = st.number_input("Darabszám", min_value=0, value=alap_darab, step=1)
with t_col2:
    ar = st.number_input("Polcár (Ft)", min_value=0, step=1000)
    
if st.button("➕ Hozzáadás"):
    st.session_state.termekek.append({"Típus": kivalasztott_tipus, "Ár": ar, "Darab": darab})
    st.success(f"{darab}x {kivalasztott_tipus} rögzítve!")

if st.session_state.termekek:
    st.dataframe(pd.DataFrame(st.session_state.termekek))
    if st.button("🗑️ Lista törlése (Újrakezdés)"):
        st.session_state.termekek = []
        st.rerun()

# --- 3. SZÖVEGES RÉSZ ---
st.header("3. Szöveges összefoglaló")
st.info("💡 FONTOS: Pontos típusokat, színt, memória kivitelt is jelezd!")
hiany = st.text_area("Milyen termék hiányzik / mit rendeltetnél?", value="-")
konkurencia = st.text_area("Konkurencia (új brand, promóter, akciók, legkeresettebb termék)", value="-")
kihelyezes = st.text_area("Kihelyezés (hiányzó DEMO, planogram, működnek-e)", value="Minden rendben")
komment = st.text_area("Komment (tapasztalatok, észrevételek)", placeholder="Ide írhatsz bármit az áruházzal, vásárlókkal kapcsolatban...")

# --- 4. EXPORTÁLÁS ---
st.header("4. Exportálás")

if not st.session_state.termekek:
    st.info("ℹ️ A letöltéshez kérlek rögzítsd a napot (adj hozzá legalább egy terméket vagy a 'No sales' opciót)!")
else:
    hibak = []
    for termek in st.session_state.termekek:
        if termek["Típus"] != "No sales":
            if termek["Ár"] == 0:
                hibak.append(f"A(z) {termek['Típus']} termék polcára nem lehet 0 Ft!")
            if termek["Darab"] == 0:
                hibak.append(f"A(z) {termek['Típus']} termék darabszáma nem lehet 0!")

    if hibak:
        st.warning("A fájl letöltéséhez kérlek javítsd a következőket:")
        for hiba in hibak:
            st.error(f"❌ {hiba}")
    else:
        if megszolitott == 0:
            st.warning("A 'Megszólított vásárlók száma' 0. Ha ez nem elírás, letöltheted a fájlt.")
            
        st.success("✅ Minden adat rendben, a formázott riport készen áll a letöltésre!")
        
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
                "Komment": komment if i == 0 else ""
            })
        
        df = pd.DataFrame(sorok)
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Napi_Riport')
            workbook = writer.book
            worksheet = writer.sheets['Napi_Riport']
            
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#F0F0F0',
                'border': 1
            })
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                column_len = max(df[value].astype(str).map(len).max(), len(value)) + 2
                worksheet.set_column(col_num, col_num, min(column_len, 40))
                
        formazott_nev = nev.replace(" ", "_")
        fajlnev = f"{formazott_nev}_W{het}_{nap}.xlsx"
        
        st.download_button(
            label="📥 Formázott Excel letöltése",
            data=buffer.getvalue(),
            file_name=fajlnev,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
