from parser import *
from solver import *
from matplotlib import pyplot as plt

nodes, branches, time_step, element_name =  scheme_data("config.json")
G_n, G_b, J_b, A, elements = load_json("config.json", nodes, branches, time_step)

# Создается объект решателя
solution = Solver(G_n, G_b, J_b, A, elements)

U_t, I_t, time = solution.solve(time_step, 1e-3, element_name)

#region
U_t = [U*1e12 for U in U_t]
I_t = [I*1e12 for I in I_t]
fig, ax = plt.subplots(figsize=(10, 6))
ax.grid()
ax.plot(time, U_t)
plt.tight_layout()
plt.show()
#endregion


