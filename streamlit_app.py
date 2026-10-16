import streamlit as st
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import importlib
import hospital
import app

importlib.reload(hospital)
importlib.reload(app)

from app import g, load_graph, find_hospital, rank_hospitals, simulate_incident
from hospital import hospitals, load_hospitals

# Set minimal student-project page layout
st.set_page_config(
    page_title="SmartRoute — Emergency Routing System",
    page_icon="🚑",
    layout="wide"
)

# Header
st.title("SmartRoute — Emergency Hospital Selection & Route Optimization")
st.caption("Academic Simulation Prototype | Capacity-Aware Hospital Intelligence & Emergency Incident Simulator")

# Load baseline data from JSON (read-only reference)
current_hospitals = load_hospitals()
baseline_graph = load_graph()

# Collect available graph locations
available_locations = sorted(list(baseline_graph.graph.keys()))

# Extract unique existing undirected roads from baseline
existing_roads = []
seen_roads = set()
for src in sorted(baseline_graph.graph.keys()):
    for dst, dist in sorted(baseline_graph.graph[src]):
        pair = tuple(sorted([src, dst]))
        if pair not in seen_roads:
            seen_roads.add(pair)
            existing_roads.append((pair[0], pair[1], dist))

# Extract unique specializations
specializations = sorted(list({
    spec.strip().title()
    for h in current_hospitals.values()
    for spec in h.get("specializations", [])
}))

# Layout columns: Left for Dispatch & Incident Simulator, Right for Network Graph
col_controls, col_visual = st.columns([1, 2], gap="large")

