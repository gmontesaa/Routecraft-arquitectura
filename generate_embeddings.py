import os
import django
from dotenv import load_dotenv
from openai import OpenAI

# Configurar entorno Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "routecraft.settings")
django.setup()

from places.models import Place  # importar después de django.setup()

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text):
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def generar_embeddings():
    lugares = Place.objects.filter(embedding__isnull=True)

    for lugar in lugares:
        print(f"Generando embedding para: {lugar.name}")
        descripcion = f"{lugar.name}. {lugar.description}"
        embedding = get_embedding(descripcion)
        lugar.embedding = embedding
        lugar.save()

    print("✅ Embeddings generados con éxito.")

if __name__ == "__main__":
    generar_embeddings()
