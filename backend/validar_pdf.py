"""
Script para validar si materias específicas están en el PDF
"""
from pathlib import Path
from pypdf import PdfReader
import re

def buscar_codigos_en_pdf(pdf_path: str, codigos_buscar: list):
    """Busca códigos específicos en el PDF y muestra el contexto"""
    pdf_file = Path(pdf_path)
    
    if not pdf_file.exists():
        print(f"❌ Archivo no encontrado: {pdf_path}")
        return
    
    reader = PdfReader(pdf_file)
    texto_completo = ""
    
    print(f"📄 Leyendo PDF: {len(reader.pages)} páginas...\n")
    
    for page in reader.pages:
        texto_completo += page.extract_text() + "\n"
    
    print(f"🔍 Buscando códigos: {', '.join(codigos_buscar)}\n")
    print("=" * 80)
    
    for codigo in codigos_buscar:
        # Buscar el código en el texto (con variaciones de formato)
        patron = re.compile(
            rf'Código\s*:?\s*{re.escape(codigo)}',
            re.IGNORECASE
        )
        
        matches = list(patron.finditer(texto_completo))
        
        if matches:
            print(f"✅ Código {codigo} ENCONTRADO ({len(matches)} vez/veces):")
            for i, match in enumerate(matches, 1):
                inicio = max(0, match.start() - 200)
                fin = min(len(texto_completo), match.end() + 500)
                contexto = texto_completo[inicio:fin]
                
                # Limpiar el contexto
                contexto = contexto.replace('\n', ' ')
                contexto = re.sub(r'\s+', ' ', contexto)
                
                print(f"\n   Ocurrencia {i}:")
                print(f"   {contexto[:300]}...")
                print()
        else:
            # Buscar variaciones del código (sin espacios, con guiones, etc.)
            codigo_limpio = codigo.replace(' ', '').replace('-', '')
            patron_variaciones = re.compile(
                rf'\b{re.escape(codigo_limpio)}\b',
                re.IGNORECASE
            )
            matches_variaciones = list(patron_variaciones.finditer(texto_completo))
            
            if matches_variaciones:
                print(f"⚠️  Código {codigo} encontrado en formato diferente ({len(matches_variaciones)} vez/veces):")
                for i, match in enumerate(matches_variaciones[:3], 1):  # Solo mostrar las primeras 3
                    inicio = max(0, match.start() - 200)
                    fin = min(len(texto_completo), match.end() + 500)
                    contexto = texto_completo[inicio:fin]
                    contexto = contexto.replace('\n', ' ')
                    contexto = re.sub(r'\s+', ' ', contexto)
                    print(f"\n   Ocurrencia {i}:")
                    print(f"   {contexto[:300]}...")
            else:
                print(f"❌ Código {codigo} NO ENCONTRADO en el PDF")
        
        print("-" * 80)

if __name__ == "__main__":
    pdf_path = "data/documents/Contenido_de_las_asignaturas.pdf"
    codigos_faltantes = ["4100554", "4100557"]
    
    buscar_codigos_en_pdf(pdf_path, codigos_faltantes)

