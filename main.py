import warnings
import networkx as nx
import pyomo.environ as pyo
import matplotlib.pyplot as plt
from typing import List
from pydantic import BaseModel, Field, ValidationError

# Ignore matplotlib warnings for a cleaner output
warnings.filterwarnings("ignore")


# =========================================================
# FASE 1: DATA VALIDATION (Pydantic)
# =========================================================
class Edge(BaseModel):
    """Represents a single edge in the logistics network."""
    source: str
    target: str
    cost: float = Field(gt=0, description="Cost must be positive")


class NetworkData(BaseModel):
    """Represents the complete network payload."""
    edges: List[Edge]


def load_and_validate_data() -> NetworkData:
    """Simulates receiving and validating raw JSON data."""
    print("--- FASE 1: Validazione Dati (Data Quality) ---")
    raw_data = {
        "edges": [
            {"source": "A", "target": "B", "cost": 10},
            {"source": "A", "target": "C", "cost": 5},
            {"source": "B", "target": "D", "cost": 10},
            {"source": "C", "target": "B", "cost": 2},
            {"source": "C", "target": "D", "cost": 20},
            {"source": "C", "target": "E", "cost": 8},
            {"source": "B", "target": "E", "cost": 4},
            {"source": "E", "target": "D", "cost": 6}
        ]
    }

    try:
        validated_data = NetworkData(**raw_data)
        print("✓ Payload validato con successo.\n")
        return validated_data
    except ValidationError as e:
        print(f"❌ Errore di validazione: {e}")
        exit(1)


# =========================================================
# FASE 2: GRAPH MODELING & VISUALIZATION (NetworkX)
# =========================================================
def build_and_visualize_graph(validated_data: NetworkData) -> nx.DiGraph:
    """Builds a directed graph and generates a visualization."""
    print("--- FASE 2: Modellazione della Rete (NetworkX) ---")

    g = nx.DiGraph()
    for edge in validated_data.edges:
        g.add_edge(edge.source, edge.target, weight=edge.cost)

    print(f"✓ Grafo generato: {g.number_of_nodes()} nodi, "
          f"{g.number_of_edges()} archi.\n")

    plt.figure(figsize=(10, 6))
    pos = {'A': (0, 1), 'B': (1, 2), 'C': (1, 0), 'E': (2, 1), 'D': (3, 1)}

    nx.draw_networkx_edges(
        g, pos, edge_color='#888888', width=2.5,
        arrowsize=25, arrowstyle='-|>', node_size=2500,
        connectionstyle="arc3,rad=0.15"
    )
    nx.draw_networkx_nodes(
        g, pos, node_color='#2C3E50', node_size=2500,
        edgecolors='white', linewidths=2
    )
    nx.draw_networkx_labels(g, pos, font_size=15, font_weight='bold', font_color='white')

    labels = {k: f"{v:g} €" for k, v in nx.get_edge_attributes(g, 'weight').items()}
    nx.draw_networkx_edge_labels(
        g, pos, edge_labels=labels, font_size=11,
        font_weight='bold', label_pos=0.3,
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.85, pad=0.3)
    )

    plt.axis('off')
    plt.title("Rete Logistica", fontsize=18,
              fontweight='bold', pad=20, color='#333333')
    plt.tight_layout()
    plt.savefig('logistic_network.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Mappa salvata come 'logistic_network.png'.\n")

    return g


# =========================================================
# FASE 3: MATHEMATICAL OPTIMIZATION (Pyomo)
# =========================================================
def optimize_logistics_path(g: nx.DiGraph, start_node: str, end_node: str):
    """Models and solves the shortest path problem using Pyomo."""
    print("--- FASE 3: Ottimizzazione Lineare (Pyomo) ---")
    print(f"Obiettivo: Minimizzare i costi da {start_node} a {end_node}")

    model = pyo.ConcreteModel()
    model.nodes = pyo.Set(initialize=list(g.nodes()))
    model.edges = pyo.Set(initialize=list(g.edges()))

    # Decision variable: 1 if edge is selected, 0 otherwise
    model.x = pyo.Var(model.edges, domain=pyo.Binary)

    # Objective function
    def minimize_cost_rule(model):
        return sum(g.edges[i, j]['weight'] * model.x[i, j] for i, j in model.edges)
    model.total_cost = pyo.Objective(rule=minimize_cost_rule, sense=pyo.minimize)

    # Constraints: Flow conservation
    model.flow_constraints = pyo.ConstraintList()
    for node in model.nodes:
        flow_out = sum(model.x[i, j] for i, j in model.edges if i == node)
        flow_in = sum(model.x[i, j] for i, j in model.edges if j == node)

        if node == start_node:
            model.flow_constraints.add(flow_out - flow_in == 1)
        elif node == end_node:
            model.flow_constraints.add(flow_out - flow_in == -1)
        else:
            model.flow_constraints.add(flow_out - flow_in == 0)

    try:
        solver = pyo.SolverFactory('glpk')
        solver.solve(model)

        print("\n🏆 --- RISULTATO OTTIMO TROVATO --- 🏆")

        # Gather activated edges
        selected_edges = []
        for i, j in model.edges:
            if pyo.value(model.x[i, j]) > 0.5:
                selected_edges.append((i, j, g.edges[i, j]['weight']))

        # Order path from start to end
        current_node = start_node
        ordered_path = []

        while current_node != end_node:
            for edge in selected_edges:
                i, j, cost = edge
                if i == current_node:
                    ordered_path.append(edge)
                    current_node = j
                    break

        for i, j, cost in ordered_path:
            print(f" 🚛 Percorri rotta: {i} -> {j} (Costo: {cost}€)")

        print(f" 💰 Costo Totale Ottimizzato: {pyo.value(model.total_cost)}€\n")

    except Exception as e:
        print("\n[INFO] Modello matematico pronto.")
        print(f"Errore solver: {e}")


# =========================================================
# MAIN EXECUTION
# =========================================================
if __name__ == "__main__":
    validated_data = load_and_validate_data()
    graph = build_and_visualize_graph(validated_data)
    optimize_logistics_path(graph, start_node='A', end_node='D')