import streamlit as st

# Parámetros constantes
UMA_DIARIA = 108.57
UMA_MENSUAL = UMA_DIARIA * 30.4

# Porcentajes de pensión según edad (Ley 73)
porcentajes_edad = {
    60: 0.75,
    61: 0.80,
    62: 0.85,
    63: 0.90,
    64: 0.95,
    65: 1.00
}

def calcular_pension(salario_mensual, semanas_totales, edad_retiro):
    salario_diario = salario_mensual / 30.4
    salario_uma = salario_diario / UMA_DIARIA
    semanas_excedentes = max(0, semanas_totales - 500)
    periodos_52 = semanas_excedentes // 52
    incremento = periodos_52 * 0.052 * salario_uma

    cuantia_uma_diaria = 1.0 + incremento
    cuantia_mensual = cuantia_uma_diaria * UMA_DIARIA * 30.4
    factor_edad = porcentajes_edad.get(edad_retiro, 1.0)

    pension_final = cuantia_mensual * factor_edad
    return round(pension_final, 2)

# Interfaz Streamlit
st.title("Calculadora de Pensión IMSS (Ley 73)")

salario_mensual = st.number_input("Salario mensual en Modalidad 40 ($MXN)", min_value=1000.0, value=87750.0, step=1000.0)
semanas_totales = st.number_input("Semanas cotizadas totales", min_value=500, value=654, step=1)
edad_retiro = st.slider("Edad de retiro", min_value=60, max_value=65, value=60)

if st.button("Calcular pensión"):
    pension = calcular_pension(salario_mensual, semanas_totales, edad_retiro)
    st.success(f"Pensión mensual estimada: ${pension:,.2f} MXN")
