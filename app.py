import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora Pensión IMSS", layout="centered")

st.title("🧮 Calculadora de Pensión IMSS")
st.write("Proyección aproximada según tu régimen de cotización.")

# === Selección de ley ===
ley = st.radio("¿Bajo qué régimen cotizaste por primera vez?", ["Ley 97", "Ley 73"])

# === Entradas generales ===
edad_actual = st.number_input("📅 Edad actual", min_value=18, max_value=100, value=55)
edad_retiro = st.number_input("🎯 Edad estimada de retiro", min_value=60, max_value=100, value=60)
semanas_act = st.number_input("📌 Semanas cotizadas actualmente", min_value=0, max_value=2000, value=720)

# === Variables comunes ===
año_retiro = 2025 + (edad_retiro - edad_actual)
semanas_requeridas_97 = min(1000, 750 + (año_retiro - 2021) * 25)

# === Cálculo para Ley 97 ===
if ley == "Ley 97":
    saldo_afore = st.number_input("💰 Saldo en tu AFORE (MXN)", min_value=0.0, step=1000.0, value=300000.0)
    pension_l97 = saldo_afore * 0.035 / 12  # 3.5% anual estimado
    semanas_faltantes = max(0, semanas_requeridas_97 - semanas_act)
    años_faltantes = semanas_faltantes / 52

    st.subheader("📊 Resultados Ley 97")
    st.write(f"👵 A los **{edad_retiro} años** (en {año_retiro}), recibirías una pensión aproximada de:")
    st.success(f"💸 ${pension_l97:,.2f} MXN/mes")

    if semanas_faltantes > 0:
        st.warning(f"Te faltan **{semanas_faltantes} semanas** (~{años_faltantes:.1f} años) para alcanzar las {int(semanas_requeridas_97)} requeridas.")
    else:
        st.info("✅ Ya cumples con las semanas requeridas.")

# === Cálculo para Ley 73 ===
else:
    salario_promedio = st.number_input("💵 Salario base promedio mensual (últimas 250 semanas)", value=10000.0, step=500.0)
    aplicar_modalidad_40 = st.checkbox("✅ Simular Modalidad 40 para mejorar pensión")

    if aplicar_modalidad_40:
        salario_m40 = st.slider("💹 Salario bajo Modalidad 40", min_value=10000.0, max_value=108750.0, step=500.0, value=25000.0)
        semanas_modalidad = st.slider("📆 Semanas bajo Modalidad 40", min_value=0, max_value=260, step=13, value=104)
        semanas_totales = semanas_act + semanas_modalidad
        salario_promedio = (salario_promedio * semanas_act + salario_m40 * semanas_modalidad) / semanas_totales
    else:
        semanas_totales = semanas_act

    if semanas_totales < 500:
        st.error("❌ Necesitas mínimo 500 semanas cotizadas para recibir pensión bajo Ley 73.")
    else:
        # Estimación sencilla tipo UMA (~96.22/día en 2025)
        pension_l73 = salario_promedio * 0.3  # Se puede mejorar con tabla real IMSS
        st.subheader("📊 Resultados Ley 73")
        st.write(f"👵 Con **{int(semanas_totales)} semanas** y salario base de **${salario_promedio:,.2f}**, tu pensión aproximada sería:")
        st.success(f"💸 ${pension_l73:,.2f} MXN/mes")

# === Explicación final ===
st.markdown("---")
st.markdown("""
### 📘 Explicación rápida
- **Ley 73**: Cotizaste antes de julio 1997. Requiere 500 semanas. Pensión basada en salario promedio (últimas 250 semanas).
- **Ley 97**: Cotizaste desde julio 1997. Requiere de 850 a 1000 semanas. Pensión depende del saldo acumulado en AFORE.
- **Modalidad 40**: Puedes aumentar tus semanas y salario base voluntariamente después de dejar de trabajar formalmente. Aplica solo en Ley 73.

ℹ️ Esta app da un cálculo **estimado**. El monto real puede cambiar según el IMSS y la CONSAR.
""")
