# Refined Claim Document — Romer Solow Model (v2, post-descent)

This fixture represents a refined decomposition of Solow growth model claims,
with explicit scope markers, falsification conditions, and evidence types added.
Claims are bounded to their domain of applicability.

## Scoped Claims with Falsification Conditions

In the standard Solow model with a Cobb-Douglas production function, capital
accumulates according to the law of motion: dot_k = s*f(k) - (n+g+delta)*k,
where s is the savings rate, n is population growth, g is technology growth,
and delta is depreciation.  This equation would be wrong if the production
function were not twice continuously differentiable.

Under the assumption that capital and labor are the only inputs and the
production function satisfies the Inada conditions, the economy converges to
a unique steady-state capital-labor ratio k*.  This convergence fails when
the Inada conditions are violated (e.g., AK models where f'(k) does not
converge to zero).

Holding technology growth and population growth constant, a higher savings
rate increases the steady-state capital per effective worker.  We can test
this via cross-country regression: countries with higher savings rates should
exhibit higher capital-output ratios, all else equal.  The claim would be
falsified if this correlation were systematically negative in the data.

In continuous time, the transition dynamics follow a saddle path.  Starting
below steady state, the economy grows; above steady state, it contracts toward
k*.  A counterexample would be a model with multiple steady states, which
would require non-convex technology.

The neoclassical model assumes diminishing returns to capital (f''(k) < 0).
This assumption fails when capital includes non-rival goods such as ideas or
software.  In economies where AI capital is non-rival, the standard Solow
convergence results do not apply without modification.

## Properly Scoped AI-Capital Claims

In a model where AI capital is treated as a non-rival input alongside human
labor, the standard Romer (1990) insight applies: the economy may exhibit
sustained per-capita growth without exogenous technological progress.
This prediction would be falsified if AI-augmented output per worker did not
grow faster than in comparable human-only economies over a ten-year horizon.

Under the assumption that AI services can be replicated at near-zero marginal
cost, investment in AI capital does not face diminishing returns in the same
way physical capital does.  This claim can be falsified by computational
evidence: a simulation showing that AI capital accumulation follows the same
diminishing-returns trajectory as physical capital would refute it.
