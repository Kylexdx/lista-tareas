# PASO 11a - Asincronía en Python puro (sin Flet, solo consola)
# Objetivo: entender async/await y comprobar por qué esperar "en paralelo" ahorra tiempo.
import asyncio
import time


async def descargar(nombre, segundos):
    print(f"[{nombre}] Empiezo la descarga...")
    await asyncio.sleep(segundos)  # espera SIN bloquear al resto del programa
    print(f"[{nombre}] Terminada.")
    return f"datos de {nombre}"


async def main():
    # 1) En secuencia: una espera a que termine la otra
    inicio = time.perf_counter()
    a = await descargar("A", 2)
    b = await descargar("B", 2)
    print(f"Secuencial: {a} y {b} en {time.perf_counter() - inicio:.1f} s\n")

    # 2) En paralelo: las dos esperas transcurren a la vez
    inicio = time.perf_counter()
    a, b = await asyncio.gather(descargar("A", 2), descargar("B", 2))
    print(f"Paralelo:   {a} y {b} en {time.perf_counter() - inicio:.1f} s")


asyncio.run(main())
