from parser import *
from solver import *
from matplotlib import pyplot as plt

nodes, branches, time_step, time_end, element_name =  scheme_data("config.json")
G_n, G_b, J_b, A, elements = load_json("config.json", nodes, branches, time_step)

# Создается объект решателя
solution = Solver(G_n, G_b, J_b, A, elements)

U_t, I_t, time = solution.solve(time_step, time_end, element_name)

#region
fig, ax = plt.subplots(figsize=(10, 6))
ax.legend(fontsize=10)
ax.minorticks_on()

ax.grid(which='major', alpha=0.3)
ax.grid(which='minor', linestyle=':', alpha=0.15)

ax.set_xlabel("t, с", fontsize=14, fontname='Courier new', fontweight='bold')
ax.set_ylabel("U, В", fontsize=14, fontname='Courier new', fontweight='bold')

U_t = [U*1e12 for U in U_t]
ax.plot(time, U_t)
plt.tight_layout()
plt.show()
#endregion


