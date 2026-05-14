import re
from pathlib import Path


WHATSAPP_URL = "https://wa.me/15550000000?text=Hi%20Nova%20Studio%20Digital"


def test_landing_sections_follow_the_marketing_flow(client):
    response = client.get("/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)

    ordered_markers = [
        'class="site-header"',
        'id="hero"',
        'id="services"',
        'id="outcomes-process"',
        'id="testimonials"',
        'id="contact"',
        'id="contact-form"',
        'class="site-footer"',
    ]

    previous_index = -1
    for marker in ordered_markers:
        current_index = body.find(marker)
        assert current_index > previous_index, f"Missing or misordered marker: {marker}"
        previous_index = current_index

    assert 'id="outcomes"' not in body
    assert 'id="process"' not in body


def test_landing_keeps_whatsapp_primary_and_proof_honest(client):
    body = client.get("/").get_data(as_text=True)

    assert body.count(f'href="{WHATSAPP_URL}"') == 2
    assert body.count('class="primary-action"') == 2
    assert "Illustrative demo" in body
    assert "Demo outcome" in body
    assert 'action="/"' in body
    assert 'method="post"' in body.lower()
    assert 'class="secondary-form"' in body
    assert 'name="name"' in body
    assert 'name="email"' in body
    assert 'name="phone"' in body
    assert 'name="service_interest"' in body
    assert 'name="message"' in body
    assert 'aria-live="polite"' in body
    assert "Preview admin scope" not in body
    assert "Message us on WhatsApp" in body
    assert body.count('class="secondary-form"') == 1
    assert body.find('Message us on WhatsApp') < body.find('id="contact-form"')
    assert body.find('class="proof-section"') < body.find('id="contact"')
    assert body.find('Demo outcome') < body.find('id="contact"')
    assert body.find('id="contact"') < body.find('id="contact-form"')
    assert 'href="#services"' in body


def test_landing_exposes_named_contact_region_and_landmark_outline(client):
    body = client.get("/").get_data(as_text=True)

    assert '<main id="main-content" class="page-shell" tabindex="-1">' in body
    assert (
        '<section id="contact" class="story-section contact-section" '
        'role="region" aria-labelledby="contact-title">' in body
    )
    assert 'id="contact-form-title"' in body
    assert body.count("<h1") == 1
    assert '<h1 id="hero-title" class="landing-hero-title">Your business needs an online presence that matches the quality of what you sell.</h1>' in body
    assert (
        "We design clear, polished landing pages built to present your offer with more confidence"
        in body
    )
    assert (
        "The goal is simple: understand what your business needs"
        in body
    )
    assert "We review the context" in body
    assert "We set the priority" in body
    assert "We reply with direction" in body
    assert "Name" in body
    assert "Phone or WhatsApp" in body
    assert "What do you need?" in body
    assert "Project details" in body
    assert "Send brief" in body
    assert "Message us on WhatsApp" in body
    assert "Telefono o WhatsApp" not in body
    assert "Detalles del proyecto" not in body
    assert re.findall(r"<header\b", body) == ["<header"]
    assert re.findall(r"<nav\b", body) == ["<nav"]
    assert re.findall(r"<main\b", body) == ["<main"]
    assert re.findall(r"<footer\b", body) == ["<footer"]

    for heading_id in (
        "services-title",
        "outcomes-process-title",
        "benefits-title",
        "process-title",
        "proof-title",
        "contact-title",
    ):
        assert f'id="{heading_id}"' in body


def test_landing_stylesheet_exposes_focus_tokens_and_mobile_stacking():
    css = Path("static/css/styles.css").read_text(encoding="utf-8")

    assert "--canvas:" in css
    assert "--signal:" in css
    assert ":focus-visible" in css
    assert "min-width: 320px;" in css
    assert ".hero-layout" in css
    assert ".outcomes-process-grid" in css
    assert ".outcomes-process-panel" in css
    assert ".contact-section" in css
    assert "flex-wrap: wrap;" in css
    assert "width: min(1120px, calc(100% - 2rem));" in css
    assert "@media (max-width: 900px)" in css
    assert "grid-template-columns: 1fr;" in css
    assert ".proof-section .section-heading" in css
    assert ".contact-form-card" in css
    assert ".contact-form-section" in css
    assert ".contact-next-steps" in css


def test_english_hero_headline_uses_landing_specific_balanced_layout(client):
    body = client.get("/").get_data(as_text=True)
    css = Path("static/css/styles.css").read_text(encoding="utf-8")

    assert '<h1 id="hero-title" class="landing-hero-title">' in body
    assert ".landing-hero-title" in css
    assert "grid-template-columns: minmax(0, 2.25fr) minmax(16rem, 0.75fr);" in css
    assert "max-width: 11em;" in css
    assert "font-size: clamp(2.75rem, 5.4vw, 4.95rem);" in css
    assert "text-wrap: balance;" in css


def test_landing_layout_avoids_desktop_visual_holes():
    css = Path("static/css/styles.css").read_text(encoding="utf-8")

    assert ".hero-layout" in css
    assert "align-items: start;" in css
    assert ".outcomes-process-grid" in css
    assert "align-items: start;" in css
    assert ".contact-primary" in css
    assert "max-width: 58rem;" in css
    assert "margin-top: 1.35rem;" in css


def test_proof_heading_uses_fuller_desktop_width():
    css = Path("static/css/styles.css").read_text(encoding="utf-8")

    assert ".proof-section .section-heading" in css
    assert "max-width: 58rem;" in css
    assert ".proof-section h2" in css
    assert "text-wrap: balance;" in css


def test_outcomes_card_has_intentional_closing_note():
    css = Path("static/css/styles.css").read_text(encoding="utf-8")

    assert "The result is a page that feels easier to trust before the first conversation starts." in Path(
        "templates/landing.html"
    ).read_text(encoding="utf-8")
    assert "outcomes-closing-note" in css
    assert "margin-top: 1.25rem;" in css


def test_contact_section_keeps_ctas_below_single_column_content():
    css = Path("static/css/styles.css").read_text(encoding="utf-8")

    assert ".contact-primary" in css
    assert "max-width: 58rem;" in css
    assert "grid-template-columns: minmax(0, 1.2fr) minmax(18rem, 0.8fr);" not in css
    assert (
        ".contact-section .contact-actions {\n"
        "    justify-self: start;\n"
        "    margin-top: 1.35rem;\n"
        "}" in css
    )
