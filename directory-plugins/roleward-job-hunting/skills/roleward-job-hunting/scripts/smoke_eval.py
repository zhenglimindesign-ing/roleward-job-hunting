#!/usr/bin/env python3
from opportunity_state import calculate_scores

base = {
    'requirements': [
        {'materiality': 'core', 'coverage': 'partial'},
        {'materiality': 'important', 'coverage': 'met'},
    ],
    'direction_alignment': 80,
    'screening_dimensions': [2, 2, 2, 2],
    'career_value_dimensions': [3, 3, 3, 3],
}
stronger = {
    **base,
    'requirements': [
        {'materiality': 'core', 'coverage': 'met'},
        {'materiality': 'important', 'coverage': 'met'},
    ],
}
base_scores = calculate_scores(base)
stronger_scores = calculate_scores(stronger)
assert stronger_scores['capability_match'] >= base_scores['capability_match']
assert stronger_scores['overall_match'] >= base_scores['overall_match']
# Employability is intentionally absent from score arithmetic; changing it cannot contaminate Capability.
with_employability = {**base, 'employability': 'structural_blocker'}
assert calculate_scores(with_employability)['capability_match'] == base_scores['capability_match']
# Prestige is not a score input.
with_prestige = {**base, 'company_prestige': 100}
assert calculate_scores(with_prestige) == base_scores
print('Score monotonicity/dimension-separation smoke passed')