with col_controls:
    st.subheader("1. Emergency Dispatch Inputs")
    
    # Emergency Location selection
    selected_location = st.selectbox(
        "Emergency Location (Origin Node)",
        options=available_locations,
        index=0 if "A" in available_locations else 0,
        help="Select the network node where the incident/emergency occurred."
    )
    
    # Emergency Type selection
    emergency_type_options = specializations + ["Other / Unspecified"]
    selected_spec_choice = st.selectbox(
        "Emergency Type / Required Specialty",
        options=emergency_type_options,
        index=0,
        help="Choose medical condition to match hospital specialization."
    )
    
    if selected_spec_choice == "Other / Unspecified":
        custom_spec = st.text_input("Specify Medical Need:", value="Pediatrics")
        emergency_type = custom_spec.strip()
    else:
        emergency_type = selected_spec_choice

    # Calculate baseline (before incident) recommendations
    baseline_options = rank_hospitals(baseline_graph, selected_location, emergency_type)
    top_before = baseline_options[0] if baseline_options else None

    # Section 2: Emergency Incident Simulator
    st.markdown("---")
    st.subheader("2. Emergency Incident Simulator")
    st.caption("Simulate dynamic road closures or traffic congestion in memory. (Original data is never modified).")

    # Road selection
    road_labels = [f"Road {u} ↔ {v} (Normal Distance: {w})" for u, v, w in existing_roads]
    selected_road_idx = st.selectbox(
        "Select Road to Simulate Incident:",
        options=range(len(existing_roads)),
        format_func=lambda i: road_labels[i],
        key="selected_road_idx"
    )
    road_u, road_v, road_orig_dist = existing_roads[selected_road_idx]

    # Incident type selection
    incident_options = [
        "None (Normal Road Network)",
        "Road Closure (Complete Obstruction)",
        "Traffic Increase (Congestion Delay)"
    ]
    incident_mode = st.radio(
        "Incident Condition:",
        options=incident_options,
        index=0,
        key="incident_mode",
        horizontal=False
    )

    traffic_delay = 0
    if incident_mode == "Traffic Increase (Congestion Delay)":
        traffic_delay = st.slider(
            f"Congestion Delay Added to Road {road_u} ↔ {road_v}:",
            min_value=1,
            max_value=30,
            value=6,
            step=1,
            help="Adds extra travel distance/time units to the road weight."
        )

    # Reset / Restore callback to safely reset widget states before next rerun
    def reset_road_network():
        st.session_state["incident_mode"] = "None (Normal Road Network)"
        st.session_state["selected_road_idx"] = 0

    st.button(
        "🔄 Reset / Restore Road Network",
        on_click=reset_road_network,
        help="Clears simulated incidents and restores original baseline network."
    )


    # Apply in-memory simulation without modifying roads.json
    if incident_mode == "Road Closure (Complete Obstruction)":
        active_incident = "closure"
        sim_graph = simulate_incident(baseline_graph, road_u, road_v, "closure")
    elif incident_mode == "Traffic Increase (Congestion Delay)":
        active_incident = "traffic"
        sim_graph = simulate_incident(baseline_graph, road_u, road_v, "traffic", traffic_delay)
    else:
        active_incident = None
        sim_graph = baseline_graph.clone()

    # Recalculate options on the simulated graph
    sim_options = rank_hospitals(sim_graph, selected_location, emergency_type)
    top_after = sim_options[0] if sim_options else None

    # Section 3: Before-and-After Comparison (when incident active)
    st.markdown("---")
    if active_incident is not None:
        st.subheader("3. Incident Impact Comparison (Before vs. After)")
        
        comp_col1, comp_col2 = st.columns(2)
        with comp_col1:
            st.markdown("**📍 Before Incident (Baseline)**")
            if top_before:
                st.write(f"- **Hospital:** {top_before['name']} (Node {top_before['location']})")
                st.write(f"- **Route:** `{' ➔ '.join(top_before['path'])}`")
                st.write(f"- **Route Cost:** **{top_before['distance']} units**")
                st.write(f"- **Score:** `{top_before['score']:.2f}`")
            else:
                st.write("*No eligible hospital before incident.*")

        with comp_col2:
            incident_tag = "⛔ Road Closed" if active_incident == "closure" else f"⚠️ +{traffic_delay} Delay"
            st.markdown(f"**⚡ After Incident ({incident_tag})**")
            if top_after:
                st.write(f"- **Hospital:** {top_after['name']} (Node {top_after['location']})")
                st.write(f"- **Route:** `{' ➔ '.join(top_after['path'])}`")
                st.write(f"- **Route Cost:** **{top_after['distance']} units**")
                st.write(f"- **Score:** `{top_after['score']:.2f}`")
            else:
                st.write("- **Hospital:** *None Reachable*")
                st.write("- **Route:** *Blocked*")
                st.write("- **Route Cost:** *∞ (Unreachable)*")

        # Recommendation change outcome indicator
        if not top_before and not top_after:
            st.info("ℹ️ No eligible hospital found either before or after incident.")
        elif top_before and not top_after:
            st.error(
                f"🚨 **Recommendation Changed: No Facility Reachable!** Road incident on {road_u}–{road_v} "
                f"severed all accessible paths to eligible facilities from Node {selected_location}."
            )
        elif top_before and top_after and top_before["name"] != top_after["name"]:
            st.warning(
                f"⚠️ **Recommendation Changed!** Shifted from **{top_before['name']}** (Node {top_before['location']}) "
                f"to **{top_after['name']}** (Node {top_after['location']}) due to incident on road {road_u}–{road_v}."
            )
        elif top_before and top_after and top_before["name"] == top_after["name"]:
            cost_diff = top_after["distance"] - top_before["distance"]
            if cost_diff > 0:
                st.info(
                    f"ℹ️ **Recommendation Unchanged, but Cost Increased:** **{top_after['name']}** remains the top recommendation, "
                    f"but route cost increased by **+{cost_diff} units** ({top_before['distance']} ➔ {top_after['distance']}) "
                    f"due to detour or congestion."
                )
            else:
                st.success(
                    f"✅ **Recommendation & Route Unaffected:** The optimal route to **{top_after['name']}** "
                    f"does not traverse road {road_u}–{road_v}."
                )
    else:
        st.subheader("3. Active Dispatch Decision (Baseline)")

    # Current Active Recommendations Table
    if sim_options:
        top_hosp = sim_options[0]
        
        # Facility route selection for visualization
        if len(sim_options) > 1:
            target_facility_name = st.selectbox(
                "Route to Highlight on Network Graph:",
                options=[h["name"] for h in sim_options],
                index=0,
                help="Defaults to Rank #1. Select another eligible facility to view its alternate route on the graph."
            )
            active_hosp = next(h for h in sim_options if h["name"] == target_facility_name)
        else:
            active_hosp = top_hosp

        route_path = active_hosp["path"]
        route_cost = active_hosp["distance"]
        dest_location = active_hosp["location"]

        st.markdown(f"**Top Recommended Facility:** **{top_hosp['name']}** (Node {top_hosp['location']})")
        st.markdown(f"**Active Route:** `{' ➔ '.join(active_hosp['path'])}` | **Distance:** {active_hosp['distance']} units | **Score:** {active_hosp['score']:.2f}")
        st.write(f"- Available Capacity: **{top_hosp['beds']} beds**, **{top_hosp['icu']} ICU units**")
        st.info(f"**Recommendation Explanation:** {top_hosp['explanation']}")
        
    else:
        route_path = []
        route_cost = float("inf")
        dest_location = None
        st.warning("No suitable hospital or reachable route found.")
        st.markdown(
            f"No hospital matching '**{emergency_type}**' with available beds (>0) and ICU units (>0) "
            f"is reachable from Node **{selected_location}** under current network conditions."
        )


