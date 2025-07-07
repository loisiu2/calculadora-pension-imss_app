import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# Constantes (2025)
UMA_DIARIA = 145.01  # UMA diaria estimada
INPC_ANUAL = 0.045   # Inflación estimada
MAX_SALARIO_M40 = 25 * UMA_DIARIA * 30  # ~$108,750 MXN
SEM_L97_2025 = 850   # Semanas requeridas Ley 97 en 2025

# Funciones de cálculo
def semanas_totales(semanas_act, semanas_mod10, semanas_mod40):
    """Suma las semanas cotizadas totales."""
    return semanas_act + semanas_mod10 + semanas_mod40

def calcular_pension_l73(salario_base, total_semanas, edad_retiro, edad_actual):
    """Calcula la pensión según Ley 73."""
    if total_semanas < 500:
        return 0
    porcentajes = {60: 0.75, 61: 0.80, 62: 0.85, 63: 0.90, 64: 0.95, 65: 1.0}
    porcentaje = porcentajes.get(edad_retiro, 1.0)
    cuantia_basica = 4000  # Simplificada, ajustar con tabla IMSS
    incremento = (max(0, total_semanas - 500) // 52) * 0.01
    pension = (salario_base * porcentaje + cuantia_basica) * (1 + incremento)
    años_faltantes = max(0, edad_retiro - edad_actual)
    pension = pension * (1 + INPC_ANUAL) ** años_faltantes
    return pension

def calcular_costo_m40(salario_mensual, semanas_mod40):
    """Calcula el costo de Modalidad 40."""
    cuota_mensual = salario_mensual * 0.10075  # ~10.075%
    total_m40 = cuota_mensual * (semanas_mod40 / 4.3)
    return cuota_mensual, total_m40

def calcular_pension_l97(saldo_afore, edad_retiro, edad_actual, rendimiento_anual):
    """Estima la pensión según Ley 97 (renta vitalicia aproximada)."""
    años_faltantes = max(0, edad_retiro - edad_actual)
    saldo_proyectado = saldo_afore * (1 + rendimiento_anual) ** años_faltantes
    pension_anual = saldo_proyectado * 0.04  # 4% del saldo
    return pension_anual / 12

def semanas_requeridas_l97(año_actual, año_retiro):
    """Calcula semanas requeridas para Ley 97 según el año."""
    año_base = 2025
    semanas_base = 850
    incremento_anual = 25
    años_transcurridos = max(0, min(año_retiro, año_actual) - año_base)
    semanas_requeridas = min(semanas_base + incremento_anual * años_transcurridos, 1000)
    return semanas_requeridas

# Interfaz de Streamlit
st.title("Calculadora de Pensión IMSS 🇲🇽")
st.write("Ingresa tus datos para proyectar tu pensión según Ley 73 o Ley 97.")

# Estado de la sesión
if 'edad_actual' not in st.session_state:
    st.session_state.edad_actual = 30

# Fecha de alta en el IMSS
st.subheader("Determina tu régimen")
fecha_alta = st.date_input("Fecha de alta en el IMSS", value=date(1995, 1, 1))
es_ley73 = fecha_alta < date(1997, 7, 1)
régimen = "Ley 73" if es_ley73 else "Ley 97"
st.write(f"**Régimen**: {régimen} {'(antes del 1 de julio de 1997)' if es_ley73 else '(a partir del 1 de julio de 1997)'}")

# Entradas comunes
edad_actual = st.number_input("Edad actual", 18, 100, value=30)
st.session_state.edad_actual = edad_actual
semanas_act = st.number_input("Semanas cotizadas actuales", 0, 5000, value=500)
edad_retiro = st.slider("Edad de retiro proyectada", 60, 70, 65)
año_actual = datetime.now().year
año_retiro = año_actual + (edad_retiro - edad_actual)

if es_ley73:
    # Ley 73: Comparativo Modalidad 10 vs. Modalidad 40
    st.subheader("Ley 73: Comparativo Modalidad 10 vs. Modalidad 40")
    usa_mod10 = st.checkbox("¿Cotizarás en Modalidad 10?", key="mod10")
    semanas_mod10 = st.number_input("Semanas en Modalidad 10", 0, 520, value=104) if usa_mod10 else 0
    salario_mod10 = st.number_input("Salario mensual en Modalidad 10 ($MXN)", 1000.0, MAX_SALARIO_M40, value=12000.0) if usa_mod10 else 0

    usa_mod40 = st.checkbox("¿Cotizarás en Modalidad 40?", key="mod40")
    semanas_mod40 = st.number_input("Semanas en Modalidad 40", 0, 520, value=250) if usa_mod40 else 0
    salario_mod40 = st.number_input("Salario mensual en Modalidad 40 ($MXN)", 1000.0, MAX_SALARIO_M40, value=50000.0) if usa_mod40 else 0

    # Cálculos
    total_semanas_mod10 = semanas_totales(semanas_act, semanas_mod10, 0)
    total_semanas_mod40 = semanas_totales(semanas_act, 0, semanas_mod40)
    pension_mod10 = calcular_pension_l73(salario_mod10, total_semanas_mod10, edad_retiro, edad_actual) if usa_mod10 else 0
    pension_mod40 = calcular_pension_l73(salario_mod40, total_semanas_mod40, edad_retiro, edad_actual) if usa_mod40 else 0
    cuota_mensual_m40, total_m40 = calcular_costo_m40(salario_mod40, semanas_mod40) if usa_mod40 else (0, 0)
    recuperacion_m40 = total_m40 / pension_mod40 if pension_mod40 > 0 and usa_mod40 else float('inf')

    # Comparativo
    st.subheader("📊 Comparativo: Modalidad 10 vs. Modalidad 40")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Modalidad 10")
        st.write(f"**Semanas totales**: {total_semanas_mod10}")
        st.write(f"**Pensión estimada**: ${pension_mod10:,.2f} MXN/mes")
        st.write("**Costo mensual**: $0 (cotización regular)")
        st.write("**Costo total**: $0")
    with col2:
        st.markdown("### Modalidad 40")
        st.write(f"**Semanas totales**: {total_semanas_mod40}")
        st.write(f"**Pensión estimada**: ${pension_mod40:,.2f} MXN/mes")
        st.write(f"**Costo mensual**: ${cuota_mensual_m40:,.2f}")
        st.write(f"**Costo total**: ${total_m40:,.2f}")
        if usa_mod40:
            st.write(f"**Recuperación de inversión**: {recuperacion_m40:.1f} meses")

    # Gráfico
    if usa_mod10 or usa_mod40:
        data = []
        if usa_mod10:
            data.append({"Modalidad": "Modalidad 10", "Pensión ($MXN)": pension_mod10})
        if usa_mod40:
            data.append({"Modalidad": "Modalidad 40", "Pensión ($MXN)": pension_mod40})
        df = pd.DataFrame(data)
        fig = px.bar(df, x="Modalidad", y="Pensión ($MXN)", title="Comparativa de pensión")
        st.plotly_chart(fig)

    # Proyección de semanas faltantes
    semanas_faltantes = max(0, 500 - max(total_semanas_mod10, total_semanas_mod40))
    años_faltantes = semanas_faltantes / 52
    st.write(f"**Proyección**: Necesitas **{semanas_faltantes} semanas** más (~{años_faltantes:.1f} años) para alcanzar las 500 semanas requeridas.")

else:
    # Ley 97: Proyección de Afore
    st.subheader("Ley 97: Proyección de pensión por Afore")
    saldo_afore = st.number_input("Saldo actual en tu Afore ($MXN)", 0.0, 10000000.0, value=500000.0)
    rendimiento_anual = st.slider("Rendimientos anuales estimados (%)", 0.0, 10.0, 5.0) / 100
    semanas_requeridas = semanas_requeridas_l97(año_actual, año_retiro)
    pension_l97 = calcular_pension_l97(saldo_afore, edad_retiro, edad_actual, rendimiento_anual)

    st.success(f"**Pensión estimada a los {edad_retiro}**: ${pension_l97:,.2f} MXN/mes")
    semanas_faltantes = max(0, semanas_requeridas - semanas_act)
    años_faltantes = semanas_faltantes / 52
    st.write(f"**Proyección**: Necesitas **{semanas_faltantes} semanas** más (~{años_faltantes:.1f} años) para alcanzar las {semanas_requeridas} semanas requeridas en {año_retiro}.")

# Explicaciones
st.markdown("""
### 📋 ¿Qué son Ley 73, Ley 97, Modalidad 10 y Modalidad 40?
- **Ley 73**: Aplica si cotizaste antes del 1 de julio de 1997. Requiere 500 semanas cotizadas. La pensión se basa en el salario promedio de las últimas 250 semanas.
- **Ley 97**: Aplica si cotizaste a partir del 1 de julio de 1997. Requiere 850 semanas en 2025, aumentando a 1,000 en 2031. La pensión depende del saldo en tu Afore.
- **Modalidad 10**: Cotización regular basada en tu salario actual (sin costo adicional).
- **Modalidad 40**: Cotización voluntaria para aumentar tu salario base (hasta ~$108,750 MXN/mes en 2025) y mejorar tu pensión (Ley 73).
""")
