import json

def count_articles(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Get the number of articles
    articles_count = len(data.get("articles", []))
    return articles_count

# Example usage
file_path = "output.json"  # Replace with your actual file path
number_of_articles = count_articles(file_path)
print(f"Number of articles: {number_of_articles}")

def count_div_tags(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()

    # Count the number of <div> tags
    div_count = content.count("<div>")
    return div_count

# Example usage
file_path = "cleaned_content.txt"  # Replace with the actual path if needed
div_count = count_div_tags(file_path)
print(f"Number of <div> tags: {div_count}")