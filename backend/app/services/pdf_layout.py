"""Coordenadas calibrables del formulario IPH2019 (puntos PDF, origen inferior izquierdo)."""

PUESTA_DISPOSICION = {
    "debug": {"color": [1, 0, 0], "line_width": 0.35, "padding": 2, "extra_height": 4, "check_size": 12},
    "fit": {"minimum_font": 4, "font_step": 0.25},
    "campos": {
        "folio": {"page": 0, "x": 356, "y": 681, "width": 195, "align": "left", "font": 7},
        "expediente": {"page": 0, "x": 445, "y": 591, "width": 130, "align": "left", "font": 7, "cells": {"count": 20, "step": 6.5}},
        "fecha": {"page": 0, "x": 77, "y": 591, "width": 110, "align": "left", "font": 7, "cells": {"count": 8, "step": 12}},
        "hora": {"page": 0, "x": 244, "y": 591, "width": 48, "align": "left", "font": 7, "cells": {"count": 4, "step": 12}},
        "anexo": {"page": 0, "font": 7, "mark_font": 7, "checks": {"A": [190, 553], "B": [190, 536], "C": [190, 518], "D": [190, 505], "E": [516, 553], "F": [516, 536], "G": [516, 518]}},
        "no_anexos": {"page": 0, "x": 517, "y": 496, "font": 7},
"conteos": {"page": 0, "font": 6, "checks": {"A": {"x": 210, "y": 553, "step": 8, "digits": 2}, "B": {"x": 210, "y": 536, "step": 8, "digits": 2}, "C": {"x": 210, "y": 518, "step": 8, "digits": 2}, "D": {"x": 210, "y": 505, "step": 8, "digits": 2}, "D_armas": {"x": 210, "y": 505, "step": 8, "digits": 2}, "D_objetos": {"x": 246, "y": 505, "step": 8, "digits": 2}, "E": {"x": 536, "y": 553, "step": 8, "digits": 2}, "F": {"x": 536, "y": 536, "step": 8, "digits": 2}, "G": {"x": 536, "y": 518, "step": 8, "digits": 2}}},
        "documentacion": {"page": 0, "font": 7, "checks": {"si": [154, 476], "no": [154, 441], "Fotografías": [350, 476], "Audio": [520, 476], "Videos": [350, 458], "Certificados médicos": [520, 458], "Otra": [350, 441]}, "otra": {"page": 0, "x": 380, "y": 441, "width": 150, "align": "left", "font": 6}},
        "persona": {
            "responsable": {
                "primer_apellido": {"page": 0, "x": 128, "y": 412, "width": 145, "align": "left", "font": 7},
                "segundo_apellido": {"page": 0, "x": 298, "y": 412, "width": 130, "align": "left", "font": 7},
                "nombres": {"page": 0, "x": 458, "y": 412, "width": 115, "align": "left", "font": 7},
                "adscripcion": {"page": 0, "x": 96, "y": 367, "width": 470, "align": "left", "font": 7},
                "cargo": {"page": 0, "x": 100, "y": 352, "width": 465, "align": "left", "font": 7},
                "firma": {"page": 0, "x": 100, "y": 337, "width": 465, "align": "left", "font": 7},
            },
            "receptor": {
                "primer_apellido": {"page": 0, "x": 128, "y": 307, "width": 145, "align": "left", "font": 7},
                "segundo_apellido": {"page": 0, "x": 298, "y": 307, "width": 130, "align": "left", "font": 7},
                "nombres": {"page": 0, "x": 458, "y": 307, "width": 115, "align": "left", "font": 7},
                "institucion": {"page": 0, "x": 145, "y": 263, "width": 430, "align": "left", "font": 7},
                "adscripcion": {"page": 0, "x": 96, "y": 248, "width": 470, "align": "left", "font": 7},
                "cargo": {"page": 0, "x": 100, "y": 232, "width": 465, "align": "left", "font": 7},
                "firma": {"page": 0, "x": 100, "y": 217, "width": 465, "align": "left", "font": 7},
                "sello": {"page": 0, "x": 100, "y": 202, "width": 465, "align": "left", "font": 7},
            },
        },
    },
}