with col_visual:
    st.subheader("Network Graph & Dynamic Route Visualization")
    
    # Build NetworkX graph from simulated in-memory graph
    G = nx.Graph()
    for node in available_locations:
        G.add_node(node)
        
    for src in sim_graph.graph:
        for dst, dist in sim_graph.graph[src]:
            if not G.has_edge(src, dst):
                G.add_edge(src, dst, weight=dist)

    # Fixed deterministic spring layout
    pos = nx.spring_layout(G, seed=42, k=1.0)
    
    # Map hospital nodes
    hospital_nodes = {
        details["location"]: name
        for name, details in current_hospitals.items()
        if details["location"] in G.nodes
    }

    # Identify edges on the active route
    route_edges = []
    if route_path and len(route_path) > 1:
        for i in range(len(route_path) - 1):
            route_edges.append((route_path[i], route_path[i + 1]))

    route_edge_set = set(route_edges) | {(v, u) for u, v in route_edges}

    # Incident edge pair
    incident_edge = tuple(sorted([road_u, road_v])) if active_incident else None

    # Separate standard edges vs affected edges
    standard_edges = [
        e for e in G.edges 
        if e not in route_edge_set and tuple(sorted([e[0], e[1]])) != incident_edge
    ]

    # Create Matplotlib Figure
    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=120)
    ax.set_facecolor("#ffffff")
    fig.patch.set_facecolor("#ffffff")

    # 1. Draw standard roads (normal gray edges)
    nx.draw_networkx_edges(
        G, pos,
        edgelist=standard_edges,
        width=1.6,
        edge_color="#94a3b8",
        ax=ax
    )

    # 2. Draw affected road (incident visualization)
    if active_incident == "closure":
        # Road is removed from sim_graph; overlay it as a dashed red edge
        nx.draw_networkx_edges(
            G, pos,
            edgelist=[(road_u, road_v)],
            width=2.8,
            style="dashed",
            edge_color="#ef4444",
            ax=ax
        )
    elif active_incident == "traffic":
        # Congested road: if not on active route, draw with bold amber color
        if (road_u, road_v) not in route_edge_set and (road_v, road_u) not in route_edge_set:
            nx.draw_networkx_edges(
                G, pos,
                edgelist=[(road_u, road_v)],
                width=3.4,
                edge_color="#f59e0b",
                ax=ax
            )

    # 3. Draw active route roads (highlighted red edges)
    if route_edges:
        nx.draw_networkx_edges(
            G, pos,
            edgelist=route_edges,
            width=4.0,
            edge_color="#dc2626",
            ax=ax
        )

    # 4. Draw edge weight labels (distances)
    edge_weights = {(u, v): str(d["weight"]) for u, v, d in G.edges(data=True)}
    
    # If closure, show CLOSED label on affected edge
    if active_incident == "closure":
        edge_weights[(road_u, road_v)] = "CLOSED"
    elif active_incident == "traffic" and (road_u, road_v) in G.edges:
        edge_weights[(road_u, road_v)] = f"{road_orig_dist + traffic_delay} (+{traffic_delay})"

    # Edge labels styling
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_weights,
        font_size=9,
        font_color="#1e293b",
        font_family="sans-serif",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", edgecolor="#cbd5e1", lw=0.8),
        ax=ax
    )

    # 5. Draw nodes by category
    route_node_set = set(route_path) if route_path else set()
    
    ordinary_nodes = []
    hosp_nodes_list = []
    route_intermediate_nodes = []

    for n in G.nodes:
        if n == selected_location or n == dest_location:
            continue
        if n in route_node_set:
            route_intermediate_nodes.append(n)
        elif n in hospital_nodes:
            hosp_nodes_list.append(n)
        else:
            ordinary_nodes.append(n)

    if ordinary_nodes:
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=ordinary_nodes,
            node_color="#f1f5f9",
            edgecolors="#64748b",
            node_size=800,
            linewidths=1.5,
            ax=ax
        )

    if hosp_nodes_list:
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=hosp_nodes_list,
            node_color="#dcfce7",
            edgecolors="#16a34a",
            node_size=800,
            linewidths=1.5,
            ax=ax
        )

    if route_intermediate_nodes:
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=route_intermediate_nodes,
            node_color="#fee2e2",
            edgecolors="#ef4444",
            node_size=850,
            linewidths=2.0,
            ax=ax
        )

    # Destination Hospital Node
    if dest_location and dest_location in G.nodes:
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=[dest_location],
            node_color="#86efac",
            edgecolors="#15803d",
            node_size=1050,
            linewidths=2.5,
            ax=ax
        )

    # Origin / Emergency Location Node
    if selected_location in G.nodes:
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=[selected_location],
            node_color="#fed7aa",
            edgecolors="#c2410c",
            node_size=1050,
            linewidths=2.5,
            ax=ax
        )

    # Node labels
    node_labels = {}
    for n in G.nodes:
        if n in hospital_nodes:
            node_labels[n] = f"{n}\n[{hospital_nodes[n]}]"
        else:
            node_labels[n] = n

    nx.draw_networkx_labels(
        G, pos,
        labels=node_labels,
        font_size=8.5,
        font_weight="bold",
        font_color="#0f172a",
        ax=ax
    )

    # Dynamic Legend reflecting current state
    legend_handles = [
        plt.Line2D([0], [0], color="#dc2626", lw=3.5, label="Optimized Route"),
        plt.Line2D([0], [0], color="#94a3b8", lw=1.5, label="Standard Road"),
    ]
    if active_incident == "closure":
        legend_handles.append(
            plt.Line2D([0], [0], color="#ef4444", lw=2.5, linestyle="--", label=f"Closed Road ({road_u}–{road_v})")
        )
    elif active_incident == "traffic":
        legend_handles.append(
            plt.Line2D([0], [0], color="#f59e0b", lw=3.0, label=f"Congested Road (+{traffic_delay})")
        )

    legend_handles.extend([
        plt.Line2D([0], [0], marker="o", color="w", label="Emergency Origin (Start)",
                   markerfacecolor="#fed7aa", markeredgecolor="#c2410c", markersize=9, markeredgewidth=1.5),
        plt.Line2D([0], [0], marker="o", color="w", label="Selected Hospital (Destination)",
                   markerfacecolor="#86efac", markeredgecolor="#15803d", markersize=9, markeredgewidth=1.5),
        plt.Line2D([0], [0], marker="o", color="w", label="Hospital Facility Node",
                   markerfacecolor="#dcfce7", markeredgecolor="#16a34a", markersize=8, markeredgewidth=1.2),
        plt.Line2D([0], [0], marker="o", color="w", label="Intersection Node",
                   markerfacecolor="#f1f5f9", markeredgecolor="#64748b", markersize=8, markeredgewidth=1.2),
    ])

    ax.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.04),
        ncol=3,
        fontsize=8,
        frameon=True,
        facecolor="#f8fafc",
        edgecolor="#cbd5e1"
    )

    title_suffix = f" — Incident Active on {road_u}–{road_v}" if active_incident else ""
    ax.set_title(f"Simulated Graph Topology & Route Map{title_suffix}", fontsize=11, fontweight="bold", pad=12)
    ax.axis("off")
    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    # Ranked Facility Options Table
    if sim_options:
        st.markdown("#### Ranked Facility Options")
        st.caption("Eligible facilities ordered by composite capacity-to-distance score:")
        ranked_display = [
            {
                "Rank": f"#{h['rank']}" + (" ★ Top" if h['rank'] == 1 else ""),
                "Hospital": h["name"],
                "Node": h["location"],
                "Distance": h["distance"],
                "Beds": h["beds"],
                "ICU": h["icu"],
                "Score": f"{h['score']:.2f}",
                "Explanation": h["explanation"]
            }
            for h in sim_options
        ]
        st.dataframe(
            ranked_display,
            width="stretch",
            hide_index=True,
            column_config={
                "Rank": st.column_config.TextColumn("Rank", width="small"),
                "Hospital": st.column_config.TextColumn("Hospital", width="medium"),
                "Node": st.column_config.TextColumn("Node", width="small"),
                "Distance": st.column_config.NumberColumn("Distance (units)", format="%d", width="small"),
                "Beds": st.column_config.NumberColumn("Beds", format="%d", width="small"),
                "ICU": st.column_config.NumberColumn("ICU", format="%d", width="small"),
                "Score": st.column_config.TextColumn("Score", width="small"),
                "Explanation": st.column_config.TextColumn("Recommendation Explanation", width="large"),
            }
        )


# Collapsible reference data inspect
with st.expander("System Reference Data (Hospitals & Road Network)", expanded=False):
    tab_hosp, tab_roads = st.tabs(["Hospitals Roster", "Road Segments"])
    
    with tab_hosp:
        hosp_table = [
            {
                "Hospital": name,
                "Node": data["location"],
                "Specializations": ", ".join(data.get("specializations", [])),
                "Beds": data.get("beds", 0),
                "ICU": data.get("icu", 0),
            }
            for name, data in current_hospitals.items()
        ]
        st.dataframe(hosp_table, width="stretch")
        
    with tab_roads:
        road_table = []
        seen = set()
        for src in baseline_graph.graph:
            for dst, dist in baseline_graph.graph[src]:
                pair = tuple(sorted([src, dst]))
                if pair not in seen:
                    seen.add(pair)
                    road_table.append({
                        "Source Node": src,
                        "Destination Node": dst,
                        "Distance / Cost": dist
                    })
        st.dataframe(road_table, width="stretch")
