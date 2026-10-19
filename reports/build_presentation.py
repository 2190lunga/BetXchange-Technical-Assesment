"""Build the BetXchange assessment PowerPoint deck from the verified data model and
the dashboard screenshots captured in reports/dashboard_screenshots/.

Content mirrors reports/executive_presentation_notes.md (13-slide structure). Every
figure here traces back to output/*.csv -- see docs/assumptions.md for methodology.
"""
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_DIR = PROJECT_ROOT / "reports" / "dashboard_screenshots"
OUTPUT_PATH = PROJECT_ROOT / "reports" / "BetXchange_Data_Analyst_Assessment.pptx"

CANDIDATE_NAME = "[Your Name Here]"
ASSESSMENT_DATE = "2026-10-18"

# BetXchange brand palette (matches dashboard/styles.css)
BLUE = RGBColor(0x0A, 0x4F, 0xCF)
BLUE_DEEP = RGBColor(0x0A, 0x43, 0xAE)
YELLOW = RGBColor(0xF5, 0xD5, 0x4A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
TEXT_DARK = RGBColor(0x15, 0x34, 0x50)
MUTED = RGBColor(0x68, 0x84, 0xA8)
SUCCESS = RGBColor(0x1F, 0xA7, 0x7A)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


def cropped(file_name: str, box_frac: tuple[float, float, float, float], out_name: str) -> Path:
    """Crop a screenshot by fractional (left, top, right, bottom) and cache the result."""
    src = SCREENSHOT_DIR / file_name
    out = SCREENSHOT_DIR / out_name
    img = Image.open(src)
    w, h = img.size
    box = (int(box_frac[0] * w), int(box_frac[1] * h), int(box_frac[2] * w), int(box_frac[3] * h))
    img.crop(box).save(out)
    return out


# Pre-crop "hero" regions (header + KPI cards + first chart row) sized close to 16:9,
# plus one focused crop of the retention cohort table.
HERO_01 = cropped("01_executive_overview.png", (0, 0, 1, 0.44), "_hero_01.png")
HERO_02 = cropped("02_customer_behaviour.png", (0, 0, 1, 0.32), "_hero_02.png")
HERO_03 = cropped("03_financial_product_mix.png", (0, 0, 1, 0.57), "_hero_03.png")
HERO_04 = cropped("04_risk_concentration.png", (0, 0, 1, 0.53), "_hero_04.png")
HERO_05 = cropped("05_growth_opportunities.png", (0, 0, 1, 0.62), "_hero_05.png")
RETENTION_CROP = cropped("02_customer_behaviour.png", (0.605, 0.435, 0.98, 0.605), "_retention_crop.png")

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
BLANK = prs.slide_layouts[6]


def add_background(slide, color=BLUE):
    rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    rect.fill.solid()
    rect.fill.fore_color.rgb = color
    rect.line.fill.background()
    rect.shadow.inherit = False
    # Send to back
    spTree = slide.shapes._spTree
    spTree.remove(rect._element)
    spTree.insert(2, rect._element)
    return rect


def add_textbox(slide, left, top, width, height, text, size=14, color=TEXT_DARK,
                 bold=False, align=PP_ALIGN.LEFT, font_name="Segoe UI", italic=False):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = font_name
    return box


def add_wordmark(slide, left, top, size=28):
    box = slide.shapes.add_textbox(left, top, Inches(4), Inches(0.6))
    tf = box.text_frame
    p = tf.paragraphs[0]
    for text, color in (("bet", WHITE), ("X", YELLOW), ("change", WHITE)):
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = True
        run.font.color.rgb = color
        run.font.name = "Segoe UI"
    return box


def add_panel(slide, left, top, width, height, radius=0.12):
    panel = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    panel.fill.solid()
    panel.fill.fore_color.rgb = WHITE
    panel.line.color.rgb = RGBColor(0xDF, 0xEA, 0xF9)
    panel.line.width = Pt(1)
    panel.shadow.inherit = False
    try:
        panel.adjustments[0] = radius
    except Exception:
        pass
    return panel


def add_bullets(slide, left, top, width, height, bullets, size=15, color=TEXT_DARK, space_after=10):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, bullet in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        run = p.add_run()
        run.text = f"\u2022  {bullet}"
        run.font.size = Pt(size)
        run.font.color.rgb = color
        run.font.name = "Segoe UI"
    return box


def add_header(slide, eyebrow, title):
    add_textbox(slide, Inches(0.6), Inches(0.35), Inches(12), Inches(0.35), eyebrow.upper(),
                size=12, color=YELLOW, bold=True)
    add_textbox(slide, Inches(0.6), Inches(0.68), Inches(12.1), Inches(0.9), title,
                size=26, color=WHITE, bold=True)


def add_image_fit(slide, image_path, left, top, max_width, max_height):
    img = Image.open(image_path)
    w, h = img.size
    aspect = w / h
    box_aspect = max_width / max_height
    if aspect > box_aspect:
        width = max_width
        height = Emu(int(max_width / aspect))
    else:
        height = max_height
        width = Emu(int(max_height * aspect))
    left_centered = Emu(int(left + (max_width - width) / 2))
    top_centered = Emu(int(top + (max_height - height) / 2))
    slide.shapes.add_picture(str(image_path), left_centered, top_centered, width=width, height=height)


def content_slide(eyebrow, title, bullets, image_path=None, bullet_width_frac=0.46):
    slide = prs.slides.add_slide(BLANK)
    add_background(slide)
    add_wordmark(slide, Inches(0.6), Inches(6.95), size=14)
    add_header(slide, eyebrow, title)

    content_top = Inches(1.75)
    content_height = Inches(5.35)

    if image_path:
        bullets_width = Emu(int(SLIDE_W * bullet_width_frac))
        panel_left = Inches(0.6)
        add_panel(slide, panel_left, content_top, bullets_width, content_height)
        add_bullets(slide, Emu(panel_left + Inches(0.3)), Emu(content_top + Inches(0.25)),
                    Emu(bullets_width - Inches(0.6)), Emu(content_height - Inches(0.5)), bullets)

        image_left = Emu(panel_left + bullets_width + Inches(0.35))
        image_width = Emu(SLIDE_W - image_left - Inches(0.5))
        img_panel = add_panel(slide, image_left, content_top, image_width, content_height)
        add_image_fit(slide, image_path, Emu(image_left + Inches(0.15)), Emu(content_top + Inches(0.15)),
                      Emu(image_width - Inches(0.3)), Emu(content_height - Inches(0.3)))
    else:
        panel_left = Inches(0.6)
        panel_width = Emu(SLIDE_W - Inches(1.2))
        add_panel(slide, panel_left, content_top, panel_width, content_height)
        add_bullets(slide, Emu(panel_left + Inches(0.4)), Emu(content_top + Inches(0.3)),
                    Emu(panel_width - Inches(0.8)), Emu(content_height - Inches(0.6)), bullets, size=16)
    return slide


# ---------------------------------------------------------------------------
# Slide 1: Title
# ---------------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
add_background(slide)
add_wordmark(slide, Inches(0.8), Inches(0.7), size=36)
add_textbox(slide, Inches(0.8), Inches(2.6), Inches(11.5), Inches(1.2),
            "BetXchange Data Analyst Assessment", size=40, color=WHITE, bold=True)
add_textbox(slide, Inches(0.8), Inches(3.6), Inches(11.5), Inches(0.6),
            "Customer behaviour, product performance, retention, risk, and growth analysis",
            size=18, color=YELLOW)
add_textbox(slide, Inches(0.8), Inches(5.6), Inches(8), Inches(0.5), CANDIDATE_NAME, size=18, color=WHITE, bold=True)
add_textbox(slide, Inches(0.8), Inches(6.05), Inches(8), Inches(0.4), f"Date: {ASSESSMENT_DATE}", size=13, color=RGBColor(0xDF, 0xEA, 0xF9))
add_textbox(slide, Inches(0.8), Inches(6.4), Inches(11), Inches(0.5),
            "Data-driven view of customer value, loyalty, profitability, and risk exposure (May-July 2024)",
            size=12, color=RGBColor(0xDF, 0xEA, 0xF9), italic=True)

# ---------------------------------------------------------------------------
# Slide 2: Executive Summary
# ---------------------------------------------------------------------------
content_slide(
    "Executive Summary",
    "Revenue is positive and growing; the real story is concentration",
    [
        "Operator revenue (stake minus payout) is positive and growing every month: "
        "+R7.4m (May) -> +R9.9m (June) -> +R16.6m (July), margin ~4.4%-5.7%.",
        "Retention is strong: cohort-based retention rates are above 80% across the period, "
        "with newer cohorts retaining even better (90%-100%).",
        "Revenue is highly concentrated: the top 1% of users (148 in July) generate 77% of "
        "that month's stake -- a dependency signal, not evidence of losses.",
        "Key management focus: concentration risk, not profitability. A small group of "
        "high-stake users drives most volume and payout volatility.",
    ],
    image_path=HERO_01,
)

# ---------------------------------------------------------------------------
# Slide 3: Data Overview & Methodology
# ---------------------------------------------------------------------------
content_slide(
    "Data Overview & Methodology",
    "Four verified sources, fully reproducible KPI pipeline",
    [
        "Sources: Users, Slips, and Transactions (3 monthly files each) plus GA4 website "
        "traffic exports -- the GA4 data was never ingested in the original pipeline and is "
        "now included.",
        "Fixed a duplicate-row bug in the slip export (Total rows re-counted daily activity) "
        "and a join fan-out bug that had inflated product-level stake to impossible, "
        "trillion-rand figures.",
        "Replaced unexplained fixed risk thresholds with documented, data-derived percentile "
        "thresholds that adapt to monthly volume.",
        "Found a real data-governance gap: only 33% of transacting customers (7,918 of "
        "24,142) have a matching row in the raw Users files -- the rest have no age/country "
        "on record at all.",
        "Every KPI table and view is reproducible end-to-end from raw files; full methodology "
        "and every assumption is logged in docs/assumptions.md.",
    ],
)

# ---------------------------------------------------------------------------
# Slide 4: Customer Analysis
# ---------------------------------------------------------------------------
content_slide(
    "Customer Analysis",
    "24,142 customers -- but age/country data only covers 33% of them",
    [
        "24,142 distinct customers, 286,244 transactions, and R684.6m total stake across "
        "May-July.",
        "Coverage limit: only 7,918 customers (33%) have a matching age/country record; the "
        "figures below describe that matched subset only, not the full customer base.",
        "Among matched customers: the 35-44 age band is 49.3% of stake and 57.5% of operator "
        "revenue; South Africa is 97.8% of matched stake.",
        "Average customer margin is 41.7% (unweighted) -- skewed upward by many small-stake "
        "customers; the revenue-weighted company margin is ~5%-6%.",
    ],
    image_path=HERO_02,
)

# ---------------------------------------------------------------------------
# Slide 5: Betting Activity Analysis
# ---------------------------------------------------------------------------
content_slide(
    "Betting Activity Analysis",
    "Casino leads, but the mix is broad and diversified",
    [
        "Casino is the largest product by modeled stake share (46.4% of July), followed by "
        "Sport (25.7%) and Aviator (14.2%).",
        "Product-level figures are a modeled allocation (by each customer's slip-count share), "
        "not a direct measurement -- the raw transactions have no product field.",
        "Transaction volume and active-customer counts both rise materially from May to July "
        "(+26% active customers).",
        "Product mix supports both marketing investment and category-level commercial "
        "decisions.",
    ],
)

# ---------------------------------------------------------------------------
# Slide 6: Financial Performance
# ---------------------------------------------------------------------------
content_slide(
    "Financial Performance",
    "Operator revenue is healthy and accelerating",
    [
        "Total stake grew from R168.2m (May) to R293.3m (July).",
        "Operator revenue (BetXchange's gross gaming revenue) grew from +R7.4m to +R16.6m "
        "over the same period.",
        "Operator margin improved from 4.4% to 5.7% -- within a typical bookmaker range.",
        "This is healthy, expected bookmaker economics: customers losing money on balance is "
        "how a sportsbook/casino earns revenue, not a sign of distress.",
    ],
    image_path=HERO_03,
)

# ---------------------------------------------------------------------------
# Slide 7: Retention Analysis
# ---------------------------------------------------------------------------
content_slide(
    "Retention Analysis",
    "Repeat activity is strong and improving in newer cohorts",
    [
        "March 2024 cohort: 80.1% (May) -> 82.2% (June) -> 87.6% (July) retention.",
        "Newer cohorts retain even better: the June 2024 cohort reaches 90.3% retention in "
        "July.",
        "Retention is a strategically important, directly actionable lever for Warren "
        "(Operations) and Ryan (Growth).",
        "Recommendation: protect high-retention cohorts with experience quality, and target "
        "engagement programmes at the lower-retention cohorts (2024/04, 2024/05).",
    ],
    image_path=RETENTION_CROP,
)

# ---------------------------------------------------------------------------
# Slide 8: Risk Analysis
# ---------------------------------------------------------------------------
content_slide(
    "Risk & Concentration Analysis",
    "Not losses -- concentration and payout exposure",
    [
        "Large-stake transactions (above that month's own 95th percentile, R3,929 in July) "
        "account for 90.9% of stake volume.",
        "The top 10 users hold 36.3% of July's stake; the top 1% (148 users) hold 77.3%.",
        "11.6% of July transactions were customer wins -- the operator's real payout exposure.",
        "This methodology cannot detect fraud, collusion, or multi-accounting: the data has "
        "no device, IP, payment-method, or account-linkage fields.",
    ],
    image_path=HERO_04,
)

# ---------------------------------------------------------------------------
# Slide 9: Marketing Analysis
# ---------------------------------------------------------------------------
content_slide(
    "Marketing Analysis",
    "Website traffic is growing; channel-level claims are out of scope",
    [
        "GA4 website traffic grew from ~7.1m monthly page views (May) to ~8.7m (July), "
        "broadly in line with transaction growth.",
        "~96% of website traffic comes from South Africa every month, consistent with "
        "BetXchange's core market.",
        "This export has NO campaign, channel, or source/medium field, and cannot be linked "
        "to the betting user_id -- campaign effectiveness and acquisition-channel ROI cannot "
        "be measured from this data.",
        "Recommendation for Gracia / governance: add UTM tagging and a login-linked "
        "identifier if channel-level marketing evaluation is required going forward.",
    ],
)

# ---------------------------------------------------------------------------
# Slide 10: Stakeholder Recommendations
# ---------------------------------------------------------------------------
content_slide(
    "Stakeholder Recommendations",
    "Tailored actions for each business owner",
    [
        "Ryan (Growth): prioritise the strongest product categories; invest in retention for "
        "high-value cohorts.",
        "Warren (Retention): focus engagement actions on lower-performing cohorts (2024/04, "
        "2024/05).",
        "Craig (Risk): monitor top-1%/top-10 stake share and large-payout review -- the "
        "priority is concentration, not losses.",
        "Holly (Marketing): use verified traffic trends for funnel review; do not claim "
        "channel ROI without UTM-tagged data.",
        "Gracia (Governance): maintain the raw-to-cleaned-to-KPI audit trail; keep "
        "docs/assumptions.md as the methodology source of truth.",
    ],
)

# ---------------------------------------------------------------------------
# Slide 11: 30/60/90 Day Action Plan
# ---------------------------------------------------------------------------
content_slide(
    "30 / 60 / 90 Day Action Plan",
    "From validated insight to operational practice",
    [
        "30 days: finalise dashboard/KPI review with stakeholders; validate retention and "
        "concentration-risk metrics with business owners.",
        "60 days: launch a targeted retention campaign; introduce a monitoring process for "
        "large individual payouts and top-user stake concentration.",
        "90 days: formal performance review cycle with stakeholder scorecards; quantify "
        "retention uplift, product growth, and concentration-risk reduction.",
    ],
    image_path=HERO_05,
)

# ---------------------------------------------------------------------------
# Slide 12: Expected Business Impact
# ---------------------------------------------------------------------------
content_slide(
    "Expected Business Impact",
    "Predictable growth through retention and concentration management",
    [
        "Revenue: stronger product contribution and reduced dependency on the top 1% of "
        "users supports more predictable, sustainable growth.",
        "Retention: cohort-based retention is a strong lever for customer lifetime value.",
        "Operations: cleaner, standardised KPI reporting improves stakeholder decision "
        "quality and speed.",
        "Risk: stake-concentration monitoring (top-10/top-1% share) enables earlier "
        "intervention on dependency and payout-volatility risk.",
    ],
)

# ---------------------------------------------------------------------------
# Slide 13: Conclusion & Next Steps
# ---------------------------------------------------------------------------
content_slide(
    "Conclusion & Next Steps",
    "Revenue is healthy; concentration is the risk to manage",
    [
        "BetXchange shows growing customer activity and positive, growing operator revenue "
        "(+R7.4m to +R16.6m, May-July) -- the earlier 'weak profitability' conclusion was "
        "based on an inverted metric and has been corrected.",
        "Revenue and stake volume are highly concentrated in a small number of users -- this "
        "is the real exposure to manage, not a loss-making business.",
        "Next steps: finalise stakeholder review of dashboard outputs; confirm "
        "concentration-risk thresholds and retention definitions with business owners; "
        "prepare the data appendix and AI-assistance disclosure for governance sign-off.",
    ],
)

prs.save(str(OUTPUT_PATH))
print(f"Saved presentation to: {OUTPUT_PATH}")
