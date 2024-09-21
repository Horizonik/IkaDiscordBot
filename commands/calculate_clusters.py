from itertools import product
from utils.types import BaseCommand, CityInfo, ClusterInfo
from utils.utils import (
    fetch_data,
    convert_data_to_markdown,
    filter_data_by_min_amount_of_cities_on_island,
    count_cities_per_island, get_islands_info
)


class CalculateClusters(BaseCommand):

    def __init__(self, command_initiator_name: str, command_name: str, params: dict):
        super().__init__(command_initiator_name, command_name)
        self.command_params = params

    def command_logic(self):
        cities_data = fetch_data(self.command_params['alliance_name'])

        city_counts = count_cities_per_island(cities_data)
        filtered_cities_data = filter_data_by_min_amount_of_cities_on_island(
            cities_data,
            city_counts,
            self.command_params['min_cities_on_island']
        )

        city_clusters = self.cluster_cities(filtered_cities_data, city_counts)
        clusters_info = self.create_clusters_info_objects(city_clusters, city_counts)

        return convert_data_to_markdown(clusters_info)

    def cluster_cities(self, cities_data: list[CityInfo], city_counts: dict) -> list:
        """Uses a DFS algorithm to determine which adjacent islands have the most cities total and saves them as a group (cluster)"""
        # TODO Note to self, might have an issue here due to no longer using a set on the city coords (same coords can get processed)
        max_islands_distance = self.command_params['max_distance']  # Max distance for clustering
        visited = set()
        clusters = []

        # Helper function for depth-first search
        def depth_first_search(city: CityInfo, cluster: list):
            stack = [city.coords]
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                cluster.append(city)

                # Only check relevant neighbors within the given distance
                for dx, dy in product(range(-max_islands_distance, max_islands_distance + 1), repeat=2):
                    if dx == 0 and dy == 0:
                        continue

                    neighbor = (current[0] + dx, current[1] + dy)
                    if abs(dx) <= max_islands_distance and abs(dy) <= max_islands_distance:
                        for city in cities_data:
                            if city.coords == neighbor and neighbor not in visited:
                                stack.append(neighbor)
                                break  # No need to check further if found

        # Start clustering cities
        for city in cities_data:
            if city.coords not in visited:
                cluster = []
                depth_first_search(city, cluster)
                clusters.append(cluster)

        return self.filter_clusters_by_min_city_count(clusters, city_counts)

    def filter_clusters_by_min_city_count(self, city_clusters: list, city_counts: dict) -> list:
        filtered_clusters = []
        for cluster in city_clusters:
            if any(city_counts.get(city.coords, 0) >= self.command_params['min_cities_per_cluster'] for city in
                   cluster):
                filtered_clusters.append(cluster)

        return filtered_clusters

    def create_clusters_info_objects(self, city_clusters: list, city_counts: dict) -> list[ClusterInfo]:
        clusters_info = []
        for cluster in city_clusters:
            total_cities = sum(city_counts.get(city.coords, 0) for city in cluster)

            if total_cities >= self.command_params['min_cities_per_cluster']:
                cluster_name = f"City Cluster {len(clusters_info) + 1}"
                islands = get_islands_info(cluster)
                clusters_info.append(ClusterInfo(
                    name=cluster_name,
                    rating=total_cities,
                    cities=cluster,
                    islands=islands
                ))

        return clusters_info
