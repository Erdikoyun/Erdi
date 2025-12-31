import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ---------------- GOOGLE SHEETS ----------------
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPE
)
client = gspread.authorize(creds)
sheet = client.open("TurMaliyetDB").sheet1


def get_all_tours():
    return pd.DataFrame(sheet.get_all_records())


def add_tour(row):
    sheet.append_row(row)


def update_tour(name, new_row):
    records = sheet.get_all_records()
    for i, r in enumerate(records, start=2):
        if r["name"] == name:
            sheet.update(f"A{i}:U{i}", [new_row])
            break


# ---------------- STREAMLIT ----------------
st.set_page_config("Tur Maliyet Dashboard", layout="wide")

menu = st.sidebar.radio(
    "Menü",
    ["Tur Ekle", "Tur Düzenle", "Tur Hesapla"]
)

df = get_all_tours()

# ---------------- TUR EKLE ----------------
if menu == "Tur Ekle":
    st.header("🚌 Yeni Tur Ekle")

    name = st.text_input("Tur Adı")

    v1 = st.number_input("1–12 Kişi", 0.0)
    v2 = st.number_input("13–26 Kişi", 0.0)
    v3 = st.number_input("27–44 Kişi", 0.0)
    guide = st.number_input("Rehber", 0.0)

    b_a = st.number_input("Kahvaltı Yetişkin", 0.0)
    b_c = st.number_input("Kahvaltı Çocuk", 0.0)
    l_a = st.number_input("Öğle Yetişkin", 0.0)
    l_c = st.number_input("Öğle Çocuk", 0.0)
    d_a = st.number_input("Akşam Yetişkin", 0.0)
    d_c = st.number_input("Akşam Çocuk", 0.0)

    entrance = st.number_input("Ören Yeri (Kişi Başı)", 0.0)

    e1t = st.text_input("Ekstra 1 Başlık")
    e1a = st.number_input("Ekstra 1 Yetişkin", 0.0)
    e1c = st.number_input("Ekstra 1 Çocuk", 0.0)

    e2t = st.text_input("Ekstra 2 Başlık")
    e2a = st.number_input("Ekstra 2 Yetişkin", 0.0)
    e2c = st.number_input("Ekstra 2 Çocuk", 0.0)

    e3t = st.text_input("Ekstra 3 Başlık")
    e3a = st.number_input("Ekstra 3 Yetişkin", 0.0)
    e3c = st.number_input("Ekstra 3 Çocuk", 0.0)

    if st.button("Kaydet"):
        add_tour([
            name, v1, v2, v3, guide,
            b_a, b_c, l_a, l_c, d_a, d_c,
            entrance,
            e1t, e1a, e1c,
            e2t, e2a, e2c,
            e3t, e3a, e3c
        ])
        st.success("Tur kaydedildi")

# ---------------- TUR HESAPLA ----------------
else:
    st.header("📊 Tur Maliyet Dashboard")

    tour_name = st.selectbox("Tur Seç", df["name"])
    adult = st.number_input("Yetişkin", 0)
    child = st.number_input("Çocuk", 0)

    if st.button("Hesapla"):
        t = df[df["name"] == tour_name].iloc[0]
        total_people = adult + child

        vehicle = (
            t.v1_12 if total_people <= 12 else
            t.v13_26 if total_people <= 26 else
            t.v27_44
        )

        food = adult * (t.b_a + t.l_a + t.d_a) + child * (t.b_c + t.l_c + t.d_c)
        entrance = total_people * t.entrance
        extras = adult * (t.e1a + t.e2a + t.e3a) + child * (t.e1c + t.e2c + t.e3c)

        total = vehicle + t.guide + food + entrance + extras

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Toplam Kişi", total_people)
        c2.metric("Araç + Rehber", f"{vehicle + t.guide:,.0f} ₺")
        c3.metric("Kişi Başı", f"{total / total_people:,.2f} ₺")
        c4.metric("Toplam Maliyet", f"{total:,.2f} ₺")

        breakdown = pd.DataFrame({
            "Kalem": ["Araç", "Rehber", "Yemek", "Ören Yeri", "Ekstra"],
            "Tutar": [vehicle, t.guide, food, entrance, extras]
        })

        st.dataframe(breakdown, use_container_width=True)
        st.bar_chart(breakdown.set_index("Kalem"))

