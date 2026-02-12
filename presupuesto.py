import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
import pandas as pd
import os
# Añadimos timedelta para el ajuste de zona horaria (UTC-3)
from datetime import datetime, timedelta


# --- CONFIGURACIÓN DE SUPABASE ---
URL_SUPABASE = "https://uccjcpvouzozjwzsxqqu.supabase.co" 
KEY_SUPABASE = "sb_publishable_JYDM7cZFlxI6D-l6wEC1Mw_-VnxD0tq" 

supabase: Client = create_client(URL_SUPABASE, KEY_SUPABASE)

# --- 1. FUNCIÓN PARA GUARDAR EN LA NUBE ---
from datetime import datetime, timedelta # Asegúrate de agregar timedelta arriba

def guardar_en_supabase(cliente, dominio, tramite, total):
    try:
        # Calculamos la hora de Argentina (UTC-3)
        argentina_now = datetime.utcnow() - timedelta(hours=3)
        fecha_formateada = argentina_now.strftime('%d/%m/%Y %H:%M:%S')

        data = {
            "cliente": cliente,
            "dominio": dominio,
            "tramite": tramite,
            "total": float(total),
            "created_at": fecha_formateada # Sobrescribimos con nuestra hora
        }
        supabase.table("presupuestos").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar en Supabase: {e}")
        return False

# --- 2. FUNCIÓN PARA LEER EL HISTORIAL DE LA NUBE ---
def obtener_historial():
    try:
        res = supabase.table("presupuestos").select("*").order("created_at", desc=True).execute()
        return res.data
    except Exception as e:
        st.error(f"Error al obtener historial: {e}")
        return []
# --- FUNCIÓN PDF OPTIMIZADA ---
def generar_pdf(nombre, dominio, tramite, total, detalle, registro, fecha):
    # Usamos 'latin-1' para evitar errores con símbolos de pesos o tildes comunes
    pdf = FPDF()
    pdf.add_page()
    
    # Título con fondo gris
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 15, txt="PRESUPUESTO GESTORIA AUTOMOTOR", ln=True, align="C", fill=True)
    pdf.ln(10)
    
    # Datos del Cliente
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt="INFORMACION DEL TRAMITE", ln=True)
    pdf.set_font("Arial", "", 11)
    
    # Tabla simple de datos
    pdf.cell(95, 8, txt=f"Cliente: {nombre}", border="B")
    pdf.cell(10)
    pdf.cell(85, 8, txt=f"Fecha: {fecha}", border="B", ln=True)
    
    pdf.cell(95, 8, txt=f"Dominio: {dominio.upper()}", border="B")
    pdf.cell(10)
    pdf.cell(85, 8, txt=f"Registro: {registro}", border="B", ln=True)
    
    pdf.cell(0, 8, txt=f"Tipo de Tramite: {tramite}", border="B", ln=True)
    pdf.ln(10)
    
    # Detalle de Costos
    pdf.set_font("Arial", "B", 12)
    pdf.cell(140, 10, txt="Concepto", border=1, align="C")
    pdf.cell(50, 10, txt="Importe", border=1, ln=True, align="C")
    
    pdf.set_font("Arial", "", 11)
    for concepto, valor in detalle.items():
        if valor > 0:
            pdf.cell(140, 8, txt=f" {concepto}", border=1)
            # El símbolo $ a veces falla en PDF, usamos 'USD' o simplemente el número si da error
            pdf.cell(50, 8, txt=f"$ {valor:,.2f}", border=1, ln=True, align="R")
    
    # Total
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(200, 255, 200)
    pdf.cell(140, 12, txt=" TOTAL FINAL A ABONAR", border=1, fill=True)
    pdf.cell(50, 12, txt=f"$ {total:,.2f}", border=1, ln=True, align="R", fill=True)
    
    # Nota al pie
    pdf.ln(20)
    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(0, 5, txt="Este presupuesto tiene caracter informativo. Los valores pueden variar segun disposicion de la DNRPA.", align="C")
    
    # --- BUSCA ESTA PARTE AL FINAL DE LA FUNCIÓN ---
    # Elimina el .encode('latin-1') porque ya es binario
    return pdf.output(dest='S')
