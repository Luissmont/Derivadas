import streamlit as st
import os
os.system('pip install sympy')
import sys
sys.path.append('/home/appuser/.local/lib/python3.11/site-packages')
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import re


# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Derivadas",
    page_icon="🧮",
    layout="wide"
)


# ======= ESTILOS =========
st.markdown("""
    <style>
        /* Fondo general */
        body {
            background-color: #1e1e2f;
        }
        /* Contenedor principal */
        .stApp {
            background: linear-gradient(135deg, #2c2c3e, #3a3a5a);
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
            color: white;
        }
        /* Sidebar con otro color */
        .stSidebar {
            background-color: #252540 !important;
            padding: 20px;
            border-radius: 10px;
            color: white;
        }
        /* Botones */
        .stButton>button {
            background-color: #ff9800;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px;
            width: 100%;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #e68900;
        }
        /* Botón de borrar */
        .backspace-button>button {
            background-color: #f44336;
        }
        .backspace-button>button:hover {
            background-color: #d32f2f;
        }
        /* Inputs */
        .stTextInput>div>div>input {
            border: 2px solid #ff9800;
            border-radius: 5px;
            padding: 10px;
            background-color: #44445a;
            color: white;
        }
        /* Sliders */
        .stSlider>div>div {
            color: white;
        }
        /* Divider */
        .stDivider {
            border-color: #ff9800;
        }
        /* Teclado matemático */
        .teclado-container {
            background-color: #33334d;
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
        }
        /* Contenedor de vista previa */
        .preview-container {
            background-color: #44445a;
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
            border: 1px solid #ff9800;
            text-align: center;
        }
        /* Paso a paso */
        .steps-container {
            background-color: #44445a;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            border: 2px solid #4caf50;
        }
        .step-title {
            background-color: #4caf50;
            color: white;
            padding: 8px 15px;
            border-radius: 5px;
            margin-bottom: 10px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)


# Función para convertir la expresión a LaTeX de forma segura
def expresion_a_latex(expresion):
    if not expresion:
        return "\\text{Ingresa una expresión...}"
    
    try:
        # Intenta convertir directamente a sympy y luego a latex
        expr = sp.sympify(expresion)
        return sp.latex(expr)
    except:
        # Si falla, hacemos una conversión manual aproximada
        # Esta es una versión simplificada que maneja algunos casos comunes
        expr = expresion
        
        # Sustituir operaciones básicas
        expr = expr.replace("**", "^")
        
        # Intentar hacer más legible la multiplicación
        expr = re.sub(r'(\d+)\*([a-zA-Z])', r'\1\2', expr)
        
        # Funciones comunes
        expr = expr.replace("sqrt(", "\\sqrt{")
        expr = expr.replace("sin(", "\\sin(")
        expr = expr.replace("cos(", "\\cos(")
        expr = expr.replace("tan(", "\\tan(")
        expr = expr.replace("log(", "\\log(")
        expr = expr.replace("ln(", "\\ln(")
        expr = expr.replace("pi", "\\pi")
        expr = expr.replace("exp(1)", "e")
        
        # Cerrar paréntesis de funciones como sqrt
        expr = expr.replace(")", "}")
        
        return expr


# NUEVA FUNCIÓN: Generar pasos de derivación
def generar_pasos_derivacion(expr, variable, orden=1):
    """
    Genera los pasos de la derivación usando reglas básicas de cálculo
    """
    x = sp.Symbol(variable)
    pasos = []
    
    # Inicialización
    expresion_actual = expr
    
    for i in range(1, orden + 1):
        # Paso 0: Expresión original para este paso
        if i == 1:
            pasos.append({
                'titulo': "Expresión original",
                'latex': sp.latex(expresion_actual)
            })
        else:
            pasos.append({
                'titulo': f"Expresión para la derivada de orden {i}",
                'latex': sp.latex(expresion_actual)
            })
            
        # Verifica si la expresión es una suma y la descompone
        if expresion_actual.is_Add:
            terminos = expresion_actual.args
            pasos.append({
                'titulo': "Regla de la suma",
                'latex': f"\\frac{{d}}{{d{variable}}}\\left({sp.latex(expresion_actual)}\\right) = " + 
                         " + ".join([f"\\frac{{d}}{{d{variable}}}\\left({sp.latex(termino)}\\right)" for termino in terminos])
            })
            
            # Derivar cada término
            nuevos_terminos = []
            for termino in terminos:
                derivada_termino = sp.diff(termino, x)
                nuevos_terminos.append(derivada_termino)
                
                # Pasos específicos para cada término según las reglas de derivación
                if termino.is_Pow and termino.args[0] == x:  # Potencia: x^n
                    potencia = termino.args[1]
                    pasos.append({
                        'titulo': f"Regla de la potencia para {sp.latex(termino)}",
                        'latex': f"\\frac{{d}}{{d{variable}}}\\left({sp.latex(termino)}\\right) = " +
                                 f"{sp.latex(potencia)} \\cdot {variable}^{{{sp.latex(potencia-1)}}} = {sp.latex(derivada_termino)}"
                    })
                elif termino.is_Mul:  # Producto: u*v
                    factores = termino.args
                    if len(factores) == 2 and x in factores:
                        u, v = factores
                        if x not in u.free_symbols:  # constante * x
                            pasos.append({
                                'titulo': f"Regla del producto con constante para {sp.latex(termino)}",
                                'latex': f"\\frac{{d}}{{d{variable}}}\\left({sp.latex(termino)}\\right) = " +
                                         f"{sp.latex(u)} \\cdot \\frac{{d}}{{d{variable}}}\\left({sp.latex(v)}\\right) = {sp.latex(derivada_termino)}"
                            })
                    else:
                        pasos.append({
                            'titulo': f"Derivada del término {sp.latex(termino)}",
                            'latex': f"\\frac{{d}}{{d{variable}}}\\left({sp.latex(termino)}\\right) = {sp.latex(derivada_termino)}"
                        })
                elif termino.has(sp.sin) or termino.has(sp.cos) or termino.has(sp.tan):  # Funciones trigonométricas
                    func_name = "seno" if termino.has(sp.sin) else "coseno" if termino.has(sp.cos) else "tangente"
                    pasos.append({
                        'titulo': f"Regla de derivación de {func_name}",
                        'latex': f"\\frac{{d}}{{d{variable}}}\\left({sp.latex(termino)}\\right) = {sp.latex(derivada_termino)}"
                    })
                elif termino.has(sp.exp):  # Función exponencial
                    pasos.append({
                        'titulo': f"Regla de derivación exponencial para {sp.latex(termino)}",
                        'latex': f"\\frac{{d}}{{d{variable}}}\\left({sp.latex(termino)}\\right) = {sp.latex(derivada_termino)}"
                    })
                elif termino.has(sp.log):  # Función logarítmica
                    pasos.append({
                        'titulo': f"Regla de derivación logarítmica para {sp.latex(termino)}",
                        'latex': f"\\frac{{d}}{{d{variable}}}\\left({sp.latex(termino)}\\right) = {sp.latex(derivada_termino)}"
                    })
                elif termino == x:  # Caso simple: x
                    pasos.append({
                        'titulo': f"Derivada de {variable}",
                        'latex': f"\\frac{{d}}{{d{variable}}}\\left({variable}\\right) = 1"
                    })
                elif termino.is_number:  # Constante
                    pasos.append({
                        'titulo': "Regla de la constante",
                        'latex': f"\\frac{{d}}{{d{variable}}}\\left({sp.latex(termino)}\\right) = 0"
                    })
                else:
                    # Cualquier otro caso
                    pasos.append({
                        'titulo': f"Derivada del término {sp.latex(termino)}",
                        'latex': f"\\frac{{d}}{{d{variable}}}\\left({sp.latex(termino)}\\right) = {sp.latex(derivada_termino)}"
                    })
            
            # Resultado combinado
            expresion_actual = sum(nuevos_terminos)
            pasos.append({
                'titulo': f"Resultado de la derivada {i}",
                'latex': f"\\frac{{d{'^'+str(i) if i>1 else ''}}}{{d{variable}{'^'+str(i) if i>1 else ''}}}\\left({sp.latex(expr)}\\right) = {sp.latex(expresion_actual)}"
            })
        else:
            # Para expresiones que no son sumas, manejamos directamente
            derivada = sp.diff(expresion_actual, x)
            
            # Detectar regla aplicada y mostrar paso específico
            if expresion_actual.is_Pow and expresion_actual.args[0] == x:  # Potencia
                potencia = expresion_actual.args[1]
                pasos.append({
                    'titulo': "Regla de la potencia",
                    'latex': f"\\frac{{d}}{{d{variable}}}\\left({variable}^{{{sp.latex(potencia)}}}\\right) = " +
                             f"{sp.latex(potencia)} \\cdot {variable}^{{{sp.latex(potencia-1)}}} = {sp.latex(derivada)}"
                })
            elif expresion_actual.has(sp.sin):  # Función seno
                pasos.append({
                    'titulo': "Regla del seno",
                    'latex': f"\\frac{{d}}{{d{variable}}}\\sin({variable}) = \\cos({variable})"
                })
            elif expresion_actual.has(sp.cos):  # Función coseno
                pasos.append({
                    'titulo': "Regla del coseno",
                    'latex': f"\\frac{{d}}{{d{variable}}}\\cos({variable}) = -\\sin({variable})"
                })
            elif expresion_actual.has(sp.exp):  # Función exponencial
                pasos.append({
                    'titulo': "Regla exponencial",
                    'latex': f"\\frac{{d}}{{d{variable}}}e^{{{variable}}} = e^{{{variable}}}"
                })
            else:
                # Caso general
                pasos.append({
                    'titulo': "Aplicando regla de derivación",
                    'latex': f"\\frac{{d}}{{d{variable}}}\\left({sp.latex(expresion_actual)}\\right) = {sp.latex(derivada)}"
                })
            
            expresion_actual = derivada
            pasos.append({
                'titulo': f"Resultado de la derivada {i}",
                'latex': f"\\frac{{d{'^'+str(i) if i>1 else ''}}}{{d{variable}{'^'+str(i) if i>1 else ''}}}\\left({sp.latex(expr)}\\right) = {sp.latex(expresion_actual)}"
            })
            
    return pasos


# Función para insertar símbolos
def insertar_simbolo(simbolo, agregar=True):
    if not agregar or "funcion" not in st.session_state:
        st.session_state.funcion = simbolo
    else:
        st.session_state.funcion += simbolo


# Función para borrar último carácter
def borrar_ultimo_caracter():
    if "funcion" in st.session_state and st.session_state.funcion:
        st.session_state.funcion = st.session_state.funcion[:-1]


# ===== SIDEBAR =====
# ===== SIDEBAR =====
with st.sidebar:
    st.title("⚙️ Opciones")
    variable = st.selectbox("Variable de derivación:", ["x", "y", "z"])
    orden = st.slider("Orden de derivada:", 1, 5, 1)
    
    # Opciones avanzadas
    st.divider()
    with st.expander("🛠️ Opciones avanzadas"):
        mostrar_pasos = st.checkbox("Mostrar paso a paso", value=True)
        mostrar_grafico = st.checkbox("Mostrar gráfico", value=True)
        mostrar_tabla = st.checkbox("Mostrar tabla de valores", value=True)
    
    # AÑADIR AQUÍ LA SECCIÓN DE AYUDA Y TUTORIALES
    st.divider()
    with st.expander("❓ Ayuda y Tutoriales"):
        st.markdown("""
        ## 🔍 Guía Rápida
        
        ### ✏️ Sintaxis correcta:
        - **Multiplicación**: Usa `*` siempre (ejemplo: `2*x` no `2x`)
        - **Potencias**: Usa `**` (ejemplo: `x**2` para x²)
        - **Paréntesis**: Asegúrate de cerrarlos correctamente
        
        ### 📊 Funciones disponibles:
        - **Básicas**: `+`, `-`, `*`, `/`, `**` (potencia)
        - **Trigonométricas**: `sin()`, `cos()`, `tan()`
        - **Logarítmicas**: `log()` (base 10), `ln()` (natural)
        - **Otras**: `sqrt()` (raíz cuadrada), `abs()` (valor absoluto)
        
        ### 🧮 Constantes especiales:
        - **Pi**: `pi`
        - **Euler (e)**: `exp(1)`
        
        ## 📚 Mini-Tutorial
        
        1. **Ingresa una función** usando el teclado o la entrada de texto
        2. **Selecciona la variable** respecto a la que quieres derivar
        3. **Elige el orden** de la derivada (1 para primera derivada)
        4. **Explora los resultados** en la visualización, paso a paso y tabla
        
        ## 🚫 Errores comunes
        
        - **"Syntax Error"**: Revisa paréntesis, operadores y sintaxis
        - **Multiplicación implícita**: Escribe `2*x` en lugar de `2x`
        - **Divisiones complejas**: Usa paréntesis para agrupar (ejemplo: `(x+1)/(x-2)`)
        """)
        
    
    st.divider()
    with st.expander("📌 Ejemplos rápidos"):
        # Tus ejemplos actuales aquí...
        if st.button("x² + y", key="ejemplo1"):
            st.session_state.funcion = "x**2 + y"
        if st.button("sin(x)*cos(y)", key="ejemplo2"):
            st.session_state.funcion = "sin(x)*cos(y)"
        if st.button("2*x**2 + 3*x + 5", key="ejemplo3"):
            st.session_state.funcion = "2*x**2 + 3*x + 5"
        if st.button("x**3 - 6*x**2 + 9*x", key="ejemplo4"):
            st.session_state.funcion = "x**3 - 6*x**2 + 9*x"
        if st.button("exp(x)", key="ejemplo5"):
            st.session_state.funcion = "exp(x)"
        if st.button("x³ + 2x - 5", key="ejemplo6"):
            st.session_state.funcion = "x**3 + 2*x - 5"
        if st.button("ln(x) + e^x", key="ejemplo7"):
            st.session_state.funcion = "log(x) + exp(x)"
        if st.button("1 / (x + 1)", key="ejemplo8"):
            st.session_state.funcion = "1 / (x + 1)"
        if st.button("tan(x) + cos(x)", key="ejemplo9"):
            st.session_state.funcion = "tan(x) + cos(x)"
        if st.button("sqrt(x) * log(x)", key="ejemplo10"):
            st.session_state.funcion = "sqrt(x) * log(x)"
        if st.button("x^5 - 4x^3 + 2x", key="ejemplo11"):
            st.session_state.funcion = "x**5 - 4*x**3 + 2*x"
        if st.button("Clear", type="secondary", key="clear_sidebar"):
            st.session_state.funcion = ""


# ===== ÁREA PRINCIPAL =====
st.title("🧮 Calculadora de Derivadas")


# Inicializar la variable funcion en session_state si no existe
if "funcion" not in st.session_state:
    st.session_state.funcion = ""


funcion = st.text_input(
    "✏️ Ingresa la función:",
    value=st.session_state.funcion,
    placeholder="Usa el teclado o escribe manualmente",
    key="funcion_input"
)


# Mantener sincronizado el valor del input con session_state
if funcion != st.session_state.funcion:
    st.session_state.funcion = funcion


# Vista previa en tiempo real de la ecuación
with st.container():
    st.markdown('<div class="preview-container">', unsafe_allow_html=True)
    st.subheader("Vista Previa de la Ecuación")
    
    # Mostrar ecuación en formato LaTeX
    if funcion:
        latex_expr = expresion_a_latex(funcion)
        st.latex(latex_expr)
    else:
        st.markdown("*La vista previa aparecerá aquí mientras escribes...*")
    
    # Mensaje de ayuda sobre multiplicación
    st.caption("⚠️ Recuerda: Para multiplicar una constante y una variable usa el operador * (ejemplo: 2*x en lugar de 2x)")
    
    st.markdown('</div>', unsafe_allow_html=True)


# Teclado matemático debajo del input
with st.container():
    st.markdown('<div class="teclado-container">', unsafe_allow_html=True)
    st.subheader("Teclado Matemático")
    
    # Fila de control con botones de acción 
    cols = st.columns([1, 1, 2])
    with cols[0]:
        # Botón Backspace (Borrar último carácter)
        st.markdown('<div class="backspace-button">', unsafe_allow_html=True)
        st.button("⌫ Backspace", on_click=borrar_ultimo_caracter, key="btn_backspace")
        st.markdown('</div>', unsafe_allow_html=True)
    with cols[1]:
        # Botón de limpiar
        st.button("🗑️ Clear", on_click=insertar_simbolo, args=("", False), key="btn_clear_main")
    with cols[2]:
        # Indicador de estado actual
        if funcion:
            st.info(f"Caracteres: {len(funcion)}")
        else:
            st.info("Sin entrada")
    
    # Primera fila - Números
    cols = st.columns(10)
    for i in range(10):
        with cols[i]: st.button(f"{i}", on_click=insertar_simbolo, args=(f"{i}",), key=f"btn_{i}")
    
    # Segunda fila - Operadores básicos
    cols = st.columns(6)
    with cols[0]: st.button("+", on_click=insertar_simbolo, args=("+",), key="btn_suma")
    with cols[1]: st.button("-", on_click=insertar_simbolo, args=("-",), key="btn_resta")
    with cols[2]: st.button("×", on_click=insertar_simbolo, args=("*",), key="btn_mult")
    with cols[3]: st.button("÷", on_click=insertar_simbolo, args=("/",), key="btn_div")
    with cols[4]: st.button("x²", on_click=insertar_simbolo, args=("**2",), key="btn_cuad")
    with cols[5]: st.button("xʸ", on_click=insertar_simbolo, args=("**",), key="btn_pot")
    
    # Tercera fila - Funciones
    cols = st.columns(6)
    with cols[0]: st.button("√", on_click=insertar_simbolo, args=("sqrt(",), key="btn_sqrt")
    with cols[1]: st.button("(", on_click=insertar_simbolo, args=("(",), key="btn_par_izq")
    with cols[2]: st.button(")", on_click=insertar_simbolo, args=(")",), key="btn_par_der")
    with cols[3]: st.button("sin", on_click=insertar_simbolo, args=("sin(",), key="btn_sin")
    with cols[4]: st.button("cos", on_click=insertar_simbolo, args=("cos(",), key="btn_cos")
    with cols[5]: st.button("tan", on_click=insertar_simbolo, args=("tan(",), key="btn_tan")
    
    # Cuarta fila - Constantes y funciones
    cols = st.columns(6)
    with cols[0]: st.button("π", on_click=insertar_simbolo, args=("pi",), key="btn_pi")
    with cols[1]: st.button("e", on_click=insertar_simbolo, args=("exp(1)",), key="btn_e")
    with cols[2]: st.button("log", on_click=insertar_simbolo, args=("log(",), key="btn_log")
    with cols[3]: st.button("ln", on_click=insertar_simbolo, args=("ln(",), key="btn_ln")
    with cols[4]: st.button("|x|", on_click=insertar_simbolo, args=("abs(",), key="btn_abs")
    with cols[5]: st.button("=", on_click=insertar_simbolo, args=("=",), key="btn_igual")
    
    # Quinta fila - Variables
    cols = st.columns(6)
    with cols[0]: st.button("x", on_click=insertar_simbolo, args=("x",), key="btn_x")
    with cols[1]: st.button("y", on_click=insertar_simbolo, args=("y",), key="btn_y")
    with cols[2]: st.button("z", on_click=insertar_simbolo, args=("z",), key="btn_z")
    with cols[3]: st.button("t", on_click=insertar_simbolo, args=("t",), key="btn_t")
    with cols[4]: st.button(",", on_click=insertar_simbolo, args=(",",), key="btn_coma")
    with cols[5]: st.button(".", on_click=insertar_simbolo, args=(".",), key="btn_punto")
    
    st.markdown('</div>', unsafe_allow_html=True)


# Cálculo y gráficos
if funcion:
    try:
        # Cálculo simbólico
        x = sp.symbols(variable)
        expr = sp.sympify(funcion)
        derivada = sp.diff(expr, x, orden)
        
        st.divider()
        st.subheader(f"📢 Derivada de orden {orden} respecto a {variable}:")
        st.latex(f"\\frac{{\\partial^{orden}}}{{\\partial {variable}^{orden}}}({sp.latex(expr)}) = {sp.latex(derivada)}")
        
        # NUEVA CARACTERÍSTICA: Paso a paso de la derivación
        if mostrar_pasos:
            st.markdown('<div class="steps-container">', unsafe_allow_html=True)
            st.subheader("🔍 Paso a paso de la derivación")
            
            try:
                pasos = generar_pasos_derivacion(expr, variable, orden)
                
                for i, paso in enumerate(pasos):
                    st.markdown(f'<div class="step-title">Paso {i+1}: {paso["titulo"]}</div>', unsafe_allow_html=True)
                    st.latex(paso["latex"])
                    
            except Exception as e:
                st.warning(f"No se pudieron generar los pasos detallados: {str(e)}")
                st.write("La derivada se calculó correctamente, pero no podemos mostrar el paso a paso para esta función.")           
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Gráfico
        if mostrar_grafico:
            st.subheader("📊 Gráfico:")
            try:
                f = sp.lambdify(x, expr, 'numpy')
                df = sp.lambdify(x, derivada, 'numpy')
                x_vals = np.linspace(-5, 5, 400)
                
                # Evitar errores de dominio en la gráfica
                try:
                    y_vals = f(x_vals)
                    dy_vals = df(x_vals)
                    
                    valid_f = np.isfinite(y_vals)
                    valid_df = np.isfinite(dy_vals)
                    
                    fig, ax = plt.subplots(figsize=(10, 5))
                    
                    if np.any(valid_f):
                        ax.plot(x_vals[valid_f], y_vals[valid_f], label=f'f({variable})', color='blue')
                    if np.any(valid_df):
                        ax.plot(x_vals[valid_df], dy_vals[valid_df], label=f'Derivada', color='red', linestyle='--')
                    
                    ax.legend()
                    ax.grid(True)
                    ax.set_title(f"Función y su derivada de orden {orden}")
                    ax.set_xlabel(variable)
                    ax.set_ylabel("Valor")
                    
                    # Mejorar límites para visualización
                    try:
                        if np.any(valid_f) and np.any(valid_df):
                            y_min = min(np.min(y_vals[valid_f]), np.min(dy_vals[valid_df]))
                            y_max = max(np.max(y_vals[valid_f]), np.max(dy_vals[valid_df]))
                            
                            # Evitar gráficos demasiado extremos
                            if abs(y_max - y_min) > 100:
                                # Usar un rango más razonable
                                ax.set_ylim(-10, 10)
                            else:
                                # Añadir un margen
                                margin = (y_max - y_min) * 0.1
                                ax.set_ylim(y_min - margin, y_max + margin)
                    except:
                        # En caso de error, usar límites predeterminados
                        pass
                        
                    st.pyplot(fig)
                except Exception as e:
                    st.warning(f"Error en cálculos numéricos: {str(e)}")
                    
                    # Mostrar una representación simbólica en su lugar
                    st.write("No se puede generar el gráfico numérico. Mostrando representación simbólica:")
                    st.latex(f"f({variable}) = {sp.latex(expr)}")
                    st.latex(f"f'({variable}) = {sp.latex(derivada)}")
                
            except Exception as e:
                st.warning(f"No se pudo generar el gráfico: {str(e)}")
                st.write("La derivada se calculó correctamente, pero la función no puede graficarse en el dominio seleccionado.")
        
        # Tabla de valores
        if mostrar_tabla:
            st.subheader("📝 Valores numéricos de la derivada:")
            puntos = [-2, -1, 0, 1, 2]
            
            # Crear tabla de valores
            data = []
            for punto in puntos:
                try:
                    valor_funcion = float(expr.subs(x, punto))
                    valor_derivada = float(derivada.subs(x, punto))
                    data.append([punto, valor_funcion, valor_derivada])
                except:
                    # Si hay un error (como división por cero), mostramos "Indefinido"
                    try:
                        valor_funcion = float(expr.subs(x, punto))
                        data.append([punto, valor_funcion, "Indefinido"])
                    except:
                        data.append([punto, "Indefinido", "Indefinido"])
            
            if data:
                st.write("Valores en puntos clave:")
                st.table({
                    f"{variable}": [d[0] for d in data],
                    f"f({variable})": [d[1] for d in data],
                    f"f{'^'+str(orden) if orden>1 else ''}'({variable})": [d[2] for d in data]
                })
        
    except Exception as e:
        st.error(f"Error en el cálculo: {str(e)}")
        st.info("Verifica la sintaxis de la función. Recuerda usar '*' para multiplicación explícita (ejemplo: 2*x en lugar de 2x).")


# Footer
st.divider()
st.caption("✨ Calculadora de Derivadas con Paso a Paso | Streamlit")