from datetime import date
import streamlit as st

# Constantes
UMA_DIARIA = 108.57
DIAS_POR_MES = 30.4
UMA_MENSUAL = UMA_DIARIA * DIAS_POR_MES

# Tabla de porcentajes según edad de retiro (Ley 73)
porcentajes_edad = {
    60: 0.75,
    61: 0.80,
    62: 0.85,
    63: 0.90,
    64: 0.95,
    65: 1.00
}

# Funciones
def calcular_edad(fecha_nac):
    hoy = date.today()
    return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))

def semanas_totales(actuales, mod10=0, mod40=0):
    return actuales + mod10 + mod40

def calcular_pension(salario_mensual, semanas_totales, edad_retiro):
    salario_diario = salario_mensual / DIAS_POR_MES
    salario_uma = salario_diario / UMA_DIARIA
    semanas_excedentes = max(0, semanas_totales - 500)
    incremento = (semanas_excedentes // 52) * 0.052 * salario_uma
    cuantia_basica_diaria = 1.0 + incremento
    cuantia_mensual = cuantia_basica_diaria * UMA_DIARIA * DIAS_POR_MES
    factor_edad = porcentajes_edad.get(edad_retiro, 1.0)
    return round(cuantia_mensual * factor_edad, 2)

def calcular_costo_m40(salario_mensual):
    return round(salario_mensual * 0.10075, 2)

def calcular_recuperacion(inversion_total, pension_mensual):
    if pension_mensual == 0:
        return None
    return round(inversion_total / pension_mensual, 1)

# Interfaz
st.set_page_config(page_title="Calculadora IMSS", layout="centered")
st.title("🧮 Calculadora de Pensión IMSS (Ley 73) – Modalidades 10 y 40")

# Datos personales
fecha_nac = st.date_input("📅 Fecha de nacimiento")
anio_alta = st.number_input("🧾 Año de alta en el IMSS", min_value=1950, max_value=2025, value=1996)
respuesta_pre97 = st.radio("¿Cotizaste antes del 1 de julio de 1997?", ["Sí", "No"]) cotiza_pre97 - respuesta_pre97 == "Sí"
edad_actual = calcular_edad(fecha_nac)
st.write(f"👤 Edad actual: **{edad_actual} años**")

# Semanas
semanas_act = st.number_input("🔢 Semanas cotizadas actualmente", min_value=0, value=300)

# Modalidad 10
usa_mod10 = st.checkbox("¿Vas a cotizar en Modalidad 10?")
semanas_mod10 = st.number_input("Semanas en Modalidad 10", 0, 520, value=104) if usa_mod10 else 0
salario_mod10 = st.number_input("Salario mensual en Modalidad 10 ($MXN)", 1000.0, 50000.0, value=12000.0) if usa_mod10 else 0

# Modalidad 40
usa_mod40 = st.checkbox("¿Vas a cotizar en Modalidad 40?")
semanas_mod40 = st.number_input("Semanas en Modalidad 40", 0, 520, value=250) if usa_mod40 else 0
salario_mod40 = st.number_input("Salario mensual en Modalidad 40 ($MXN)", 1000.0, 87750.0, value=50000.0) if usa_mod40 else 0

# Semanas totales proyectadas
total_semanas = semanas_totales(semanas_act, semanas_mod10, semanas_mod40)
st.markdown(f"📈 **Semanas proyectadas totales:** {total_semanas}")

# Edad de retiro
edad_retiro = st.slider("Edad de retiro proyectada", 60, 65, 60)

# Cálculo de pensión
if cotiza_pre97:
    salario_base = salario_mod40 or salario_mod10 or 0
    pension = calcular_pension(salario_base, total_semanas, edad_retiro)
    st.success(f"💵 Pensión estimada a los {edad_retiro}: **${pension:,.2f} MXN mensuales**")