import pandas as pd
import os

def guardar_en_registro(datos):
    archivo = "registro_presupuestos.csv"
    df_nuevo = pd.DataFrame([datos])
    
    # Si el archivo no existe, lo crea con encabezados. Si existe, agrega la fila abajo.
    if not os.path.isfile(archivo):
        df_nuevo.to_csv(archivo, index=False, encoding='utf-8-sig')
    else:
        df_nuevo.to_csv(archivo, mode='a', index=False, header=False, encoding='utf-8-sig')

# --- EL RESTO DE TU CÓDIGO SIGUE IGUAL ---
# (Asegúrate de mantener las secciones de Cálculos Finales y la Sección 6 que ya tienes)

# --- CONFIGURACIÓN DE INTERFAZ ---
st.set_page_config(page_title="Gestor de Presupuestos Automotor", layout="centered")
st.title("📋 Presupuestador de Trámites Gestoria V&H")

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
    fecha = st.date_input("Fecha")

# --- SECCIÓN 2: DETALLES DEL TRÁMITE ---
st.header("Detalles del Trámite")
col_t1, col_t2 = st.columns(2)

with col_t1:
    tramites_precios = {
        "Transferencia": 60000.0,
        "Transferencia M": 80000.0,
        "Transferencia L": 100000.0,
        "Duplicado Cedula o Titulo": 60000.0,
        "Denuncia de Extravío": 12000.0,
        "Denuncia de Venta": 60000.0,
        "Certificación de Firmas en R.S": 40000.0,
        "Certificacion de 1ra firma Escribania": 30000.0,
        "Informe de Dominio": 10000.0
    }
    tipo_tramite = st.selectbox("Seleccione el Trámite", list(tramites_precios.keys()))
valor_tabla = st.number_input("Precio de tabla automotor ($)", min_value=0.0, step=1000.0,format="%.0f")
with col_t2:
    distancia = st.number_input("Distancia (KM ida y vuelta)", min_value=0.0)
    costo_km = st.number_input("Costo por KM combustible ($)", min_value=0.0, value=350.0)
    mora_opciones = {"0%": 0.0, "20%": 0.2, "40%": 0.4, "60%": 0.6, "80%": 0.8, "100%": 1.0}
    mora_sel = st.selectbox("Cantidad de Moras F08 (%)", list(mora_opciones.keys()))

# --- SECCIÓN 3: SELECCIÓN DE FORMULARIOS ---
st.header("Selección de Formularios")
tab_auto, tab_moto = st.tabs(["🚗 AUTO", "🏍️ MOTO"])
total_formularios = 0.0

with tab_auto:
    c_a1, c_a2 = st.columns(2)
    with c_a1:
        if st.checkbox("02 ($8.300)"): total_formularios += 8300
        if st.checkbox("03 ($8.300)"): total_formularios += 8300
        if st.checkbox("Contrato de prenda ($7.700)"): total_formularios += 7700
        if st.checkbox("04 ($8.300)"): total_formularios += 8300
        if st.checkbox("05 ($8.300)"): total_formularios += 8300
        if st.checkbox("08 ($16.000)"): total_formularios += 16000
        if st.checkbox("08D ($16.000)"): total_formularios += 16000
        if st.checkbox("T.P. ($8.300)"): total_formularios += 8300
    with c_a2:
        if st.checkbox("11 ($8.300)"): total_formularios += 8300
        if st.checkbox("12 ($16.000)"): total_formularios += 16000
        if st.checkbox("15 ($13.000)"): total_formularios += 13000
        if st.checkbox("59 ($8.300)"): total_formularios += 8300
        if st.checkbox("59D ($8.300)"): total_formularios += 8300
        if st.checkbox("Informe Infracciones ($15.000)"): total_formularios += 15000
        if st.checkbox("Informe Histórico Dominio ($15.000)"): total_formularios += 15000
        if st.checkbox("Informe Dominio ($10.000)"): total_formularios += 10000

