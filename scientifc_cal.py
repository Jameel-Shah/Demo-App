import html
import math
import re

import streamlit as st
import streamlit.components.v1 as components

import calculator

# Configure page settings
st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="centered")

# ============================================================
# STATE MANAGEMENT & INITIALIZATION
# ============================================================
# "display" holds the whole expression the user is building (one single box).

if "display" not in st.session_state:
    st.session_state.display = "0"
if "prev_value" not in st.session_state:      # last evaluated expression (history line)
    st.session_state.prev_value = None
if "pending_op" not in st.session_state:      # kept for compatibility
    st.session_state.pending_op = None
if "reset_next" not in st.session_state:      # True right after "=" shows a result
    st.session_state.reset_next = False
if "degree_mode" not in st.session_state:
    st.session_state.degree_mode = True
if "error" not in st.session_state:
    st.session_state.error = ""

OPERATORS = "+-×÷^"

# Text inserted into the display for each scientific button
FUNCTION_TOKENS = {
    "sin": "sin(", "cos": "cos(", "tan": "tan(",
    "asin": "asin(", "acos": "acos(", "atan": "atan(",
    "sinh": "sinh(", "cosh": "cosh(", "tanh": "tanh(",
    "asinh": "asinh(", "acosh": "acosh(", "atanh": "atanh(",
    "√x": "sqrt(", "∛x": "cbrt(",
    "ln": "ln(", "log₁₀": "log(", "log₂": "log2(",
    "|x|": "abs(", "floor": "floor(", "ceil": "ceil(",
}
# Longest first so "asin(" is matched before "sin(" when backspacing
_TOKENS_BY_LENGTH = sorted(set(FUNCTION_TOKENS.values()), key=len, reverse=True)

# ============================================================
# EXPRESSION ENGINE
# ============================================================

def _expand_factorials(expr):
    """Turn 5! or (2+1)! into fact(5) / fact((2+1))."""
    while "!" in expr:
        i = expr.index("!")
        if i > 0 and expr[i - 1] == ")":
            depth, j = 0, i - 1
            while j >= 0:
                depth += expr[j] == ")"
                depth -= expr[j] == "("
                if depth == 0:
                    break
                j -= 1
            if j < 0:
                raise SyntaxError("Unbalanced brackets")
        else:
            m = re.search(r"(\d+\.?\d*|pi|tau|e)$", expr[:i])
            if not m:
                raise SyntaxError("Misplaced !")
            j = m.start()
        expr = expr[:j] + "fact(" + expr[j:i] + ")" + expr[i + 1:]
    return expr


def _prepare(expr):
    expr = expr.replace("×", "*").replace("÷", "/").replace("π", "pi").replace("τ", "tau")
    expr = re.sub(r"\s+", "", expr).replace("^", "**")
    expr = _expand_factorials(expr)
    expr = expr.replace("%", "/100")
    expr = expr.rstrip("+-*/.")                                  # dangling operator
    expr += ")" * (expr.count("(") - expr.count(")"))            # auto-close brackets
    expr = expr.replace("log2(", "logtwo(")
    expr = re.sub(r"(?<![\w.])0+(?=\d)", "", expr)               # 007 -> 7
    expr = re.sub(r"(\d|\))(?=\(|[a-df-z]|e(?![\d+\-]))", r"\1*", expr)  # 2sin( -> 2*sin(
    expr = re.sub(r"\)(?=[\d.])", ")*", expr)                    # )5 -> )*5
    expr = re.sub(r"\b(pi|tau|e)\b(?=\()", r"\1*", expr)         # pi( -> pi*(
    expr = re.sub(r"(pi|tau)(?=\d)", r"\1*", expr)               # pi2 -> pi*2
    expr = re.sub(r"(?<![\w.])\d+(?![\w.])", lambda m: m.group(0) + ".0", expr)  # floats only
    return expr


