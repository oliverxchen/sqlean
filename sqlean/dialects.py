"""SQL dialect specifications"""

COMMON_SQL = {
    "select": "SELECT",
    "distinct": "DISTINCT",
    "where": "WHERE",
    "from": "FROM",
    "inner": "JOIN_MODIFIER",
    "full": "JOIN_MODIFIER",
    "outer": "JOIN_MODIFIER",
    "cross": "JOIN_MODIFIER",
    "left": "JOIN_MODIFIER",
    "right": "JOIN_MODIFIER",
    "join": "JOIN",
    "and": "BOOLEAN_OPERATOR",
    "or": "BOOLEAN_OPERATOR",
    "like": "LIKE",
    "on": "ON",
    "in": "IN",
    "group": "GROUP",
    "order": "ORDER",
    "by": "BY",
    "if": "IF",
    "end": "END",
    "then": "THEN",
    "as": "AS",
    "else": "ELSE",
    "case": "CASE",
    "when": "WHEN",
    "with": "WITH",
}

# From:
# https://cloud.google.com/bigquery/docs/reference/standard-sql/functions-and-operators
BIGQUERY = {
    "cast": "CAST",
    "any_value": "AGG_FUNCTION",  # Aggregate functions
    "array_agg": "AGG_FUNCTION",
    "array_concat_agg": "AGG_FUNCTION",
    "avg": "AGG_FUNCTION",
    "bit_and": "AGG_FUNCTION",
    "bit_or": "AGG_FUNCTION",
    "bit_xor": "AGG_FUNCTION",
    "count": "AGG_FUNCTION",
    "countif": "AGG_FUNCTION",
    "logical_and": "AGG_FUNCTION",
    "logical_or": "AGG_FUNCTION",
    "max": "AGG_FUNCTION",
    "min": "AGG_FUNCTION",
    "string_agg": "AGG_FUNCTION",
    "sum": "AGG_FUNCTION",
    "corr": "AGG_FUNCTION",  # Statistical aggregate functions
    "covar_pop": "AGG_FUNCTION",
    "covar_samp": "AGG_FUNCTION",
    "stddev_pop": "AGG_FUNCTION",
    "stddev_samp": "AGG_FUNCTION",
    "stddev": "AGG_FUNCTION",
    "var_pop": "AGG_FUNCTION",
    "var_samp": "AGG_FUNCTION",
    "variance": "AGG_FUNCTION",
    "approx_count_distinct": "AGG_FUNCTION",  # Approximate aggregate functions
    "approx_quantiles": "AGG_FUNCTION",
    "approx_top_count": "AGG_FUNCTION",
    "approx_top_sum": "AGG_FUNCTION",
    "rank": "NUM_FUNCTION",  # Numbering functions
    "dense_rank": "NUM_FUNCTION",
    "percent_rank": "NUM_FUNCTION",
    "cume_dist": "NUM_FUNCTION",
    "ntile": "NUM_FUNCTION",
    "row_number": "NUM_FUNCTION",
    "bit_count": "FUNCTION",  # Bit functions
    "abs": "FUNCTION",  # Mathematical functions
    "sign": "FUNCTION",
    "is_inf": "FUNCTION",
    "is_nan": "FUNCTION",
    "ieee_divide": "FUNCTION",
    "rand": "FUNCTION",
    "sqrt": "FUNCTION",
    "pow": "FUNCTION",
    "power": "FUNCTION",
    "exp": "FUNCTION",
    "ln": "FUNCTION",
    "log": "FUNCTION",
    "log10": "FUNCTION",
    "greatest": "FUNCTION",
    "least": "FUNCTION",
    "div": "FUNCTION",
    "safe_divide": "FUNCTION",
    "safe_multiply": "FUNCTION",
    "safe_negate": "FUNCTION",
    "safe_add": "FUNCTION",
    "safe_subtract": "FUNCTION",
    "mod": "FUNCTION",
    "round": "FUNCTION",
    "trunc": "FUNCTION",
    "ceil": "FUNCTION",
    "ceiling": "FUNCTION",
    "floor": "FUNCTION",
    "cos": "FUNCTION",
    "cosh": "FUNCTION",
    "acos": "FUNCTION",
    "acosh": "FUNCTION",
    "sin": "FUNCTION",
    "sinh": "FUNCTION",
    "asin": "FUNCTION",
    "asinh": "FUNCTION",
    "tan": "FUNCTION",
    "tanh": "FUNCTION",
    "atan": "FUNCTION",
    "atanh": "FUNCTION",
    "atan2": "FUNCTION",
    "range_bucket": "FUNCTION",
    "first_value": "NAV_FUNCTION",  # Navigation functions
    "last_value": "NAV_FUNCTION",
    "nth_value": "NAV_FUNCTION",
    "lead": "NAV_FUNCTION",
    "lag": "NAV_FUNCTION",
    "percentile_cont": "NAV_FUNCTION",
    "percentile_disc": "NAV_FUNCTION",
}
