import contextvars

# Declarar la variable de contexto global para contexto
contexto_ejecucion = contextvars.ContextVar('contexto_ejecucion')