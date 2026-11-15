# =============================================================================
# ENTREGA FINAL - LISTA DE TAREAS CON FLET
# Módulo: ASO (2º ASIR) · UD1 · Fundamentos de GNU/Linux · Tema Flet
# -----------------------------------------------------------------------------
# Esta aplicación parte del paso 8 de "Mi primera app" (lista de tareas con
# funciones dentro de main) y le añade:
#
#   1. No permitir tareas repetidas (sin distinguir mayúsculas de minúsculas).
#   2. El contador cambia de color: ROJO si no hay ninguna tarea, VERDE si hay.
#   3. Botón «Borrar completadas» (borra las filas con la casilla marcada).
#   4. Botón de lápiz en cada tarea para MODIFICARla (con las mismas
#      validaciones que al añadir: no vacía y no repetida).
#
# Está escrito en estilo "funciones dentro de main", igual que los pasos 1-8,
# y comentado línea a línea para poder releerlo dentro de unos meses.
# =============================================================================

# 'import flet as ft': importamos la librería Flet y le damos el alias 'ft'
# para escribir ft.Text, ft.Row... en lugar de flet.Text, flet.Row...
import flet as ft


# -----------------------------------------------------------------------------
# main(page): Flet llama a esta función al arrancar y le entrega la 'page'
# (la ventana / pestaña del navegador / pantalla del móvil). Todo lo que el
# usuario ve se construye aquí dentro.
# -----------------------------------------------------------------------------
def main(page: ft.Page):
    # ---- Propiedades de la página ------------------------------------------
    page.title = "Lista de tareas"          # texto de la barra de la ventana
    page.padding = 20                       # margen interior en píxeles
    page.scroll = ft.ScrollMode.ADAPTIVE    # si hay muchas tareas, la página hace scroll

    # ---- Controles principales (los guardamos en variables para poder -------
    # ---- leerlos o modificarlos después desde las funciones) ----------------
    titulo = ft.Text("Mis tareas", size=30, weight=ft.FontWeight.BOLD)

    # Campo donde se escribe la nueva tarea. expand=True: ocupa todo el ancho
    # libre de su fila, dejando el botón «Añadir» a la derecha.
    nueva_tarea = ft.TextField(label="Nueva tarea", expand=True)

    # Texto de avisos: aquí se muestran mensajes como «Tarea X, añadida
    # correctamente». Empieza vacío; cambiamos su texto y su color según el caso.
    mensaje = ft.Text("")

    # Contador de tareas pendientes. REQUISITO 2: al arrancar no hay ninguna
    # tarea, así que empieza en ROJO. Luego actualizar_contador() lo cambia.
    contador = ft.Text("Tareas pendientes: 0", color=ft.Colors.RED)

    # Columna (lista vertical) que contendrá una "fila" por cada tarea.
    # Es una lista de Python normal: tareas.controls.
    tareas = ft.Column()

    # =========================================================================
    # FUNCIONES AUXILIARES (no son manejadores de eventos: las llamamos
    # nosotros desde otras funciones)
    # =========================================================================

    def casilla_de(fila):
        """Devuelve el Checkbox de una fila de tarea.

        Estructura de cada fila (ver crear_fila):
            fila (Column)
              ├─ controls[0] = vista_normal (Row)
              │     ├─ controls[0] = Checkbox   <-- este es el que buscamos
              │     └─ controls[1] = Row con los botones editar y borrar
              └─ controls[1] = vista_edicion (Row)
        Centralizar el acceso aquí evita escribir fila.controls[0].controls[0]
        por todas partes (y si cambia la estructura, solo se toca esta función).
        """
        return fila.controls[0].controls[0]

    def normalizar(texto):
        """Prepara un texto para COMPARARLO (no para mostrarlo).

        - split() + join(): quita espacios sobrantes al principio, al final y
          los dobles del medio ("comprar   pan" -> "comprar pan").
        - casefold(): pasa a minúsculas de forma completa. Es la forma
          recomendada de comparar sin distinguir mayúsculas (mejor que lower()
          con letras como la «ß» alemana).
        """
        return " ".join(texto.split()).casefold()

    def existe_tarea(texto, ignorar=None):
        """True si ya hay una tarea con ese texto (sin distinguir mayúsculas).

        'ignorar' sirve al MODIFICAR: la tarea que estamos editando no debe
        compararse consigo misma (si no, no podríamos guardarla sin cambios
        ni cambiar "pan" por "Pan").
        """
        buscado = normalizar(texto)
        for fila in tareas.controls:
            if fila is ignorar:          # 'is' = es exactamente el mismo objeto
                continue                 # saltamos a la siguiente fila
            if normalizar(casilla_de(fila).label) == buscado:
                return True
        return False

    def mostrar_mensaje(texto, color):
        """Cambia el texto y el color del aviso. No llama a page.update():
        lo hace quien nos llama, justo después."""
        mensaje.value = texto
        mensaje.color = color

    def actualizar_contador(e=None):
        """Recalcula el contador a partir del estado real de la lista.

        e=None permite llamarla de dos formas: como manejador (Flet pasa 'e',
        por ejemplo desde el on_change de un Checkbox) o directamente desde
        nuestro código sin argumentos.
        """
        total = len(tareas.controls)  # tareas que existen (marcadas o no)
        # Contamos 1 por cada fila cuya casilla NO está marcada (pendiente).
        pendientes = sum(1 for fila in tareas.controls if not casilla_de(fila).value)
        contador.value = f"Tareas pendientes: {pendientes}"
        # REQUISITO 2: rojo si no hay ninguna tarea definida, verde si hay alguna.
        contador.color = ft.Colors.GREEN if total > 0 else ft.Colors.RED
        page.update()  # sin esto los cambios no se ven en pantalla

    # =========================================================================
    # CREACIÓN DE UNA FILA DE TAREA
    # Cada tarea es una Column con DOS "vistas" que se alternan con visible:
    #   - vista_normal : casilla + botones editar y borrar
    #   - vista_edicion: campo de texto + botones guardar y cancelar
    # Las funciones internas (empezar_edicion, guardar_edicion...) están
    # definidas DENTRO de crear_fila: así cada tarea "recuerda" sus propios
    # controles (casilla, campo_edicion, fila...) sin necesidad de lambdas
    # complicadas. A esto se le llama closure (cierre).
    # =========================================================================
    def crear_fila(texto):
        # Casilla con el texto de la tarea. on_change: se dispara al
        # marcar/desmarcar y recalcula el contador.
        casilla = ft.Checkbox(label=texto, expand=True, on_change=actualizar_contador)

        # Campo que aparece solo al editar. on_submit: Enter = guardar.
        campo_edicion = ft.TextField(expand=True)

        # ---- Manejadores de la edición (REQUISITO 4) -----------------------
        def empezar_edicion(e):
            campo_edicion.value = casilla.label   # precargamos el texto actual
            campo_edicion.error = None
            vista_normal.visible = False          # ocultamos la vista normal...
            vista_edicion.visible = True          # ...y mostramos la de edición
            page.update()

        def cancelar_edicion(e):
            campo_edicion.error = None
            vista_normal.visible = True
            vista_edicion.visible = False
            page.update()

        def guardar_edicion(e):
            nuevo = campo_edicion.value.strip()

            # Validación 1: no se permite dejarla vacía.
            if not nuevo:
                campo_edicion.error = "La tarea no puede estar vacía"
                page.update()
                return  # salimos sin guardar

            # Validación 2 (REQUISITO 1 aplicado también al modificar):
            # no puede coincidir con OTRA tarea. ignorar=fila excluye a esta.
            if existe_tarea(nuevo, ignorar=fila):
                campo_edicion.error = "Ya existe otra tarea igual"
                mostrar_mensaje(
                    f"Tarea {nuevo} ya existe, no se puede modificar",
                    ft.Colors.ORANGE,
                )
                page.update()
                return

            # Todo correcto: guardamos el texto nuevo y volvemos a la vista normal.
            anterior = casilla.label
            casilla.label = nuevo
            campo_edicion.error = None
            vista_normal.visible = True
            vista_edicion.visible = False
            mostrar_mensaje(
                f"Tarea {anterior}, modificada a {nuevo} correctamente",
                ft.Colors.BLUE,
            )
            page.update()

        campo_edicion.on_submit = guardar_edicion  # Enter en el campo = guardar

        # ---- Vista normal: casilla + lápiz + papelera ----------------------
        vista_normal = ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                casilla,  # controls[0]: casilla_de(fila) depende de esto
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CREATE_OUTLINED,
                            tooltip="Modificar tarea",
                            on_click=empezar_edicion,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=ft.Colors.RED_400,
                            tooltip="Eliminar tarea",
                            # lambda: Flet solo entrega 'e' al manejador, pero
                            # eliminar_tarea necesita saber QUÉ fila borrar.
                            on_click=lambda e: eliminar_tarea(fila),
                        ),
                    ],
                ),
            ],
        )

        # ---- Vista de edición: campo + guardar + cancelar (oculta al inicio)
        vista_edicion = ft.Row(
            visible=False,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                campo_edicion,
                ft.IconButton(
                    icon=ft.Icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.Colors.GREEN,
                    tooltip="Guardar cambios",
                    on_click=guardar_edicion,
                ),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    tooltip="Cancelar",
                    on_click=cancelar_edicion,
                ),
            ],
        )

        # La fila completa de la tarea: las dos vistas, una encima de otra
        # (solo una es visible cada vez).
        fila = ft.Column(spacing=0, controls=[vista_normal, vista_edicion])
        return fila

    # =========================================================================
    # MANEJADORES DE EVENTOS (los que Flet llama al hacer clic, Enter...)
    # =========================================================================

    def eliminar_tarea(fila):
        texto = casilla_de(fila).label
        tareas.controls.remove(fila)  # quitamos esa fila de la lista
        mostrar_mensaje(f"Tarea {texto}, borrada correctamente", ft.Colors.RED)
        actualizar_contador()         # recalcula, cambia el color y hace page.update()

    def añadir_tarea(e):
        texto = nueva_tarea.value.strip()  # strip(): quita espacios sobrantes

        # Validación 1: campo vacío.
        if not texto:
            nueva_tarea.error = "Escribe una tarea"
            page.update()
            return

        # Validación 2 (REQUISITO 1): tarea repetida, sin distinguir mayúsculas.
        if existe_tarea(texto):
            nueva_tarea.error = None  # el aviso va en naranja, no como error rojo
            mostrar_mensaje(
                f"Tarea {texto} ya existe, no se puede añadir", ft.Colors.ORANGE
            )
            page.update()
            return  # NO se añade nada (y dejamos el texto escrito para corregirlo)

        # Todo correcto: creamos la fila y la añadimos a la columna de tareas.
        nueva_tarea.error = None
        tareas.controls.append(crear_fila(texto))
        nueva_tarea.value = ""  # vaciamos el campo para la siguiente tarea
        mostrar_mensaje(f"Tarea {texto}, añadida correctamente", ft.Colors.GREEN)
        actualizar_contador()   # incluye page.update()

    def borrar_completadas(e):
        # REQUISITO 3. Recorremos una COPIA de la lista ([:]) porque vamos a
        # borrar elementos mientras recorremos; hacerlo sobre la original
        # provocaría saltos (se "salta" el elemento siguiente al borrado).
        borradas = 0
        for fila in tareas.controls[:]:
            if casilla_de(fila).value:       # True = casilla marcada = completada
                tareas.controls.remove(fila)
                borradas += 1

        if borradas == 0:
            mostrar_mensaje("No hay tareas completadas que borrar", ft.Colors.ORANGE)
        else:
            mostrar_mensaje(
                f"Tareas completadas borradas: {borradas}", ft.Colors.RED
            )
        actualizar_contador()  # actualiza el número y el color (rojo si queda vacía)

    # =========================================================================
    # BOTONES Y MONTAJE DE LA PANTALLA
    # =========================================================================
    boton_añadir = ft.Button(content="Añadir", on_click=añadir_tarea)
    boton_borrar_completadas = ft.OutlinedButton(
        content="Borrar completadas", on_click=borrar_completadas
    )

    # Asignamos on_submit (tecla Enter) DESPUÉS de definir añadir_tarea:
    # al crear el TextField esa función todavía no existía.
    nueva_tarea.on_submit = añadir_tarea

    # page.add coloca los controles uno debajo de otro, en este orden.
    page.add(
        titulo,
        ft.Row([nueva_tarea, boton_añadir]),             # campo + botón en horizontal
        mensaje,
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # uno a cada extremo
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[contador, boton_borrar_completadas],
        ),
        tareas,
    )


# Arranca la aplicación. Se pasa 'main' SIN paréntesis: le damos la función,
# no el resultado de ejecutarla.
ft.run(main)
