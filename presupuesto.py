import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
import pandas as pd
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from PIL import Image

# --- 1. CONFIGURACIÓN DE CONEXIÓN Y ZONA HORARIA ---
URL_SUPABASE = "https://uccjcpvouzozjwzsxqqu.supabase.co" 
KEY_SUPABASE = "sb_publishable_JYDM7cZFlxI6D-l6wEC1Mw_-VnxD0tq" 
supabase: Client = create_client(URL_SUPABASE, KEY_SUPABASE)

ARG_TZ = ZoneInfo("America/Argentina/Buenos_Aires")

# --- 2. CONFIGURACIÓN DE PÁGINA E ICONO ---
try:
    # Usamos "Icono.png" con mayúscula para coincidir con tu GitHub
    img_icono = Image.open("Icono.png")
except:
    img_icono = "📋"

st.set_page_config(
    page_title="Gestoría V&H",
    page_icon=img_icono, 
    layout="centered"
)

# --- 3. FUNCIÓN DE LOGIN (SISTEMA DE USUARIOS) ---
def login_usuario():
    if "session" not in st.session_state:
        st.session_state.session = None

    if st.session_state.session is None:
        st.markdown("<h2 style='text-align: center;'>🔐 Acceso Privado</h2>", unsafe_allow_html=True)
        st.info("Ingresa con tu correo y contraseña autorizados.")
        
        with st.form("login_form"):
            email = st.text_input("Correo electrónico")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Iniciar Sesión")
            
            if submit:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.session = res.session
                    st.success("Acceso concedido")
                    st.rerun()
                except Exception:
                    st.error("Credenciales incorrectas o usuario no autorizado.")
        return False
    return True

