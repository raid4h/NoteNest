# palettes.py
#
# Each theme is a dictionary mapping a SEMANTIC TOKEN (a plain string
# describing a role, e.g. "background") to the hex color that role
# should have in that theme.
#
# The token names below must be IDENTICAL across every theme dict.
# That's what lets ThemeManager swap themes safely: it just looks up
# the same token in a different dictionary.

# Warm, soothing "oat milk latte" palette — cream base with a
# consistent warm-brown undertone running through every token,
# instead of separately-chosen warm/cool swatches.
LIGHT = {
    "background":     "#FBF3E4",
    "card_primary":    "#F1E4D0",
    "card_secondary":  "#E8D8C0",
    "border":          "#D9C4A5",
    "accent":          "#C8A97E",
    "text_secondary":  "#8A6F53",
    "button":          "#6B4A32",
    "text_primary":    "#3B2A1D",
    "button_text":     "#FBF3E4",
}

DARK = {
    "background":      "#222238",
    "card_primary":    "#2A2945",
    "card_secondary":  "#322F51",
    "border":          "#39355C",
    "accent":          "#474466",
    "text_secondary":  "#553A84",
    "button":          "#5C5493",
    "text_primary":    "#B4ACBD",
    "button_text":     "#222238",
}

# Pastel blush/mauve/lavender palette — desaturated and lightened
# across every token so nothing reads as bright or saturated, unlike
# the original hot-pink/magenta pairing.
PINK = {
    "background":      "#F8E8F0",
    "card_primary":    "#F0DCE8",
    "card_secondary":  "#E6D6EC",
    "border":          "#D9B8D9",
    "accent":          "#E7B8D8",
    "text_secondary":  "#9C7A96",
    "button":          "#B98CB0",
    "text_primary":    "#6B4463",
    "button_text":     "#FDF6FA",
}

CYBERPUNK = {
    "background":      "#0A0A12",
    "card_primary":    "#1A1B2E",
    "card_secondary":  "#252742",
    "border":          "#7B2EFF",
    "accent":          "#F2F5FF",
    "text_secondary":  "#FF2E9F",
    "button":          "#2D7CFF",
    "text_primary":    "#00E5FF",
    "button_text":     "#0A0A12",
}

# --- Semantic token constants ---
# These are just the *names* of the roles — plain strings, not colors.
# Existing code that imports these (like every themed screen's
# THEME_MAP) does not need to change at all.

BACKGROUND      = "background"
CARD_PRIMARY    = "card_primary"
CARD_SECONDARY  = "card_secondary"
TEXT_PRIMARY    = "text_primary"
TEXT_SECONDARY  = "text_secondary"
BUTTON          = "button"
BUTTON_TEXT     = "button_text"
BORDER          = "border"
ACCENT          = "accent"