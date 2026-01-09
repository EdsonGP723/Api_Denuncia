from groq import Groq
from django.conf import settings
import json
from datetime import datetime


class AIService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def generar_denuncia(self, nombre_victima: str, clasificacion: str) -> dict:
        """
        Genera una denuncia detallada usando Groq AI
        """

        prompt = f"""Eres un asistente especializado en generar denuncias corporativas realistas y detalladas.

Genera una denuncia con los siguientes parámetros:
- Nombre de la víctima/denunciado: {nombre_victima}
- Clasificación del incidente: {clasificacion}

La denuncia debe ser realista y contextualizada para el entorno corporativo mexicano.

IMPORTANTE: Responde ÚNICAMENTE con un objeto JSON válido, sin texto adicional, siguiendo EXACTAMENTE esta estructura:

{{
  "date": "YYYY-MM-DD HH:MM:SS",
  "anonymous": true,
  "channel": "web",
  "reporter": {{
    "relationship_to_company": "employee|contractor|ex-employee|third-party",
    "country": "México"
  }},
  "people": {{
    "offender": {{
      "name": "{nombre_victima}",
      "position": "cargo del denunciado",
      "department": "departamento"
    }}
  }},
  "incident": {{
    "type": "{clasificacion}",
    "description": "descripción detallada del incidente (mínimo 50 palabras)",
    "approximate_date": "YYYY-MM",
    "is_ongoing": true|false
  }},
  "location": {{
    "city": "ciudad de México",
    "work_related": true
  }},
  "evidence": {{
    "has_evidence": true|false,
    "description": "descripción de la evidencia disponible"
  }}
}}

Requisitos:
1. La descripción del incidente debe ser específica y detallada (mínimo 50 palabras)
2. Usa contexto mexicano (ciudades, departamentos, situaciones típicas)
3. Genera datos coherentes según el tipo de incidente
4. La fecha debe ser reciente (últimos 3 meses)
5. NO incluyas comillas al inicio o final, ni texto explicativo, SOLO el JSON"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente que genera únicamente respuestas en formato JSON válido, sin texto adicional."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2048,
                response_format={"type": "json_object"}
            )

            response_text = response.choices[0].message.content.strip()

            # Limpiar posibles markdown o texto extra
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # Parsear el JSON
            denuncia_data = json.loads(response_text)

            return denuncia_data

        except json.JSONDecodeError as e:
            raise ValueError(f"Error al parsear respuesta de IA: {str(e)}")
        except Exception as e:
            if '429' in str(e) or 'rate_limit' in str(e).lower():
                raise ValueError(
                    "Límite de API excedido. Por favor intenta más tarde.")
            raise ValueError(f"Error al generar denuncia: {str(e)}")
