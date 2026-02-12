import streamlit as st

st.set_page_config(page_title="Gestor de Presupuestos Automotor", layout="centered")

st.title("📋 Presupuestador de Trámites")

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
    # Lista de trámites según tu imagen de "Parámetros Configurables"
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
    valor_tabla = st.number_input("Precio de tabla automotor ($)", min_value=0.0, step=1000.0)

with col_t2:
    distancia = st.number_input("Distancia (KM ida y vuelta)", min_value=0.0)
    costo_km = st.number_input("Costo por KM combustible ($)", min_value=0.0, value=350.0)
    # Selector de Mora basado en tu tabla de 0% a 100%
    mora_opciones = {"0%": 0.0, "20%": 0.2, "40%": 0.4, "60%": 0.6, "80%": 0.8, "100%": 1.0}
    mora_sel = st.selectbox("Cantidad de Moras F08 (%)", list(mora_opciones.keys()))

# --- SECCIÓN 3: SELECCIÓN DE FORMULARIOS (AUTO Y MOTO) ---
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

# --- SECCIÓN 5: MOSTRAR DETALLE DE COSTOS (INTERFAZ MÉTRICA) ---
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

# --- BOTÓN DE WHATSAPP ---
if st.button("Generar formato WhatsApp"):
    texto_wa = f"""
*PRESUPUESTO GESTORÍA AUTOMOTOR*
---------------------------------
*Cliente:* {nombre}
*Dominio:* {dominio}
*Trámite:* {tipo_tramite}
---------------------------------
- Arancel DNRPA: ${arancel_dnrpa:,.2f}
- Impuesto al Sello (3%): ${impuesto_sello:,.2f}
- Mora F08: ${valor_mora:,.2f}
- Formularios: ${total_formularios:,.2f}
- Honorarios: ${honorarios:,.2f}
- Traslado/Combustible: ${costo_combustible:,.2f}
---------------------------------
*TOTAL FINAL: ${total_final:,.2f}*
    """
    st.text_area("Copia este mensaje:", texto_wa, height=300)