"""FM algorithm limits shared across gain calculators and managers.

Mirrors ``FMPmrConfig.hpp`` in ckpttn-cpp. Nets whose degree exceeds
``FM_MAX_DEGREE`` are excluded from gain updates and cost accounting, so a
handful of very high-fanout nets cannot dominate the running time.
"""

FM_MAX_DEGREE = 500