with tab_moto:
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        if st.checkbox("T.P.M. ($6.500)"): total_formularios += 6500
        if st.checkbox("02M ($8.300)"): total_formularios += 8300
        if st.checkbox("03M ($8.300)"): total_formularios += 8300
        if st.checkbox("04M ($8.300)"): total_formularios += 8300
        if st.checkbox("05M ($7.500)"): total_formularios += 7500
    with c_m2:
        if st.checkbox("08M ($7.500)"): total_formularios += 7500
        if st.checkbox("08MD ($7.500)"): total_formularios += 7500
        if st.checkbox("11M ($6.500)"): total_formularios += 6500
        if st.checkbox("12M ($6.500)"): total_formularios += 6500

# --- SECCIÓN 4: CÁLCULOS FINALES ---
arancel_dnrpa = valor_tabla * 0.0125
impuesto_sello = valor_tabla * 0.03
valor_mora = arancel_dnrpa * mora_opciones[mora_sel]
honorarios = tramites_precios[tipo_tramite]
costo_combustible = distancia * costo_km
total_final = arancel_dnrpa + valor_mora + honorarios + costo_combustible + impuesto_sello + total_formularios

# --- SECCIÓN 5: MOSTRAR DETALLE ---
st.markdown("---")
st.header("💰 Detalle de Costos")
col_res1, col_res2, col_res3 = st.columns(3)
col_res1.metric("Arancel DNRPA", f"${arancel_dnrpa:,.2f}")
col_res1.metric("Impuesto al Sello", f"${impuesto_sello:,.2f}")
col_res2.metric("Mora F08", f"${valor_mora:,.2f}")
col_res2.metric("Honorarios", f"${honorarios:,.2f}")
col_res3.metric("Subtotal Forms", f"${total_formularios:,.2f}")
col_res3.metric("Combustible", f"${costo_combustible:,.2f}")

st.success(f"### TOTAL: ${total_final:,.2f}")

# --- SECCIÓN 6: EXPORTACIÓN ---
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("✅ Generar formato WhatsApp"):
        texto_wa = f"""*PRESUPUESTO GESTORÍA AUTOMOTOR*\n---\n*Cliente:* {nombre}\n*Dominio:* {dominio}\n*Trámite:* {tipo_tramite}\n---\n- Arancel: ${arancel_dnrpa:,.2f}\n- Sello: ${impuesto_sello:,.2f}\n- Honorarios: ${honorarios:,.2f}\n---\n*TOTAL: ${total_final:,.2f}*"""
        st.text_area("Copia este mensaje:", texto_wa, height=200)

    if st.button("💾 Guardar en Historial Permanente"):
        if nombre and dominio:
            exito = guardar_en_supabase(nombre, dominio, tipo_tramite, total_final)
            if exito:
                st.success("✅ Guardado en la nube de Supabase.")
        else:
            st.warning("Completa Nombre y Dominio antes de guardar.")

with col_btn2:
    detalle_pdf = {
        "Arancel DNRPA (1.25%)": arancel_dnrpa,
        "Impuesto al Sello (3%)": impuesto_sello,
        "Recargo por Moras": valor_mora,
        "Subtotal Formularios": total_formularios,
        "Honorarios Profesionales": honorarios,
        "Gastos de Combustible/Traslado": costo_combustible
    }
    
    try:
        pdf_raw = generar_pdf(nombre, dominio, tipo_tramite, total_final, detalle_pdf, registro, fecha)
        pdf_bytes = bytes(pdf_raw, 'latin-1') if isinstance(pdf_raw, str) else bytes(pdf_raw)
        
        st.download_button(
            label="📥 Descargar Presupuesto PDF",
            data=pdf_bytes,
            file_name=f"Presupuesto_{dominio}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")

# --- SECCIÓN 7: CONSULTA DE HISTORIAL ---
st.markdown("---")
st.header("📂 Historial Multidispositivo")

if st.button("🔄 Actualizar Historial desde la Nube"):
    datos_nube = obtener_historial()
    if datos_nube:
        df_historial = pd.DataFrame(datos_nube)
        # Reordenamos columnas para que se vea más profesional
        cols = ["created_at", "cliente", "dominio", "tramite", "total"]
        df_mostrar = df_historial[[c for c in cols if c in df_historial.columns]]
        st.dataframe(df_mostrar, use_container_width=True)
    else:

        st.info("No hay registros en la base de datos todavía.")

















