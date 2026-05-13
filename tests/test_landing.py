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
    assert "Demo ilustrativa" in body
    assert "Resultado demo" in body
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
    assert "Escribir por WhatsApp" in body
    assert body.count('class="secondary-form"') == 1
    assert body.find('Escribir por WhatsApp') < body.find('id="contact-form"')


def test_landing_exposes_named_contact_region_and_landmark_outline(client):
    body = client.get("/").get_data(as_text=True)

    assert '<main id="main-content" class="page-shell" tabindex="-1">' in body
    assert (
        '<section id="contact" class="story-section contact-section" '
        'role="region" aria-labelledby="contact-title">' in body
    )
    assert 'id="contact-form-title"' in body
    assert body.count("<h1") == 1
    assert '<h1 id="hero-title">Sitios premium para vender mejor por WhatsApp.</h1>' in body
    assert (
        "Diseñamos la landing, ordenamos el mensaje y dejamos un siguiente paso claro"
        in body
    )
    assert (
        "La idea es simple: entender que necesita tu marca"
        in body
    )
    assert "Leemos el contexto" in body
    assert "Ordenamos la prioridad" in body
    assert "Respondemos con direccion" in body
    assert "Nombre" in body
    assert "Telefono o WhatsApp" in body
    assert "Que necesitas" in body
    assert "Detalles del proyecto" in body
    assert "Enviar brief" in body
    assert "Escribir por WhatsApp" in body
    assert "Phone or WhatsApp" not in body
    assert "Project details" not in body
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