def eval_expression(expr):
    """Parse keyboard/button formulas safely using the calculator functions."""
    deg = st.session_state.degree_mode
    safe_dict = {
        "sin": lambda x: calculator.sin(x, deg),
        "cos": lambda x: calculator.cos(x, deg),
        "tan": lambda x: calculator.tan(x, deg),
        "asin": lambda x: calculator.asin(x, deg),
        "acos": lambda x: calculator.acos(x, deg),
        "atan": lambda x: calculator.atan(x, deg),
        "sinh": calculator.sinh, "cosh": calculator.cosh, "tanh": calculator.tanh,
        "asinh": calculator.asinh, "acosh": calculator.acosh, "atanh": calculator.atanh,
        "sqrt": calculator.square_root,
        "cbrt": calculator.cube_root,
        "log": calculator.log10,
        "logtwo": calculator.log2,
        "ln": calculator.natural_log,
        "abs": calculator.absolute,
        "floor": calculator.floor,
        "ceil": calculator.ceil,
        "fact": calculator.factorial,
        "pi": calculator.PI,
        "tau": calculator.TAU,
        "e": calculator.E,
    }
    prepared = _prepare(expr)
    if prepared == "":
        return 0.0
    if not re.fullmatch(r"[a-z0-9+\-*/().,]*", prepared):
        raise SyntaxError("Invalid characters")
    return eval(prepared, {"__builtins__": {}}, safe_dict)


def _format_result(res):
    if isinstance(res, complex):
        raise ValueError("Result is not a real number.")
    res = float(res)
    if math.isnan(res) or math.isinf(res):
        raise ValueError("Result is undefined.")
    res = round(res, 10)
    if abs(res) < 1e15 and res == int(res):
        return str(int(res))
    return f"{res:.10g}"


def _error_text(e):
    if isinstance(e, ZeroDivisionError):
        return "Cannot divide by zero."
    if isinstance(e, ValueError):
        return str(e)
    if isinstance(e, OverflowError):
        return "Result is too large."
    if isinstance(e, (SyntaxError, TypeError, NameError)):
        return "Invalid expression."
    return f"Error: {e}"

# ============================================================
# ACTION HANDLERS  (used as on_click callbacks)
# ============================================================

def _start_fresh_if_needed():
    """After '=' the next digit/constant starts a new calculation."""
    if st.session_state.reset_next:
        st.session_state.display = "0"
        st.session_state.reset_next = False


def handle_digit(digit):
    st.session_state.error = ""
    _start_fresh_if_needed()
    d = st.session_state.display
    if d == "0":
        st.session_state.display = str(digit)
    elif d.endswith("0") and (len(d) == 1 or d[-2] not in "0123456789."):
        st.session_state.display = d[:-1] + str(digit)     # avoid 5+03
    else:
        st.session_state.display += str(digit)


def handle_dot():
    st.session_state.error = ""
    _start_fresh_if_needed()
    d = st.session_state.display
    m = re.search(r"[0-9.]*$", d)
    segment = m.group(0) if m else ""
    if "." in segment:
        return
    if segment == "":
        st.session_state.display += "0."
    else:
        st.session_state.display += "."


def handle_clear():
    st.session_state.display = "0"
    st.session_state.prev_value = None
    st.session_state.pending_op = None
    st.session_state.reset_next = False
    st.session_state.error = ""


def handle_backspace():
    st.session_state.error = ""
    st.session_state.reset_next = False
    d = st.session_state.display
    for token in _TOKENS_BY_LENGTH:          # remove "sin(" in one go
        if d.endswith(token):
            d = d[: -len(token)]
            break
    else:
        d = d[:-1]
    st.session_state.display = d if d else "0"


def handle_bracket(bracket):
    st.session_state.error = ""
    _start_fresh_if_needed()
    d = st.session_state.display
    if bracket == ")" and d.count("(") <= d.count(")"):
        return                                 # nothing to close
    if d == "0" and bracket == "(":
        st.session_state.display = "("
    else:
        st.session_state.display += bracket


def handle_binary_op(op_name):
    st.session_state.error = ""
    st.session_state.reset_next = False        # keep working with the shown result
    sym = "^" if op_name == "x^y" else op_name
    d = st.session_state.display
    if d.endswith("("):
        if sym == "-":
            st.session_state.display += "-"
        return
    if d and d[-1] in OPERATORS:
        d = d[:-1]                             # replace the previous operator
    st.session_state.display = d + sym


