# rules.py

"""
REQUEST PATTERN ANALİZ TASARIMI:

A. Regex (Düzenli İfadeler) Kullanımı:
   - Hedef: URL parametreleri ve Form verileri.
   - Örnek Desen: (UNION|SELECT|INSERT|DROP) -> SQL Enjeksiyonu tespiti.

B. AST (Abstract Syntax Tree) Kullanımı:
   - Hedef: JSON payloadları veya Python expression içeren girdiler.
   - Senaryo: Gelen veriyi parse edip içinde 'os.system', 'subprocess' gibi
     tehlikeli çağrılar var mı diye ağaç yapısında aranacak.
"""

def get_regex_patterns():
    pass