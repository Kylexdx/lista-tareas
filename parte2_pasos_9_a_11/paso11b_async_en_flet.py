# PASO 11b - Un manejador asíncrono en Flet
# Simulamos una llamada lenta a una API con asyncio.sleep y mostramos un indicador de carga.
import asyncio

import flet as ft


def main(page: ft.Page):
    page.title = "Asincronía en Flet"
    page.padding = 20

    estado = ft.Text("Pulsa el botón para simular una llamada a una API")
    anillo = ft.ProgressRing(visible=False)
    boton = ft.Button(content="Simular llamada a API")

    async def simular_llamada(e):
        # 1) Preparamos la pantalla: botón bloqueado y anillo visible
        boton.disabled = True
        anillo.visible = True
        estado.value = "Cargando datos..."
        page.update()  # el usuario ve el anillo YA, aunque el manejador no ha terminado

        # 2) Esperamos "la respuesta del servidor" sin congelar la app
        await asyncio.sleep(2)

        # 3) Llegaron los datos: restauramos la pantalla
        anillo.visible = False
        boton.disabled = False
        estado.value = "¡Datos recibidos!"
        page.update()

    boton.on_click = simular_llamada

    page.add(estado, anillo, boton)


ft.run(main)
