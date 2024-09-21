# import discord
# import plotly.express as px
# import pandas as pd
# import numpy as np
#
# from utils.types import BaseCommand, CityInfo
# from utils.utils import fetch_data, filter_data_by_min_amount_of_cities_on_island, count_cities_per_island
#
#
# class GenerateHeatmap(BaseCommand):
#
#     def __init__(self, ctx: discord.Interaction, params: dict):
#         super().__init__(ctx, params)
#         self.command_params = params
#
#     def command_logic(self):
#         cities_data = fetch_data(f"state=active&search=ally&allies[1]={self.command_params['alliance_name']}")
#         city_counts = count_cities_per_island(cities_data)
#
#         filtered_cities_data = filter_data_by_min_amount_of_cities_on_island(
#             cities_data, city_counts,
#             self.command_params['min_cities_on_island']
#         )
#
#         self.create_interactive_heatmap(filtered_cities_data)
#
#     def create_interactive_heatmap(self, cities_data: list[CityInfo]):
#         if not cities_data:
#             raise ValueError("No coordinate data found.")
#
#         # Create a 100x100 heatmap grid
#         grid_size = 100
#         island_heatmap = np.zeros((grid_size, grid_size))
#
#         # Set fixed grid bounds (1:1 to 100:100)
#         min_x, max_x = 1, 100
#         min_y, max_y = 1, 100
#
#         # Populate the heatmap with coordinates, using coords from CityInfo objects
#         for city in cities_data:
#             x, y = city.coords
#             if min_x <= x <= max_x and min_y <= y <= max_y:
#                 island_heatmap[y - min_y, x - min_x] += 1
#
#         # Create a DataFrame for Plotly with the fixed coordinates
#         df = pd.DataFrame(
#             island_heatmap,
#             index=[f'{y + min_y}' for y in range(grid_size)],
#             columns=[f'{x + min_x}' for x in range(grid_size)]
#         )
#
#         # Melt the DataFrame to long format for Plotly
#         df_melted = df.reset_index().melt(
#             id_vars='index',
#             var_name='X',
#             value_name=f'{self.command_params["alliance_name"]} Cities'
#         )
#
#         df_melted.rename(columns={'index': 'Y'}, inplace=True)
#
#         # Create heatmap
#         fig = px.density_heatmap(
#             df_melted,
#             x='X',
#             y='Y',
#             z=f'{self.command_params["alliance_name"]} Cities',
#             color_continuous_scale='YlOrRd',
#             text_auto=True
#         )
#
#         # Update layout
#         fig.update_layout(
#             title=f"{self.command_params['alliance_name']} Alliance City Distribution Heatmap",
#             xaxis_title="X Coordinate",
#             yaxis_title="Y Coordinate",
#             xaxis=dict(scaleanchor="y", range=[1, 100]),  # Force x-axis range from 1 to 100
#             yaxis=dict(constrain='domain', range=[1, 100]),  # Force y-axis range from 1 to 100
#             coloraxis_colorbar=dict(title=f'Amount of cities')
#         )
#
#         fig.update_traces(
#             texttemplate='%{text}',  # Display text in cells
#             textfont_size=10  # Adjust text size
#         )
#
#         fig.show()