def execute_equals():
    st.session_state.error = ""
    expr = st.session_state.display
    try:
        res = _format_result(eval_expression(expr))
        st.session_state.prev_value = expr + ")" * (expr.count("(") - expr.count(")"))
        st.session_state.display = res
        st.session_state.pending_op = None
        st.session_state.reset_next = True
    except Exception as e:
        st.session_state.error = _error_text(e)


def handle_unary_op(func_name):
    st.session_state.error = ""
    d = st.session_state.display

    # --- scientific functions: show them as  sin(  and wait for the argument ---
    if func_name in FUNCTION_TOKENS:
        token = FUNCTION_TOKENS[func_name]
        if d == "0":
            st.session_state.display = token
        elif st.session_state.reset_next:
            st.session_state.display = token + d       # f(previous result)
        else:
            st.session_state.display = d + token
        st.session_state.reset_next = False
        return

    # --- postfix operations ---
    st.session_state.reset_next = False
    if func_name == "x²":
        st.session_state.display = d + "^2"
    elif func_name == "x³":
        st.session_state.display = d + "^3"
    elif func_name == "%":
        st.session_state.display = d + "%"
    elif func_name == "x!":
        st.session_state.display = d + "!"
    elif func_name == "±":
        m = re.search(r"\(-([0-9.]+)\)$", d)
        n = re.search(r"([0-9.]+)$", d)
        if m:
            st.session_state.display = d[: m.start()] + m.group(1)
        elif n and d != "0":
            st.session_state.display = d[: n.start()] + "(-" + n.group(1) + ")"


def handle_constant(const_val):
    st.session_state.error = ""
    _start_fresh_if_needed()
    if const_val == calculator.PI:
        symbol = "π"
    elif const_val == calculator.TAU:
        symbol = "τ"
    else:
        symbol = "e"
    if st.session_state.display == "0":
        st.session_state.display = symbol
    else:
        st.session_state.display += symbol


def handle_typed_expression(typed=None):
    """Evaluate a whole expression string in one go (kept for compatibility)."""
    if typed is not None and typed.strip():
        st.session_state.display = typed
    execute_equals()

# ============================================================
# KEYBOARD BRIDGE  (physical keys -> button clicks)
# ============================================================

KEYBOARD_JS = """
<script>
(function () {
  const doc = window.parent.document;
  if (doc.__calcKeyHandler) doc.removeEventListener('keydown', doc.__calcKeyHandler, true);

  const FUNCS = {sin:'sin', cos:'cos', tan:'tan', asin:'asin', acos:'acos', atan:'atan',
    sinh:'sinh', cosh:'cosh', tanh:'tanh', asinh:'asinh', acosh:'acosh', atanh:'atanh',
    ln:'ln', log:'log₁₀', log10:'log₁₀', log2:'log₂', sqrt:'√x', cbrt:'∛x',
    abs:'|x|', floor:'floor', ceil:'ceil'};
  const CONSTS = {pi:'π', e:'e', tau:'τ'};
  const SIMPLE = {'.':'.', '+':'+', '-':'-', '*':'×', '/':'÷', 'x':'×', '^':'x^y',
    '%':'%', '!':'x!', '(':'(', ')':')', '=':'=', 'Enter':'=',
    'Backspace':'⌫', 'Delete':'C', 'Escape':'C'};
  for (let i = 0; i <= 9; i++) SIMPLE[String(i)] = String(i);
  let buf = '';

  function press(label) {
    for (const b of doc.querySelectorAll('button')) {
      if (b.innerText.trim() === label) { b.click(); return true; }
    }
    return false;
  }
  function flush() { if (CONSTS[buf]) press(CONSTS[buf]); buf = ''; }

  const handler = function (ev) {
    if (ev.ctrlKey || ev.metaKey || ev.altKey) return;
    const t = ev.target;
    if (t && (t.tagName === 'TEXTAREA' || t.isContentEditable ||
        (t.tagName === 'INPUT' && ['text','number','password','search'].includes(t.type)))) return;
    const k = ev.key;

    // typing function names:  s i n (  ->  presses the "sin" button
    if (/^[a-zA-Z]$/.test(k)) {
      if (k.toLowerCase() === 'x' && buf === '') { ev.preventDefault(); press('×'); return; }
      buf = (buf + k.toLowerCase()).slice(-6); ev.preventDefault(); return;
    }
    if (/^[0-9]$/.test(k) && /^log\\d*$/.test(buf)) { buf += k; ev.preventDefault(); return; }
    if (k === '(' && FUNCS[buf]) { press(FUNCS[buf]); buf = ''; ev.preventDefault(); return; }
    if (k === 'Backspace' && buf.length) { buf = buf.slice(0, -1); ev.preventDefault(); return; }

    flush();
    const label = SIMPLE[k];
    if (label) {
      ev.preventDefault();
      press(label);
      if (doc.activeElement && doc.activeElement.blur) doc.activeElement.blur();
    }
  };
  doc.__calcKeyHandler = handler;
  doc.addEventListener('keydown', handler, true);
})();
</script>
"""

