import matplotlib.pyplot as plt
from shapely.geometry import LineString

line_string = [(85.2964994, 27.7022948), (85.2967612, 27.7022755), (85.2970328 ,27.7022274), (85.297128, 27.7022125), (85.2971609, 27.7022108), (85.2971911, 27.7022143), (85.2973205, 27.7022476)]
line = LineString(line_string)
print(line)

x, y = line.xy
plt.plot(x, y)
plt.show()
