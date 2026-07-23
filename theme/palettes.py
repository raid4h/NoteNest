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
# consistent warm-brown undertone running through every token.
CREAM = {
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

# This is the APP'S DEFAULT theme (formerly "Floral") — periwinkle-
# lavender base with soft pink/coral accents.
DEFAULT = {
    "background":      "#DCD6F5",
    "card_primary":    "#F8F5FC",
    "card_secondary":  "#F5C7DC",
    "border":          "#B9AEE8",
    "accent":          "#F2A6B4",
    "text_secondary":  "#8A7FA8",
    "button":          "#E8899F",
    "text_primary":    "#4A3B6B",
    "button_text":     "#FFF9FC",
}

# True grayscale — every value is a shade of gray, no hue at all,
# distinct from the old Cyberpunk's neon purple/pink/blue palette.
# A light button on a near-black background gives it a deliberate,
# high-contrast "monochrome poster" feel rather than a colorful one.
MONOCHROME = {
    "background":      "#121212",
    "card_primary":    "#1E1E1E",
    "card_secondary":  "#2A2A2A",
    "border":          "#3D3D3D",
    "accent":          "#9E9E9E",
    "text_secondary":  "#B0B0B0",
    "button":          "#E0E0E0",
    "text_primary":    "#FFFFFF",
    "button_text":     "#121212",
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