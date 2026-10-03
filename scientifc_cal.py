import streamlit as st
import calculator

# Configure page settings
st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="centered")

# ============================================================
# STATE MANAGEMENT & INITIALIZATION
# ============================================================

if "display" not in st.session_state:
    st.session_state.display = "0"
if "prev_value" not in st.session_state:
    st.session_state.prev_value = None
if "pending_op" not in st.session_state:
    st.session_state.pending_op = None
if "reset_next" not in st.session_state:
    st.session_state.reset_next = False
if "degree_mode" not in st.session_state:
    st.session_state.degree_mode = True
if "error" not in st.session_state:
    st.session_state.error = ""

# ============================================================
# ACTION HANDLERS
# ============================================================

def handle_digit(digit):
    st.session_state.error = ""
    if st.session_state.reset_next or st.session_state.display == "0":
        st.session_state.display = str(digit)
        st.session_state.reset_next = False
    else:
        st.session_state.display += str(digit)

def handle_dot():
    st.session_state.error = ""
    if st.session_state.reset_next:
        st.session_state.display = "0."
        st.session_state.reset_next = False
    elif "." not in st.session_state.display:
        st.session_state.display += "."

def handle_clear():
    st.session_state.display = "0"
    st.session_state.prev_value = None
    st.session_state.pending_op = None
    st.session_state.reset_next = False
    st.session_state.error = ""

def handle_backspace():
    st.session_state.error = ""
    if len(st.session_state.display) > 1:
        st.session_state.display = st.session_state.display[:-1]
    else:
        st.session_state.display = "0"

def eval_expression(expr):
    """Parse keyboard formulas safely using the calculator functions."""
    expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**")
    
    safe_dict = {
        "sin": lambda x: calculator.sin(x, st.session_state.degree_mode),
        "cos": lambda x: calculator.cos(x, st.session_state.degree_mode),
        "tan": lambda x: calculator.tan(x, st.session_state.degree_mode),
        "sqrt": calculator.square_root,
        "log": calculator.log10,
        "ln": calculator.natural_log,
        "pi": calculator.PI,
        "e": calculator.E,
        "abs": calculator.absolute,
        "fact": calculator.factorial
    }
    try:
        return eval(expr, {"__builtins__": None}, safe_dict)
    except Exception:
        return float(expr)

def handle_binary_op(op_name):
    st.session_state.error = ""
    try:
        current_val = float(eval_expression(st.session_state.display))
        if st.session_state.pending_op and st.session_state.prev_value is not None:
            execute_equals()
            st.session_state.prev_value = float(st.session_state.display)
        else:
            st.session_state.prev_value = current_val
            
        st.session_state.pending_op = op_name
        st.session_state.reset_next = True
    except Exception as e:
        st.session_state.error = f"Invalid expression: {e}"

def execute_equals():
    st.session_state.error = ""
    try:
        if st.session_state.pending_op is not None and st.session_state.prev_value is not None:
            val1 = st.session_state.prev_value
            val2 = float(eval_expression(st.session_state.display))
            op = st.session_state.pending_op

            if op == "+":
                res = calculator.add(val1, val2)
            elif op == "-":
                res = calculator.subtract(val1, val2)
            elif op == "×":
                res = calculator.multiply(val1, val2)
            elif op == "÷":
                res = calculator.divide(val1, val2)
            elif op == "x^y":
                res = calculator.power(val1, val2)

            st.session_state.prev_value = None
            st.session_state.pending_op = None
        else:
            res = eval_expression(st.session_state.display)

        if res == int(res):
            st.session_state.display = str(int(res))
        else:
            st.session_state.display = str(round(res, 8))

        st.session_state.reset_next = True
    except Exception as e:
        st.session_state.error = str(e)

