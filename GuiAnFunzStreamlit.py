import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --- Configurazione Pagina ---
st.set_page_config(page_title="Plotter Universale", layout="wide")

st.title("📈 Plotter Universale: Funzioni e Successioni")
st.markdown("Analisi di funzioni $y=f(x)$ e successioni $x_{n+1}=f(x_n)$")

# --- Sidebar: Input e Parametri ---
with st.sidebar:
    st.header("Parametri")
    
    # 1. Selezione Modalità
    mode_label = st.radio(
        "Seleziona Tipo di Analisi:",
        ("Funzione y = f(x)", "Successione x(n+1) = f(x(n))")
    )
    mode = 0 if mode_label == "Funzione y = f(x)" else 1

    st.markdown("---")

    # 2. Formula
    if mode == 0:
        default_func = "x**2"
        label_func = "Funzione y = f(x):"
    else:
        default_func = "0.5 * x + 1"
        label_func = "Legge x(n+1) = f(x):" # usa 'x' per x_n

    func_str = st.text_input(label_func, value=default_func, help="Usa sintassi Python: x**2, sin(x), exp(x)...")

    # 3. Range Grafico (Zoom manuale)
    n_limit = st.number_input("Range Grafico [±n] (Limiti Assi Y)", value=10.0, step=1.0)

    st.markdown("---")

    # 4. Parametri Dinamici
    if mode == 0:
        st.subheader("Intervallo X")
        col1, col2 = st.columns(2)
        with col1:
            x_s = st.number_input("Da (Inizio)", value=-5.0)
        with col2:
            x_e = st.number_input("A (Fine)", value=5.0)
        x_step_val = st.number_input("Incremento", value=0.1, format="%.4f")
    else:
        st.subheader("Parametri Successione")
        seq_start = st.number_input("Valore Iniziale (x0)", value=0.5)
        seq_iters = st.number_input("Numero Iterazioni (n max)", value=20, step=1, min_value=1)

    run_btn = st.button("Esegui Analisi", type="primary")

# --- Logica di Calcolo e Plot ---
# In Streamlit lo script gira sempre dall'inizio alla fine. 
# Usiamo il bottone o lasciamo che si aggiorni automaticamente.
# Qui mettiamo il codice principale.

if func_str: # Esegue solo se c'è una funzione scritta
    try:
        # Preparazione ambiente matematico sicuro
        allowed_math = {
            "sin": np.sin, "cos": np.cos, "tan": np.tan, 
            "exp": np.exp, "log": np.log, "sqrt": np.sqrt, 
            "pi": np.pi, "abs": np.abs, "np": np
        }

        # Creazione Tabella e Grafico
        fig, ax = plt.subplots(figsize=(8, 5))
        
        df_result = None

        if mode == 0:
            # --- FUNZIONE ---
            if x_step_val <= 0:
                st.error("L'incremento deve essere > 0")
                st.stop()

            # Generazione X
            x_data = np.arange(x_s, x_e + (x_step_val/1000), x_step_val)
            allowed_math["x"] = x_data
            
            # Calcolo Y
            y_data = eval(func_str, {"__builtins__": {}}, allowed_math)
            
            # Gestione scalari (es: y=5)
            if isinstance(y_data, (int, float)):
                y_data = np.full_like(x_data, y_data)

            # Plot
            ax.plot(x_data, y_data, label=f"y={func_str}", color='blue')
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            
            # Limiti
            ax.set_xlim(-n_limit, n_limit) # O user defined se volessimo
            ax.set_ylim(-n_limit, n_limit)

            # DataFrame per visualizzazione dati
            df_result = pd.DataFrame({"X": x_data, "Y": y_data})

        else:
            # --- SUCCESSIONE ---
            x_current = seq_start
            iters = int(seq_iters)
            
            n_data = []
            val_data = []

            for n in range(iters + 1):
                n_data.append(n)
                val_data.append(x_current)
                
                # Calcolo next step
                try:
                    allowed_math["x"] = x_current
                    x_next = eval(func_str, {"__builtins__": {}}, allowed_math)
                    x_current = x_next
                except Exception as e:
                    st.warning(f"Calcolo interrotto a n={n}: {e}")
                    break
                
                if abs(x_current) > 1e100:
                    st.warning("Valore troppo grande (divergenza), stop.")
                    break
            
            # Plot
            ax.plot(n_data, val_data, '-o', label=f"x(n+1)={func_str}", color='red', markersize=4)
            ax.set_xlabel("n (passi)")
            ax.set_ylabel("Valore x(n)")
            
            # Limiti
            ax.set_xlim(0, max(n_data) + 1 if n_data else 10)
            ax.set_ylim(-n_limit, n_limit)

            # DataFrame
            df_result = pd.DataFrame({"n": n_data, "x(n)": val_data})

        # --- Finiture Grafico Comuni ---
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.axhline(0, color='black', linewidth=1)
        if mode == 0: 
            ax.axvline(0, color='black', linewidth=1)
        ax.legend()
        ax.set_title("Grafico Analisi")

        # --- Layout Output Streamlit ---
        col_graph, col_data = st.columns([2, 1])

        with col_graph:
            st.pyplot(fig)
            st.info("💡 Nota: In questa versione web, usa il campo 'Range Grafico' nella barra laterale per zoomare in/out sugli assi.")

        with col_data:
            st.subheader("Dati Numerici")
            if df_result is not None:
                st.dataframe(df_result, height=400, use_container_width=True)

    except Exception as e:
        st.error(f"Errore nella formula o nei calcoli: {e}")