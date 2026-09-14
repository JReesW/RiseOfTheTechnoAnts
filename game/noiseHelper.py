import numpy as np
import opensimplex
import time

def generate_noise_map(width: int, height: int, seed: int, amplitude=1.0, frequency=0.1, octaves=3, persistence=0.5, lacunarity=2.0):
    noise_array = np.zeros([height, width])
    os = opensimplex.OpenSimplex(seed)

    start = time.perf_counter()

    max_value = 0

    for i in range(octaves):
        x_array = np.arange(width) * frequency
        y_array = np.arange(height) * frequency

        # print(f"array creation: {time.perf_counter() - start}")

        next_array = os.noise2array(x_array, y_array)

        # print(f"noise creation: {time.perf_counter() - start}")

        noise_array += next_array * amplitude

        # print(f"noise applying: {time.perf_counter() - start}")

        max_value += amplitude

        amplitude *= persistence
        frequency *= lacunarity

    # print(f"end time: {time.perf_counter() - start}")

    return noise_array / max_value

def normalize_noise_map(noise_array):
    return (noise_array + 1) / 2

def noise_map_to_rgb(noise_array):
    normized_noise_array = (normalize_noise_map(noise_array) * 255).astype(np.uint8)
    
    rgb_array = np.repeat(normized_noise_array[:, :, None], 3, axis=2)
    return rgb_array