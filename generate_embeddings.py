import os
import django
from dotenv import load_dotenv

# Configurar entorno Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "routecraft.settings")
django.setup()

from places.models import Place  # importar después de django.setup()
from places.adapters.openai_embeddings import OpenAIEmbeddingsClient
from places.services import EmbeddingService

load_dotenv()

def generar_embeddings():
    # Verificar API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: Falta la variable OPENAI_API_KEY en tu .env")
        return

    # Servicio de embeddings usando el adaptador
    svc = EmbeddingService(OpenAIEmbeddingsClient(api_key=api_key))

    lugares = Place.objects.filter(embedding__isnull=True)
    if not lugares.exists():
        print("No hay lugares pendientes de embeddings.")
        return

    for lugar in lugares:
        try:
            print(f"🔄 Generando embedding para: {lugar.name}")
            descripcion = f"{lugar.name}. {lugar.description or ''}"
            vector = svc.create_vectors([descripcion])[0]  # retorna lista de vectores
            lugar.embedding = vector
            lugar.save(update_fields=["embedding"])
            print(f"✅ Guardado embedding de {lugar.name}")
        except Exception as e:
            print(f"⚠️ Error generando embedding para {lugar.name}: {e}")

    print("🎉 Embeddings generados con éxito.")

if __name__ == "__main__":
    generar_embeddings()
