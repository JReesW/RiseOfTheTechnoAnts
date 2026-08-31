import numpy as np
import opensimplex

def generate_noise_map(width: int, height: int, seed: int, amplitude=1.0, frequency=0.1, octaves=3, persistence=0.5, lacunarity=2.0):
    noise_array = np.zeros([width, height])

    for i in range(octaves):
        os = opensimplex.OpenSimplex(seed + i)

        noise_array += amplitude * os.noise2array(np.arange(0, frequency * width, frequency), np.arange(0, frequency * height, frequency))

        amplitude *= persistence
        frequency *= lacunarity

    return noise_array

def normalize_noise_map(noise_array):
    return (noise_array + 1) / 2

def noise_map_to_rgb(noise_array):
    normized_noise_array = (normalize_noise_map(noise_array) * 255).astype(np.uint8)
    
    rgb_array = np.repeat(normized_noise_array[:, :, None], 3, axis=2)
    return rgb_array