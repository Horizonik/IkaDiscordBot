from itertools import product

from embeds.embeds import calculate_clusters_embed
from utils.data_utils import fetch_data
from utils.general_utils import count_cities_per_island, generate_cluster_name
from utils.types import BaseCommand, CityData


class CalculateClusters(BaseCommand):

    async def command_logic(self):
        cities_data = fetch_data(f"server={self.region_id}&world={self.world_id}&state=active&search=ally&allies[1]={self.command_params['alliance_name']}")
        if not cities_data:
            raise ValueError(f"alliance '{self.command_params['alliance_name']}' doesn't exist or has no data!")

        city_counts = count_cities_per_island(cities_data)
        filtered_cities_data = self.filter_data_by_min_amount_of_cities_on_island(cities_data, city_counts)
        city_clusters = self.cluster_cities(filtered_cities_data)

        await self.ctx.response.send_message(embed=calculate_clusters_embed(
            self.clusters_to_str(city_clusters, city_counts),
            self.command_params['alliance_name']
        ))

    def clusters_to_str(self, clusters: list[list[CityData]], city_counts: dict) -> list[str]:
        formatted_clusters = []
        cluster_index = 1

        for cluster in clusters:
            cluster_name = f"{generate_cluster_name()} [Cluster {chr(65 + cluster_index - 1)}]"
            total_cities = sum(city_counts.get(city.coords, 0) for city in cluster)

            if total_cities < self.command_params['min_cities_per_cluster']:
                continue

            cluster_str = [f"{cluster_name} - total of {total_cities}"]
            for city in cluster:
                count = city_counts.get(city.coords, 0)
                cluster_str.append(f"- {city.x}:{city.y} -> {count} cities")

            formatted_clusters.append("\n".join(cluster_str))
            cluster_index += 1

        return formatted_clusters

    def cluster_cities(self, cities_data: list[CityData]) -> list[list[CityData]]:
        coord_set = set(city.coords for city in cities_data)
        visited = set()
        clusters = []

        # Helper function for depth-first search
        def depth_first_search(city: CityData, cluster: list):
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

    def filter_data_by_min_amount_of_cities_on_island(self, cities_data: list[CityData], city_counts: dict) -> list:
        return [city for city in cities_data if
                city_counts[city.coords] >= self.command_params['min_cities_per_island']]
