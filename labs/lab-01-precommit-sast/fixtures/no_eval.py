# Static scanner fixture only: the input is a constant, harmless expression.
# ruleid: no-eval
result = eval("1 + 1")

# ok: no-eval
result = 1 + 1
