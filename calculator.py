import math

# ============================================================
# BASIC OPERATIONS
# ============================================================

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

def percentage(x):
    return x / 100

def change_sign(x):
    return -x

# ============================================================
# POWERS AND ROOTS
# ============================================================

def square(x):
    return x ** 2

def cube(x):
    return x ** 3

def power(x, y):
    return x ** y

def square_root(x):
    if x < 0:
        raise ValueError("Square root of a negative number is not real.")
    return math.sqrt(x)

def cube_root(x):
    return math.cbrt(x)

# ============================================================
# LOGARITHMIC FUNCTIONS
# ============================================================

def natural_log(x):
    if x <= 0:
        raise ValueError("ln requires a positive number.")
    return math.log(x)

def log10(x):
    if x <= 0:
        raise ValueError("log requires a positive number.")
    return math.log10(x)

def log2(x):
    if x <= 0:
        raise ValueError("log₂ requires a positive number.")
    return math.log2(x)

# ============================================================
# TRIGONOMETRIC FUNCTIONS
# ============================================================

def sin(x, degree_mode=True):
    if degree_mode:
        x = math.radians(x)
    return math.sin(x)

def cos(x, degree_mode=True):
    if degree_mode:
        x = math.radians(x)
    return math.cos(x)

def tan(x, degree_mode=True):
    if degree_mode:
        x = math.radians(x)
    return math.tan(x)

# ============================================================
# INVERSE TRIGONOMETRIC FUNCTIONS
# ============================================================

def asin(x, degree_mode=True):
    if x < -1 or x > 1:
        raise ValueError("sin⁻¹ input must be between -1 and 1.")
    result = math.asin(x)
    if degree_mode:
        result = math.degrees(result)
    return result

def acos(x, degree_mode=True):
    if x < -1 or x > 1:
        raise ValueError("cos⁻¹ input must be between -1 and 1.")
    result = math.acos(x)
    if degree_mode:
        result = math.degrees(result)
    return result

def atan(x, degree_mode=True):
    result = math.atan(x)
    if degree_mode:
        result = math.degrees(result)
    return result

# ============================================================
# HYPERBOLIC FUNCTIONS
# ============================================================

def sinh(x):
    return math.sinh(x)

def cosh(x):
    return math.cosh(x)

def tanh(x):
    return math.tanh(x)

# ============================================================
# INVERSE HYPERBOLIC FUNCTIONS
# ============================================================

def asinh(x):
    return math.asinh(x)

def acosh(x):
    if x < 1:
        raise ValueError("acosh requires x >= 1.")
    return math.acosh(x)

def atanh(x):
    if x <= -1 or x >= 1:
        raise ValueError("atanh requires -1 < x < 1.")
    return math.atanh(x)

# ============================================================
# OTHER MATHEMATICAL FUNCTIONS
# ============================================================

def factorial(x):
    if x < 0 or not float(x).is_integer():
        raise ValueError("Factorial requires a non-negative integer.")
    return math.factorial(int(x))

def absolute(x):
    return abs(x)

def floor(x):
    return math.floor(x)

def ceil(x):
    return math.ceil(x)

# ============================================================
# CONSTANTS
# ============================================================

PI = math.pi
E = math.e
TAU = math.tau