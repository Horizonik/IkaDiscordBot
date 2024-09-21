from itertools import product

import discord

from utils.types import BaseCommand, CityInfo, ClusterInfo
from utils.utils import (
    fetch_data,
    count_cities_per_island,
    convert_data_to_embed, generate_cluster_name
)


class CalculateClusters(BaseCommand):

    def __init__(self, ctx: discord.Interaction, params: dict):
        super().__init__(ctx, params)
        self.command_params = params

    async def command_logic(self):
        cities_data = fetch_data(f"state=active&search=ally&allies[1]={self.command_params['alliance_name']}")

        city_counts = count_cities_per_island(cities_data)
        filtered_cities_data = self.filter_data_by_min_amount_of_cities_on_island(
            cities_data,
            city_counts
        )

        city_clusters = self.cluster_cities(filtered_cities_data)
        clusters_as_objects = self.convert_raw_clusters_to_objects(city_clusters, city_counts)

        # Create the embed message instead of markdown
        embed = convert_data_to_embed(clusters_as_objects)
        await self.ctx.response.send_message(embed=embed)

    def cluster_cities(self, cities_data: list[CityInfo]) -> list[list[CityInfo]]:
        coord_set = set(city.coords for city in cities_data)
        visited = set()
        clusters = []

        # Helper function for depth-first search
        def depth_first_search(city: CityInfo, cluster: list):
            stack = [city]
            while stack:
                current_city = stack.pop()
                if current_city.coords in visited:
                    continue
                visited.add(current_city.coords)
                cluster.append(current_city)

                # Only check relevant neighbors within the given distance
                for dx, dy in product(range(-self.command_params['max_cluster_distance'],
                                            self.command_params['max_cluster_distance'] + 1), repeat=2):
                    if dx == 0 and dy == 0:
                        continue

                    neighbor_coords = (current_city.coords[0] + dx, current_city.coords[1] + dy)
                    if neighbor_coords in coord_set and neighbor_coords not in visited:
                        for neighbor in cities_data:
                            if neighbor.coords == neighbor_coords:
                                stack.append(neighbor)
                                break  # Stop searching once we found the first matching neighbor

        # Start clustering cities
        for city in cities_data:
            if city.coords not in visited:
                cluster = []
                depth_first_search(city, cluster)
                if cluster:  # Only add non-empty clusters
                    clusters.append(cluster)

        return clusters

    def filter_data_by_min_amount_of_cities_on_island(self, cities_data: list[CityInfo], city_counts: dict) -> list:
        return [city for city in cities_data if
                city_counts[city.coords] >= self.command_params['min_cities_per_island']]

    def filter_clusters_by_city_count(self, clusters: list, city_counts: dict) -> list:
        filtered_clusters = []
        for cluster in clusters:
            if any(city_counts.get(city.coords, 0) >= self.command_params['min_cities_per_cluster'] for city in
                   cluster):
                filtered_clusters.append(cluster)
        return filtered_clusters

    def convert_raw_clusters_to_objects(self, clusters: list[list[CityInfo]], city_counts: dict) -> list[ClusterInfo]:
        cluster_infos = []
        cluster_index = 1

        for cluster_cities in clusters:
            cluster_name = f"{generate_cluster_name()} [#{chr(65 + cluster_index - 1)}]"
            total_cities = sum(city_counts.get(city.coords, 0) for city in cluster_cities)

            if total_cities < self.command_params['min_cities_per_cluster']:
                continue

            cluster_infos.append(ClusterInfo(cluster_name, -1, cluster_cities))
            cluster_index += 1

        return cluster_infos
