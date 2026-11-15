# PASO 10b - Filtros (todas / activas / completadas) y "Borrar completadas"
# before_update decide qué tareas se ven según la pestaña seleccionada.
from typing import Callable

import flet as ft


@ft.control
class Tarea(ft.Column):
    nombre: str = ""  # campo: texto de la tarea
    # Callbacks: funciones que pasa el "dueño" de la lista.
    # Se llaman on_...: convención de Flet para funciones y eventos
    on_borrar: Callable | None = None  # al pulsar borrar
    on_cambio: Callable | None = None  # al marcar/desmarcar

    def init(self):
        # Se ejecuta al crear la tarea: aquí se construye su interfaz
        self.completada = False
        self.casilla = ft.Checkbox(
            value=False, label=self.nombre, on_change=self.cambio_estado
        )
        self.campo_edicion = ft.TextField(expand=True)

        # Vista normal: casilla + botones editar y borrar
        self.vista_normal = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.casilla,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CREATE_OUTLINED,
                            tooltip="Editar tarea",
                            on_click=self.clic_editar,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            tooltip="Eliminar tarea",
                            on_click=self.clic_borrar,
                        ),
                    ],
                ),
            ],
        )

        # Vista de edición: campo de texto + botón guardar (oculta al empezar)
        self.vista_edicion = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.campo_edicion,
                ft.IconButton(
                    icon=ft.Icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.Colors.GREEN,
                    tooltip="Guardar cambios",
                    on_click=self.clic_guardar,
                ),
            ],
        )

        self.controls = [self.vista_normal, self.vista_edicion]

    def clic_editar(self, e):
        self.campo_edicion.value = self.casilla.label
        self.vista_normal.visible = False
        self.vista_edicion.visible = True
        self.update()

    def clic_guardar(self, e):
        nuevo_texto = self.campo_edicion.value.strip()

        if not nuevo_texto:
            self.campo_edicion.error = "La tarea no puede estar vacía"
            self.update()
            return

        self.campo_edicion.error = None
        self.casilla.label = nuevo_texto
        self.vista_normal.visible = True
        self.vista_edicion.visible = False
        self.update()

    def cambio_estado(self, e):
        self.completada = self.casilla.value
        self.on_cambio()

    def clic_borrar(self, e):
        self.on_borrar(self)


@ft.control
class AppTareas(ft.Column):
    def init(self):
        self.width = 600  # ancho fijo de la app

        self.nueva_tarea = ft.TextField(
            label="Nueva tarea", expand=True, on_submit=self.clic_añadir
        )
        self.tareas = ft.Column()

        # Pestañas de filtro (estructura TabBar dentro de Tabs)
        self.pestanas = ft.TabBar(
            scrollable=False,
            tabs=[
                ft.Tab(label="todas"),
                ft.Tab(label="activas"),
                ft.Tab(label="completadas"),
            ],
        )
        self.filtro = ft.Tabs(
            length=3,
            selected_index=0,
            on_change=self.cambio_filtro,
            content=self.pestanas,
        )

        self.contador = ft.Text("Tareas pendientes: 0")

        self.controls = [
            ft.Row(
                [ft.Text("Mis tareas", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [
                    self.nueva_tarea,
                    ft.Button(content="Añadir", on_click=self.clic_añadir),
                ]
            ),
            ft.Column(
                spacing=25,
                controls=[
                    self.filtro,
                    self.tareas,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.contador,
                            ft.OutlinedButton(
                                content="Borrar completadas",
                                on_click=self.clic_limpiar,
                            ),
                        ],
                    ),
                ],
            ),
        ]

    def clic_añadir(self, e):
        texto = self.nueva_tarea.value.strip()

        if not texto:
            self.nueva_tarea.error = "Escribe una tarea"
            self.update()
            return

        self.nueva_tarea.error = None
        self.tareas.controls.append(
            Tarea(nombre=texto, on_borrar=self.eliminar_tarea, on_cambio=self.update)
        )
        self.nueva_tarea.value = ""
        self.update()

    def eliminar_tarea(self, tarea):
        self.tareas.controls.remove(tarea)
        self.update()

    def clic_limpiar(self, e):
        # [:] recorre una COPIA de la lista, porque vamos a borrar mientras iteramos
        for tarea in self.tareas.controls[:]:
            if tarea.completada:
                self.tareas.controls.remove(tarea)
        self.update()

    def cambio_filtro(self, e):
        self.update()

    def before_update(self):
        filtro = self.pestanas.tabs[self.filtro.selected_index].label
        pendientes = 0

        for tarea in self.tareas.controls:
            tarea.visible = (
                filtro == "todas"
                or (filtro == "activas" and not tarea.completada)
                or (filtro == "completadas" and tarea.completada)
            )
            if not tarea.completada:
                pendientes += 1

        self.contador.value = f"Tareas pendientes: {pendientes}"


def main(page: ft.Page):
    page.title = "Lista de tareas"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.add(AppTareas())


ft.run(main)
