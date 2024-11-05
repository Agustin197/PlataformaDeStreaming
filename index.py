import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# Parámetros de simulación
num_clients = 50  # Número de usuarios concurrentes (intentando conectar)
video_bitrate = 5  # Mbps por usuario
network_bandwidth = 1000  # Mbps del servidor
cpu_cores = 4  # Número de núcleos de CPU disponibles
cpu_speed = 2.5  # GHz por núcleo
memory_capacity = 16  # GB de RAM disponibles
storage_speed = 500  # MB/s de velocidad de almacenamiento (lectura/escritura)
processing_delay_base = 0.05  # Tiempo base de procesamiento en segundos por solicitud
latency_range = (0.01, 0.2)  # Latencia de red en segundos

# Límite de clientes según el ancho de banda
max_clients = network_bandwidth // video_bitrate
print(f"Ancho de banda disponible: {network_bandwidth} Mbps")
print(f"Bitrate de video: {video_bitrate} Mbps por cliente")
print(f"Máximo clientes soportados por ancho de banda: {max_clients}\n")

# Estados de recursos
cpu_usage = 0  # En GHz
memory_usage = 0  # En GB
storage_io = 0  # En MB/s
active_clients = 0  # Conteo de clientes activos

def simulate_video_stream(client_id):
    """
    Simula la transmisión de video para un cliente específico y el uso de componentes.
    """
    global cpu_usage, memory_usage, storage_io, active_clients
    
    # Calcular el uso de CPU, memoria y almacenamiento
    cpu_needed = 0.1 * cpu_speed  # Se usa un 10% de un núcleo por cliente (ajustable)
    memory_needed = 0.1  # Cada cliente usa 0.1 GB de RAM
    storage_needed = video_bitrate / 8  # Conversión de Mbps a MB/s para almacenamiento
    
    # Verificar si hay suficientes recursos disponibles
    if active_clients >= max_clients:
        print(f"ALERTA: Se alcanzó el máximo de clientes permitidos ({max_clients}). Cliente {client_id} no pudo conectarse.")
        return None
    elif (cpu_usage + cpu_needed <= cpu_cores * cpu_speed) and \
         (memory_usage + memory_needed <= memory_capacity) and \
         (storage_io + storage_needed <= storage_speed):
        
        # Asignar recursos temporales y aumentar el conteo de clientes activos
        cpu_usage += cpu_needed
        memory_usage += memory_needed
        storage_io += storage_needed
        active_clients += 1

        # Calcular la latencia de red y el tiempo total de procesamiento
        network_latency = random.uniform(*latency_range)
        processing_delay = processing_delay_base + (cpu_needed / cpu_speed)
        total_processing_time = processing_delay + network_latency
        
        print(f"Cliente {client_id} - Latencia de red: {network_latency:.3f}s, "
              f"Tiempo de procesamiento: {processing_delay:.3f}s, "
              f"Tiempo total: {total_processing_time:.3f}s")
        
        # Simular procesamiento
        time.sleep(total_processing_time)
        
        # Liberar recursos después de procesar la solicitud
        cpu_usage -= cpu_needed
        memory_usage -= memory_needed
        storage_io -= storage_needed
        active_clients -= 1
        
        return total_processing_time
    else:
        # Recursos insuficientes
        print(f"Cliente {client_id} - Recursos insuficientes: CPU={cpu_usage:.2f}GHz, "
              f"Memoria={memory_usage:.2f}GB, Almacenamiento={storage_io:.2f}MB/s")
        return None

def run_simulation():
    """
    Ejecuta la simulación del servidor de streaming de video con uso de componentes.
    """
    # Simulación en paralelo con límite de clientes y recursos
    with ThreadPoolExecutor(max_workers=max_clients) as executor:
        future_to_client = {executor.submit(simulate_video_stream, client_id): client_id for client_id in range(1, num_clients + 1)}
        
        for future in as_completed(future_to_client):
            client_id = future_to_client[future]
            try:
                result = future.result()
                if result is None:
                    print(f"Cliente {client_id} no fue atendido debido a la limitación de recursos o de clientes.")
            except Exception as exc:
                print(f"Cliente {client_id} generó una excepción: {exc}")

# Ejecutar simulación
run_simulation()
