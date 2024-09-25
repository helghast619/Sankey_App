import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Streamlit app title
st.title("Sankey Diagram: Distributor to Retailer State Distribution")

# Load data from CSV
uploaded_file = st.file_uploader("Upload Distributor Data CSV", type=["csv"])

if uploaded_file is not None:
    # Read the uploaded CSV file
    df = pd.read_csv(uploaded_file)

    # Data preprocessing
    df = df.dropna(subset=['distributor_state', 'retailer_state'])
    df['scans'] = pd.to_numeric(df['scans'], errors='coerce')
    df = df.dropna(subset=['scans'])

    # Create a list of unique states for each category
    distributor_states = df['distributor_state'].unique()
    retailer_states = df['retailer_state'].unique()

    # Combine into a single list of unique nodes for the Sankey chart
    all_states = list(distributor_states) + list(retailer_states)

    # Create a dictionary to map states to node indices
    state_indices = {state: i for i, state in enumerate(all_states)}

    # Create the source, target, and value lists for the Sankey chart
    sources = [state_indices[state] for state in df['distributor_state']]
    targets = [state_indices[state] for state in df['retailer_state']]

    # Calculate the percentage distribution for each retailer based on the distributor
    df['percentage'] = (df['scans'] / df.groupby('distributor_state')['scans'].transform('sum')) * 100
    values = df['percentage']

    # Set the x-coordinates: 0.1 for distributors and 0.9 for retailers
    x_coords = [0.1 if state in distributor_states else 0.9 for state in all_states]

    # Set the y-coordinates with adjusted spacing
    distributor_count = len(distributor_states)
    retailer_count = len(retailer_states)
    base_spacing = 0.05
    y_coords_distributors = [i * (1 / (distributor_count + 1)) + base_spacing for i in range(distributor_count)]
    y_coords_retailers = [i * (1 / (retailer_count + 1)) + base_spacing + 0.01 for i in range(retailer_count)]
    y_coords = y_coords_distributors + y_coords_retailers

    # Define colors for nodes and flows
    node_colors = ['#636EFA' if state in distributor_states else '#00CC96' for state in all_states]
    color_mapping = {'WITHIN SAME STATE': 'rgba(0, 255, 0, 0.5)', 'OUTSIDE STATE': 'rgba(255, 0, 0, 0.5)'}
    flow_colors = [color_mapping.get(flag, 'rgba(0, 0, 0, 0.2)') for flag in df['flag']]

    # Create the Sankey chart
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=30,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_states,
            color=node_colors,
            x=x_coords,
            y=y_coords,
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            hovertemplate='<b>%{source.label} → %{target.label}</b><br>' +
                          'Percentage of Scans: %{value:.2f}%<extra></extra>',
            color=flow_colors
        )
    ))

    # Add legend traces
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color='rgba(0, 255, 0, 0.5)', line=dict(width=1, color='Black')),
        name='WITHIN SAME STATE',
    ))

    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color='rgba(255, 0, 0, 0.5)', line=dict(width=1, color='Black')),
        name='OUTSIDE STATE',
    ))

    # Update layout
    fig.update_layout(
        title_text="Sankey Diagram: Distributor State to Retailer State Distribution (Percentage)",
        title_font_size=20,
        font=dict(size=10),
        height=900,
        width=900,
        margin=dict(l=40, r=40, t=40, b=40),
        showlegend=True,
    )

    # Display the Sankey chart in Streamlit
    st.plotly_chart(fig)

else:
    st.write("Please upload a CSV file to generate the Sankey diagram.")
