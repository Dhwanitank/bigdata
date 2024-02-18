import requests
import json
import redis
import matplotlib.pyplot as plt

class TVMazeAPI:
    """Class to interact with the TVMaze API."""

    def __init__(self):
        self.url = "https://api.tvmaze.com/shows"

    def fetch_data(self):
        """Fetch data from the TVMaze API."""
        response = requests.get(self.url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to fetch data from API")
            return None

class RedisClient:
    """Class to interact with Redis."""

    def __init__(self):
        self.redis_host = 'redis-10376.c326.us-east-1-3.ec2.cloud.redislabs.com'
        self.redis_port = 10376
        self.redis_password = 'NVpOQbtzT2P5wZrcW5NhqY383UQzFlEr'
        self.redis_db = 0
        self.redis_client = redis.Redis(host=self.redis_host, port=self.redis_port, password=self.redis_password, db=self.redis_db)

    def insert_data(self, data):
        """Insert JSON data into Redis."""
        for item in data:
            self.redis_client.set(item['id'], json.dumps(item))

class TVShowAnalyzer:
    """Class to analyze TV show data."""

    def generate_bar_chart(self, data):
        """Generate bar chart for top 10 shows by average rating."""
        # Sort the data based on ratings
        sorted_data = sorted(data, key=lambda x: x['rating']['average'] if x['rating']['average'] is not None else 0, reverse=True)

        # Extract data for top 10 shows
        top_10_data = sorted_data[:10]

        # Extract relevant data for the chart
        show_names = [show['name'] for show in top_10_data]
        ratings = [show['rating']['average'] if show['rating']['average'] is not None else 0 for show in top_10_data]

        # Create the bar chart
        plt.figure(figsize=(10, 6))
        plt.barh(show_names, ratings, color='skyblue')
        plt.xlabel('Average Rating')
        plt.ylabel('TV Show')
        plt.title('Top 10 TV Shows by Average Rating')
        plt.gca().invert_yaxis()  # Invert y-axis to have highest ratings at the top
        plt.tight_layout()

        # Save the chart as an image or display it
        plt.savefig('top_10_bar_chart.png')

    def perform_aggregation(self, data):
        """Perform aggregation on TV show data."""
        total_shows = len(data)
        total_ratings = sum(show['rating']['average'] if show['rating']['average'] is not None else 0 for show in data)
        average_rating = total_ratings / total_shows if total_shows > 0 else 0
        return total_shows, average_rating

    def search_by_title(self, title, data):
        """Search for TV shows by title."""
        matching_shows = [show for show in data if title.lower() in show['name'].lower()]
        return matching_shows

def main():
    """Main function to run the TV show analysis."""
    api = TVMazeAPI()
    data = api.fetch_data()

    if data:
        redis_client = RedisClient()
        redis_client.insert_data(data)
        print("Data inserted into Redis successfully.")

        analyzer = TVShowAnalyzer()

        total_shows, average_rating = analyzer.perform_aggregation(data)
        print("Total number of shows:", total_shows)
        print("Average rating of all shows:", average_rating)

        analyzer.generate_bar_chart(data)
        print("Bar chart generated successfully.")

        search_term = input("Enter the title to search for: ")
        matching_shows = analyzer.search_by_title(search_term, data)
        if matching_shows:
            print("Matching shows found:")
            for show in matching_shows:
                print(show['name'])
        else:
            print("No matching shows found.")
    else:
        print("Failed to fetch data from API.")

if __name__ == "__main__":
    main()
