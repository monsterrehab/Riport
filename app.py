import streamlit as st
import pandas as pd
import io
from datetime import date
import openpyxl

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
    
    # Automatikus Hét és Nap számolás
    het = datum.isocalendar()[1]
    magyar_napok = ["hétfő", "kedd", "szerda", "csütörtök", "péntek", "szombat", "vasárnap"]
    nap = magyar_napok[datum.weekday()]
    
with col2:
    st.info(f"📅 Automatikus dátum:\n**{het}. hét, {nap}**")
    oraszam = st.number_input("Ledolgozott óraszám", min_value=1, value=8)
    megszolitott = st.number_input("Megszólított vásárlók száma", min_value=0, value=0)

# --- 2. TERMÉKEK RÖGZÍTÉSE ---
st.header("2. Eladott termékek rögzítése")

# Terméklista kiolvasása KÖZVETLENÜL az eredeti Excel sablon Fókusz füléről
termek_lista = []
try:
    df_fokusz = pd.read_excel('sablon.xlsx', sheet_name='Fókusz', header=None)
    termek_lista = df_fokusz[0].dropna().tolist()
    if "Típus" in termek_lista: 
        termek_lista.remove("Típus")
except Exception:
    termek_lista = ["Kérlek töltsd fel a sablon.xlsx fájlt a GitHubra!"]

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

# --- 4. EXPORTÁLÁS (SABLON ALAPJÁN) ---
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
        
        try:
            # Megnyitjuk az eredeti Excel sablont
            wb = openpyxl.load_workbook('sablon.xlsx')
            
            # Ellenőrizzük, hogy a Riport fül megvan-e, ha igen azt választjuk ki
            if 'Riport' in wb.sheetnames:
                ws = wb['Riport']
            else:
                ws = wb.active  # Ha nincs Riport nevű fül, az elsőt használja
            
            # Adatok beírása a 2. sortól kezdve (az 1. sor a fejléc)
            kezdo_sor = 2
            for i, termek in enumerate(st.session_state.termekek):
                sor = kezdo_sor + i
                ws.cell(row=sor, column=1, value=nev)
                ws.cell(row=sor, column=2, value=uzlet)
                ws.cell(row=sor, column=3, value=datum.strftime("%Y-%m-%d"))
                ws.cell(row=sor, column=4, value=het)
                ws.cell(row=sor, column=5, value=nap)
                ws.cell(row=sor, column=6, value=oraszam)
                ws.cell(row=sor, column=7, value=megszolitott)
                ws.cell(row=sor, column=8, value=termek["Darab"])
                ws.cell(row=sor, column=9, value=termek["Ár"])
                ws.cell(row=sor, column=10, value=termek["Típus"])
                ws.cell(row=sor, column=11, value=hiany if i == 0 else "")
                ws.cell(row=sor, column=12, value=konkurencia if i == 0 else "")
                ws.cell(row=sor, column=13, value=kihelyezes if i == 0 else "")
                ws.cell(row=sor, column=14, value=komment if i == 0 else "")
            
            # Excel mentése a memóriába (hogy ne módosítsa végleg a felhőben lévő sablont)
            buffer = io.BytesIO()
            wb.save(buffer)
            
            formazott_nev = nev.replace(" ", "_")
            fajlnev = f"{formazott_nev}_W{het}_{nap}.xlsx"
            
            st.download_button(
                label="📥 Formázott Excel letöltése",
                data=buffer.getvalue(),
                file_name=fajlnev,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"Hiba történt a sablon megnyitásakor. Biztosan feltöltötted a 'sablon.xlsx' fájlt? Részletek: {e}")