def handle_unary_op(func_name):
    st.session_state.error = ""
    try:
        val = float(eval_expression(st.session_state.display))
        res = 0

        if func_name == "x²":
            res = calculator.square(val)
        elif func_name == "x³":
            res = calculator.cube(val)
        elif func_name == "√x":
            res = calculator.square_root(val)
        elif func_name == "∛x":
            res = calculator.cube_root(val)
        elif func_name == "%":
            res = calculator.percentage(val)
        elif func_name == "±":
            res = calculator.change_sign(val)
        elif func_name == "ln":
            res = calculator.natural_log(val)
        elif func_name == "log₁₀":
            res = calculator.log10(val)
        elif func_name == "log₂":
            res = calculator.log2(val)
        elif func_name == "sin":
            res = calculator.sin(val, st.session_state.degree_mode)
        elif func_name == "cos":
            res = calculator.cos(val, st.session_state.degree_mode)
        elif func_name == "tan":
            res = calculator.tan(val, st.session_state.degree_mode)
        elif func_name == "asin":
            res = calculator.asin(val, st.session_state.degree_mode)
        elif func_name == "acos":
            res = calculator.acos(val, st.session_state.degree_mode)
        elif func_name == "atan":
            res = calculator.atan(val, st.session_state.degree_mode)
        elif func_name == "sinh":
            res = calculator.sinh(val)
        elif func_name == "cosh":
            res = calculator.cosh(val)
        elif func_name == "tanh":
            res = calculator.tanh(val)
        elif func_name == "asinh":
            res = calculator.asinh(val)
        elif func_name == "acosh":
            res = calculator.acosh(val)
        elif func_name == "atanh":
            res = calculator.atanh(val)
        elif func_name == "x!":
            res = calculator.factorial(val)
        elif func_name == "|x|":
            res = calculator.absolute(val)
        elif func_name == "floor":
            res = calculator.floor(val)
        elif func_name == "ceil":
            res = calculator.ceil(val)

        if res == int(res):
            st.session_state.display = str(int(res))
        else:
            st.session_state.display = str(round(res, 8))

        st.session_state.reset_next = True
    except Exception as e:
        st.session_state.error = str(e)

def handle_constant(const_val):
    st.session_state.error = ""
    st.session_state.display = str(round(const_val, 8))
    st.session_state.reset_next = True

def handle_typed_expression():
    typed = st.session_state.keyboard_input
    if typed.strip():
        st.session_state.display = typed
        execute_equals()

# ============================================================
# STYLING
# ============================================================

