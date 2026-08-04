import os

os.system("title HoopCoach AI")
print("Iniciando HoopCoach AI...")

from HoopCoach_AI import iniciar_entrenamiento
from Balon_AI import iniciar_deteccion_balon


def mostrar_menu():

    while True:

        print("\n===================================")
        print("         HOOPCOACH AI")
        print("===================================")
        print("1. Analizar técnica de lanzamiento")
        print("2. Detectar balón")
        print("3. Salir")
        print("===================================")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":

            print("\nIniciando análisis de postura...\n")
            iniciar_entrenamiento()

        elif opcion == "2":

            print("\nIniciando detección de balón...\n")
            iniciar_deteccion_balon()

        elif opcion == "3":

            print("\nGracias por usar HoopCoach AI.")
            break

        else:

            print("\nOpción inválida. Intente nuevamente.")


if __name__ == "__main__":
    mostrar_menu()