# ============================================================
# STYLING
# ============================================================

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle at top, #1b2233 0%, #0b0e14 70%); }
    .block-container { max-width: 480px; padding-top: 2rem; }
    h1 { font-size: 1.5rem !important; text-align: center; color: #e6edf3; }

    /* keep the keypad in 4 columns on phones too */
    div[data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 8px !important; }
    div[data-testid="stColumn"] { min-width: 0 !important; }

    div.stButton > button {
        width: 100%; height: 54px; font-size: 18px; font-weight: 600;
        border-radius: 14px; border: 1px solid #2d333b;
        background: #1f2630; color: #f0f6fc; margin-bottom: 2px;
        transition: transform .05s ease, background .15s ease;
    }
    div.stButton > button:hover { background: #2b3441; border-color: #58a6ff; color: #fff; }
    div.stButton > button:active { transform: scale(.95); }

    [class*="st-key-fn_"] button  { background: #162033; color: #79c0ff; font-size: 16px; }
    [class*="st-key-num_"] button { background: #252d3a; font-size: 20px; }
    [class*="st-key-op_"] button  { background: #ff9f0a; border-color: #ff9f0a; color: #fff; font-size: 22px; }
    [class*="st-key-op_"] button:hover { background: #ffb340; }
    [class*="st-key-clr_"] button { background: #da3633; border-color: #da3633; color: #fff; }
    [class*="st-key-eq_"] button  { background: #238636; border-color: #2ea043; color: #fff; font-size: 22px; }
    [class*="st-key-eq_"] button:hover { background: #2ea043; }

    .display-screen {
        background: linear-gradient(145deg, #161b22, #0d1117);
        border: 1px solid #30363d; border-radius: 18px;
        padding: 14px 22px 18px; text-align: right;
        font-family: 'SF Mono', Consolas, monospace; font-weight: 700;
        color: #58a6ff; margin-bottom: 14px; min-height: 96px;
        word-break: break-all; box-shadow: inset 0 2px 12px rgba(0,0,0,.45);
    }
    .sub-display { font-size: 12px; font-weight: 500; color: #8b949e; margin-bottom: 6px; letter-spacing: .5px; }
    .cursor { display: inline-block; width: 2px; height: 1em; background: #58a6ff;
              margin-left: 3px; vertical-align: text-bottom; animation: blink 1s steps(1) infinite; }
    @keyframes blink { 50% { opacity: 0; } }
    .hint { text-align: center; color: #6e7681; font-size: 12px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# UI LAYOUT
# ============================================================

st.title("🧮 Scientific Calculator By Jameel Shah")

# Header indicator
sub_info = f"MODE: {'DEG' if st.session_state.degree_mode else 'RAD'}"
if st.session_state.prev_value:
    sub_info += f" &nbsp;|&nbsp; {html.escape(st.session_state.prev_value)} ="

shown = st.session_state.display
size = 38 if len(shown) <= 12 else 28 if len(shown) <= 22 else 20

# The ONE display box: shows exactly what you type / click
st.markdown(f"""
<div class="display-screen">
    <div class="sub-display">{sub_info}</div>
    <span style="font-size:{size}px">{html.escape(shown)}</span><span class="cursor"></span>
</div>
""", unsafe_allow_html=True)

if st.session_state.error:
    st.error(st.session_state.error)

# Mode Toggle
st.toggle("Degrees Mode (DEG/RAD)", key="degree_mode")


def fn_button(col, label, key, handler, *args):
    col.button(label, key=key, on_click=handler, args=args, use_container_width=True)


# Tabbed Interface for Advanced Functions
tab1, tab2, tab3 = st.tabs(["Trig & Hyperbolic", "Powers & Logs", "Misc & Constants"])

with tab1:
    cols = st.columns(3)
    names = ["sin", "cos", "tan", "asin", "acos", "atan",
             "sinh", "cosh", "tanh", "asinh", "acosh", "atanh"]
    for i, name in enumerate(names):
        fn_button(cols[i % 3], name, f"fn_{name}", handle_unary_op, name)

with tab2:
    c = st.columns(3)
    fn_button(c[0], "x²", "fn_sq", handle_unary_op, "x²")
    fn_button(c[1], "x³", "fn_cube", handle_unary_op, "x³")
    fn_button(c[2], "x^y", "fn_pow", handle_binary_op, "x^y")
    fn_button(c[0], "√x", "fn_sqrt", handle_unary_op, "√x")
    fn_button(c[1], "∛x", "fn_cbrt", handle_unary_op, "∛x")
    fn_button(c[2], "%", "fn_pct", handle_unary_op, "%")
    fn_button(c[0], "ln", "fn_ln", handle_unary_op, "ln")
    fn_button(c[1], "log₁₀", "fn_log10", handle_unary_op, "log₁₀")
    fn_button(c[2], "log₂", "fn_log2", handle_unary_op, "log₂")

with tab3:
    c = st.columns(3)
    fn_button(c[0], "x!", "fn_fact", handle_unary_op, "x!")
    fn_button(c[1], "|x|", "fn_abs", handle_unary_op, "|x|")
    fn_button(c[2], "±", "fn_sign", handle_unary_op, "±")
    fn_button(c[0], "floor", "fn_floor", handle_unary_op, "floor")
    fn_button(c[1], "ceil", "fn_ceil", handle_unary_op, "ceil")
    fn_button(c[2], "π", "fn_pi", handle_constant, calculator.PI)
    fn_button(c[0], "e", "fn_e", handle_constant, calculator.E)
    fn_button(c[1], "τ", "fn_tau", handle_constant, calculator.TAU)

st.divider()

# Main Number Pad Grid
row1 = st.columns(4)
fn_button(row1[0], "C", "clr_clear", handle_clear)
fn_button(row1[1], "(", "fn_lpar", handle_bracket, "(")
fn_button(row1[2], ")", "fn_rpar", handle_bracket, ")")
fn_button(row1[3], "÷", "op_div", handle_binary_op, "÷")

row2 = st.columns(4)
for i, d in enumerate("789"):
    fn_button(row2[i], d, f"num_{d}", handle_digit, d)
fn_button(row2[3], "×", "op_mul", handle_binary_op, "×")

row3 = st.columns(4)
for i, d in enumerate("456"):
    fn_button(row3[i], d, f"num_{d}", handle_digit, d)
fn_button(row3[3], "-", "op_sub", handle_binary_op, "-")

row4 = st.columns(4)
for i, d in enumerate("123"):
    fn_button(row4[i], d, f"num_{d}", handle_digit, d)
fn_button(row4[3], "+", "op_add", handle_binary_op, "+")

row5 = st.columns(4)
fn_button(row5[0], "⌫", "clr_back", handle_backspace)
fn_button(row5[1], "0", "num_0", handle_digit, "0")
fn_button(row5[2], ".", "num_dot", handle_dot)
fn_button(row5[3], "=", "eq_equals", execute_equals)

st.markdown(
    '<div class="hint">⌨️ Just type: digits, + - * / ^ ( ) % !, names like <b>sin(</b> or <b>sqrt(</b>, '
    '<b>Enter</b> = equals, <b>Backspace</b> = delete, <b>Esc</b> = clear</div>',
    unsafe_allow_html=True,
)

# Invisible component that forwards physical key presses to the buttons above
components.html(KEYBOARD_JS, height=0)