# --- INICIO DE LA APLICACIÓN PROTEGIDA ---
if login_usuario():
    
    # Botón para cerrar sesión en la barra lateral
    if st.sidebar.button("Cerrar Sesión"):
        supabase.auth.sign_out()
        st.session_state.session = None
        st.rerun()

    # --- FUNCIONES DE APOYO ---
    def formato_moneda(valor):
        return f"$ {valor:,.0f}".replace(",", ".")

    def guardar_en_supabase(cliente, dominio, tramite, total):
        try:
            ahora = datetime.now(ARG_TZ)
            fecha_para_supabase = ahora.isoformat()
            data = {
                "cliente": cliente,
                "dominio": dominio,
                "tramite": tramite,
                "total": float(total),
                "created_at": fecha_para_supabase
            }
            supabase.table("presupuestos").insert(data).execute()
            return True
        except Exception as e:
            st.error(f"Error al guardar: {e}")
            return False

    def obtener_historial():
        try:
            res = supabase.table("presupuestos").select("*").order("created_at", desc=True).execute()
            return res.data
        except Exception as e:
            st.error(f"Error al obtener historial: {e}")
            return []

    def generar_pdf(nombre, dominio, tramite, total, detalle, registro, fecha):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 15, txt="PRESUPUESTO GESTORIA AUTOMOTOR", ln=True, align="C", fill=True)
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, txt="INFORMACION DEL TRAMITE", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(95, 8, txt=f"Cliente: {nombre}", border="B")
        pdf.cell(10)
        pdf.cell(85, 8, txt=f"Fecha: {fecha}", border="B", ln=True)
        pdf.cell(95, 8, txt=f"Dominio: {dominio.upper()}", border="B")
        pdf.cell(10)
        pdf.cell(85, 8, txt=f"Registro: {registro}", border="B", ln=True)
        pdf.cell(0, 8, txt=f"Tipo de Tramite: {tramite}", border="B", ln=True)
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(140, 10, txt="Concepto", border=1, align="C")
        pdf.cell(50, 10, txt="Importe", border=1, ln=True, align="C")
        pdf.set_font("Arial", "", 11)
        for concepto, valor in detalle.items():
            if valor > 0:
                pdf.cell(140, 8, txt=f" {concepto}", border=1)
                pdf.cell(50, 8, txt=f"$ {valor:,.2f}", border=1, ln=True, align="R")
        pdf.ln(5)
        pdf.set_font("Arial", "B", 14)
        pdf.set_fill_color(200, 255, 200)
        pdf.cell(140, 12, txt=" TOTAL FINAL A ABONAR", border=1, fill=True)
        pdf.cell(50, 12, txt=f"$ {total:,.2f}", border=1, ln=True, align="R", fill=True)
        pdf.ln(20)
        pdf.set_font("Arial", "I", 9)
        pdf.multi_cell(0, 5, txt="Este presupuesto tiene caracter informativo. Los valores pueden variar segun disposicion de la DNRPA.", align="C")
        return pdf.output(dest='S')

    # --- INTERFAZ DE USUARIO ---
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.warning("No se encontró el archivo logo.png")

    st.markdown("<h1 style='text-align: center;'>📋 Presupuestador de Trámites</h1>", unsafe_allow_html=True)

    # --- SECCIÓN 1: DATOS DEL CLIENTE ---
    st.header("Datos del Cliente")
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre y Apellido")
        dni = st.text_input("DNI / CUIT")
        dominio = st.text_input("Dominio del Vehículo")
    with col2:
        telefono = st.text_input("Teléfono")
        registro = st.text_input("Registro")
        fecha_input = st.date_input("Fecha")

    # --- SECCIÓN 2: DETALLES DEL TRÁMITE ---
    st.header("Detalles del Trámite")
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        tramites_precios = {
            "-": 0.0, "Transferencia": 60000.0, "Transferencia M": 80000.0,
            "Transferencia L": 100000.0, "Denuncia de Posesion": 80000.0,
            "Alta/Baja": 45000.0, "Duplicado Cedula o Titulo": 60000.0,
            "Denuncia de Extravío": 12000.0, "Denuncia de Venta": 60000.0,
            "Certificación de Firmas en R.S": 40000.0, "Informe de Dominio": 10000.0
        }
        tipo_tramite = st.selectbox("Seleccione el Trámite", list(tramites_precios.keys()))
        valor_tabla = st.number_input("Precio de tabla automotor ($)", min_value=0.0, step=1000.0, format="%.0f")
        st.caption(f"Valor: **{formato_moneda(valor_tabla)}**")

    with col_t2:
        distancia = st.number_input("Distancia (KM ida y vuelta)", min_value=0.0)
        costo_km = st.number_input("Costo por KM combustible ($)", min_value=0.0, value=350.0)
        mora_opciones = {"0%": 0.0, "20%": 0.2, "40%": 0.4, "60%": 0.6, "100%": 1.0}
        mora_sel = st.selectbox("Cantidad de Moras F08 (%)", list(mora_opciones.keys()))
        otros_gastos = st.number_input("Otros gastos ($)", min_value=0.0)

    # --- SECCIÓN 3: FORMULARIOS ---
    st.header("Selección de Formularios")
    total_formularios = 0.0
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        if st.checkbox("08 ($16.000)"): total_formularios += 16000
        if st.checkbox("12 ($16.000)"): total_formularios += 16000
    with c_f2:
        if st.checkbox("Informe Infracciones ($15.000)"): total_formularios += 15000
        if st.checkbox("02 ($8.300)"): total_formularios += 8300

    # --- SECCIÓN 4: CÁLCULOS ---
    arancel_dnrpa = valor_tabla * 0.0125
    impuesto_sello = valor_tabla * 0.03
    valor_mora = arancel_dnrpa * mora_opciones[mora_sel]
    honorarios = tramites_precios[tipo_tramite]
    costo_combustible = distancia * costo_km
    total_final = arancel_dnrpa + valor_mora + honorarios + costo_combustible + impuesto_sello + total_formularios + otros_gastos

    # --- SECCIÓN 5: RESULTADOS ---
    st.markdown("---")
    st.header("💰 Detalle de Costos")
    col_res1, col_res2, col_res3 = st.columns(3)
    col_res1.metric("Arancel DNRPA", formato_moneda(arancel_dnrpa))
    col_res1.metric("Impuesto al Sello", formato_moneda(impuesto_sello))
    col_res2.metric("Mora F08", formato_moneda(valor_mora))
    col_res2.metric("Honorarios", formato_moneda(honorarios))
    col_res3.metric("Subtotal Forms", formato_moneda(total_formularios))
    col_res3.metric("Combustible", formato_moneda(costo_combustible))
    
    st.success(f"### TOTAL FINAL: {formato_moneda(total_final)}")

    # --- SECCIÓN 6: BOTONES ---
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("💾 Guardar en Historial"):
            if nombre and dominio:
                if guardar_en_supabase(nombre, dominio, tipo_tramite, total_final):
                    st.success("✅ Guardado en la nube.")
            else:
                st.warning("Faltan datos del cliente.")

    with col_btn2:
        detalle_pdf = {"Arancel": arancel_dnrpa, "Sello": impuesto_sello, "Mora": valor_mora, "Honorarios+Otros": honorarios + total_formularios + costo_combustible + otros_gastos}
        try:
            pdf_raw = generar_pdf(nombre, dominio, tipo_tramite, total_final, detalle_pdf, registro, fecha_input)
            st.download_button(label="📥 Descargar PDF", data=pdf_raw, file_name=f"Presupuesto_{dominio}.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Error PDF: {e}")

    # --- SECCIÓN 7: HISTORIAL ---
    st.markdown("---")
    if st.button("🔄 Ver Historial de la Nube"):
        datos = obtener_historial()
        if datos:
            df = pd.DataFrame(datos)[["created_at", "cliente", "dominio", "tramite", "total"]]
            st.dataframe(df, use_container_width=True)




























































