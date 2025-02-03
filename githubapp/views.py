import requests
import matplotlib.pyplot as plt
import io
import urllib
import base64
from django.shortcuts import render

def github_user_search(request):
    user_data = None
    error_message = None
    graph_url = None

    if request.method == "POST":
        username = request.POST.get("username")
        if username:
            url = f"https://api.github.com/users/{username}"
            response = requests.get(url)

            if response.status_code == 200:
                user_data = response.json()
                followers_url = user_data.get("followers_url", "")
                following_url = f"https://api.github.com/users/{username}/following"
                repos_url = user_data.get("repos_url", "")

                followers_response = requests.get(followers_url)
                following_response = requests.get(following_url)
                repos_response = requests.get(repos_url)

                user_data["followers"] = followers_response.json() if followers_response.status_code == 200 else []
                user_data["following"] = following_response.json() if following_response.status_code == 200 else []
                user_data["repos"] = repos_response.json()[:5] if repos_response.status_code == 200 else []

                # Create a progress bar graph
                graph_url = generate_progress_graph(user_data)

            else:
                error_message = "User not found or GitHub API rate limit exceeded."

    return render(request, "github_user_search.html", {"user_data": user_data, "error_message": error_message, "graph_url": graph_url})



def generate_progress_graph(user_data):
    """Generate a progress bar graph and return its URL"""
    labels = ['Repos', 'Followers', 'Following']

    # Ensure values are integers, not lists or sequences
    values = [
        user_data.get('public_repos', 0), 
        len(user_data.get('followers', [])),  # Count followers instead of passing a list
        len(user_data.get('following', []))   # Count following instead of passing a list
    ]

    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color=['blue', 'green', 'orange'])
    plt.xlabel('Metrics')
    plt.ylabel('Count')
    plt.title(f"GitHub Progress for {user_data.get('login', '')}")

    # Convert the plot to a PNG image
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    graph_url = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    plt.close()

    return f"data:image/png;base64,{graph_url}"
