import os

files = [
    'scripts/extract.py', 
    'scripts/transform.py', 
    'scripts/load.py', 
    'scripts/run_pipeline.py'
]

for f in files:
    if os.path.exists(f):
        with open(f, 'rb') as file:
            content = file.read()
        
        if b'\x00' in content:
            with open(f, 'wb') as file:
                file.write(content.replace(b'\x00', b''))
            print(f"✅ Réparé : {f}")
        else:
            print(f"👌 OK : {f}")
    else:
        print(f"❌ Introuvable : {f}")

print("\n🎉 Vérification terminée ! Vous pouvez lancer le pipeline.")