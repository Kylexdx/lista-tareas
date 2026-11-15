# Lista de tareas con Flet (entrega final ASO UD2)

Aplicación de lista de tareas hecha con Flet a partir del paso 8 de "Mi primera app".

Funcionalidades añadidas:
1. No permite tareas repetidas (sin distinguir mayúsculas/minúsculas), ni al añadir ni al modificar.
2. El contador es rojo si no hay ninguna tarea y verde si hay alguna.
3. Botón «Borrar completadas».
4. Botón de lápiz para modificar cada tarea.

## Ejecutar en desarrollo (Kubuntu)

    python3 -m venv env
    source env/bin/activate
    pip install flet
    flet run src/main.py          # ventana de escritorio
    flet run --web src/main.py    # versión web en local (se abre en el navegador)

## Estructura

    entrega_final/
    ├── pyproject.toml    # nombre, versión y dependencias (flet)
    ├── README.md
    └── src/
        └── main.py       # toda la app, comentada línea a línea

## Compilar para cada plataforma

Desde la carpeta del proyecto (donde está pyproject.toml), con el entorno virtual activado:

    flet build web        # -> build/web      (se prueba con: python -m http.server --directory build/web 8000)
    flet build apk        # -> build/apk      (Android)
    flet build windows    # -> build/windows  (solo desde Windows; requiere Visual Studio con C++)
    flet build linux      # -> build/linux    (desde Linux o WSL)

Alternativa sin instalar nada: subir el proyecto a GitHub; el workflow
.github/workflows/build.yml compila los 4 destinos en la nube y deja los
resultados en la pestaña Actions, en "Artifacts".
