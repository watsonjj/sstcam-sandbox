from CHECOnsky.calib import get_calib_data
import yaml
from numpy.polynomial.polynomial import polyval
import numpy as np
from matplotlib import pyplot as plt

path = get_calib_data("temperature_coeff.yml")
with open(path, 'r') as file:
    temperature_dict = yaml.safe_load(file)
temperature_coeff = temperature_dict[f'temperature_coeff']
temp_max = temperature_dict['temperature_max']
temp_min = temperature_dict['temperature_min']
temperature = np.linspace(temp_min, temp_max, 100)
temperature_corr = polyval(temperature, temperature_coeff)
plt.plot(temperature, temperature_corr)
plt.xlabel("Temperature")
plt.ylabel("Correction Factor")