st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    div.stButton > button {
        width: 100%;
        height: 52px;
        font-size: 16px;
        font-weight: 600;
        border-radius: 8px;
        border: 1px solid #30363d;
        background-color: #21262d;
        color: #f0f6fc;
        margin-bottom: 5px;
    }
    div.stButton > button:hover {
        background-color: #30363d;
        border-color: #8b949e;
    }
    .display-screen {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 15px 20px;
        text-align: right;
        font-size: 32px;
        font-weight: bold;
        font-family: monospace;
        color: #58a6ff;
        margin-bottom: 15px;
        word-wrap: break-word;
    }
    .sub-display {
        font-size: 13px;
        color: #8b949e;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# UI LAYOUT
# ============================================================

st.title("🧮 Scientific Calculator By Jameel Shah")

# Header indicator
sub_info = f"MODE: {'DEG' if st.session_state.degree_mode else 'RAD'}"
if st.session_state.pending_op and st.session_state.prev_value is not None:
    sub_info += f" | {st.session_state.prev_value} {st.session_state.pending_op}"

# Instant responsive HTML display screen
st.markdown(f"""
<div class="display-screen">
    <div class="sub-display">{sub_info}</div>
    {st.session_state.display}
</div>
""", unsafe_allow_html=True)

if st.session_state.error:
    st.error(st.session_state.error)

# Keyboard Input Box for typing expressions directly
st.text_input(
    label="Type math expression here (e.g., 5+10, sqrt(16), sin(45)) and press Enter:",
    key="keyboard_input",
    on_change=handle_typed_expression,
    placeholder="Type expression and press Enter..."
)

# Mode Toggle
st.session_state.degree_mode = st.toggle("Degrees Mode (DEG/RAD)", value=st.session_state.degree_mode)

# Tabbed Interface for Advanced Functions
tab1, tab2, tab3 = st.tabs(["Trig & Hyperbolic", "Powers & Logs", "Misc & Constants"])

with tab1:
    c1, c2, c3 = st.columns(3)
    if c1.button("sin", key="btn_sin"): handle_unary_op("sin")
    if c2.button("cos", key="btn_cos"): handle_unary_op("cos")
    if c3.button("tan", key="btn_tan"): handle_unary_op("tan")
    
    if c1.button("asin", key="btn_asin"): handle_unary_op("asin")
    if c2.button("acos", key="btn_acos"): handle_unary_op("acos")
    if c3.button("atan", key="btn_atan"): handle_unary_op("atan")

    if c1.button("sinh", key="btn_sinh"): handle_unary_op("sinh")
    if c2.button("cosh", key="btn_cosh"): handle_unary_op("cosh")
    if c3.button("tanh", key="btn_tanh"): handle_unary_op("tanh")

    if c1.button("asinh", key="btn_asinh"): handle_unary_op("asinh")
    if c2.button("acosh", key="btn_acosh"): handle_unary_op("acosh")
    if c3.button("atanh", key="btn_atanh"): handle_unary_op("atanh")

with tab2:
    c1, c2, c3 = st.columns(3)
    if c1.button("x²", key="btn_sq"): handle_unary_op("x²")
    if c2.button("x³", key="btn_cube"): handle_unary_op("x³")
    if c3.button("x^y", key="btn_pow"): handle_binary_op("x^y")

    if c1.button("√x", key="btn_sqrt"): handle_unary_op("√x")
    if c2.button("∛x", key="btn_cbrt"): handle_unary_op("∛x")
    if c3.button("%", key="btn_pct_tab"): handle_unary_op("%")

    if c1.button("ln", key="btn_ln"): handle_unary_op("ln")
    if c2.button("log₁₀", key="btn_log10"): handle_unary_op("log₁₀")
    if c3.button("log₂", key="btn_log2"): handle_unary_op("log₂")

with tab3:
    c1, c2, c3 = st.columns(3)
    if c1.button("x!", key="btn_fact"): handle_unary_op("x!")
    if c2.button("|x|", key="btn_abs"): handle_unary_op("|x|")
    if c3.button("±", key="btn_sign_tab"): handle_unary_op("±")

    if c1.button("floor", key="btn_floor"): handle_unary_op("floor")
    if c2.button("ceil", key="btn_ceil"): handle_unary_op("ceil")
    if c3.button("π", key="btn_pi"): handle_constant(calculator.PI)

    if c1.button("e", key="btn_e"): handle_constant(calculator.E)
    if c2.button("τ (Tau)", key="btn_tau"): handle_constant(calculator.TAU)

st.divider()

# Main Number Pad Grid
row1 = st.columns(4)
if row1[0].button("C", key="btn_clear"): handle_clear()
if row1[1].button("⌫", key="btn_back"): handle_backspace()
if row1[2].button("%", key="btn_pct_grid"): handle_unary_op("%")
if row1[3].button("÷", key="btn_div"): handle_binary_op("÷")

row2 = st.columns(4)
if row2[0].button("7", key="btn_7"): handle_digit("7")
if row2[1].button("8", key="btn_8"): handle_digit("8")
if row2[2].button("9", key="btn_9"): handle_digit("9")
if row2[3].button("×", key="btn_mul"): handle_binary_op("×")

row3 = st.columns(4)
if row3[0].button("4", key="btn_4"): handle_digit("4")
if row3[1].button("5", key="btn_5"): handle_digit("5")
if row3[2].button("6", key="btn_6"): handle_digit("6")
if row3[3].button("-", key="btn_sub"): handle_binary_op("-")

row4 = st.columns(4)
if row4[0].button("1", key="btn_1"): handle_digit("1")
if row4[1].button("2", key="btn_2"): handle_digit("2")
if row4[2].button("3", key="btn_3"): handle_digit("3")
if row4[3].button("+", key="btn_add"): handle_binary_op("+")

row5 = st.columns(4)
if row5[0].button("±", key="btn_sign_grid"): handle_unary_op("±")
if row5[1].button("0", key="btn_0"): handle_digit("0")
if row5[2].button(".", key="btn_dot"): handle_dot()
if row5[3].button("=", key="btn_eq"): execute_equals()