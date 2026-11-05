import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from flask_jwt_extended import create_access_token
from pypdf import PdfReader

from app import create_app
from app.models.iph import IPH, IPHCaptura
from app.services.pdf_generator import generar_pdf_iph


class PdfPreviewRouteTest(unittest.TestCase):
    def test_preview_without_capture_returns_valid_pdf(self):
        self.assertEqual(IPH.__table__.c.ID_IPH.name, "ID_IPH")
        self.assertEqual(
            next(iter(IPHCaptura.__table__.c.iph_id.foreign_keys)).target_fullname,
            "dbo.iph.ID_IPH",
        )
        app = create_app("development")
        app.config.update(TESTING=True)
        registro = SimpleNamespace(
            id=2110,
            folio_interno="28/41/005/00109/2026",
            no_referencia=None,
            no_expediente=None,
            fecha_puesta_disposicion=None,
            hora_puesta_disposicion=None,
            institucion=None,
            adscripcion=None,
            estado="EN_TRAMITE",
            policias=[],
            conocimiento_hecho=None,
            acta_noticia=None,
            inspeccion_lugar=None,
            narracion_primer_respondiente=None,
            denunciantes=[],
            ofendidos=[],
            victimas=[],
            testigos=[],
            imputados=[],
            inspecciones_vehiculo=[],
            acciones_realizadas=[],
            actuaciones=[],
        )

        with app.app_context():
            token = create_access_token(identity="pdf-preview-test")

        with (
            patch("app.blueprints.iph.routes._registro_legacy_para_pdf", return_value=registro),
            patch("app.blueprints.iph.routes._tabla_capturas_disponible", return_value=False),
        ):
            response = app.test_client().post(
                "/api/iph/2110/previsualizar-pdf",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "camposPorModulo": {
                        "puesta_disposicion": [
                            {"label": "Hora puesta a disposición", "value": "14:35"}
                        ]
                    }
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/pdf")
        self.assertTrue(response.data.startswith(b"%PDF-"))
        pdf = PdfReader(io.BytesIO(response.data))
        self.assertEqual(len(pdf.pages), 4)
        texto_pdf = "\n".join(page.extract_text() or "" for page in pdf.pages)
        self.assertIn("INFORME POLICIAL HOMOLOGADO", texto_pdf)
        self.assertIn("28/41/005/00109/2026", texto_pdf)
        self.assertIn("14:35", texto_pdf)

    def test_used_annex_uses_the_original_template_pages(self):
        registro = SimpleNamespace(
            folio_interno="FOLIO-ANEXO",
            no_expediente="",
            no_referencia="",
        )
        documento = generar_pdf_iph(
            registro,
            capturas={},
            campos_por_modulo={
                "puesta_disposicion": [
                    {"label": "Anexo A. Detención(es): ¿se entrega?", "value": "SI"}
                ],
                "anexo_a": [{"label": "Número RND", "value": "RND-2026-001"}],
            },
        )
        pdf = PdfReader(documento)
        self.assertEqual(len(pdf.pages), 7)
        self.assertIn("ANEXO A. DETENCIÓN", pdf.pages[4].extract_text())
        self.assertIn("RND-2026-001", "\n".join(page.extract_text() or "" for page in pdf.pages))


if __name__ == "__main__":
    unittest.main()
