from data_fetcher import fetch_animal_data


def generate_animal_card(animal):
    """Generate an HTML card for an animal, omitting missing fields."""
    # Implementation of generate_animal_card function
    # This is a placeholder as the actual implementation is not provided in the issue description
    return "<div>Animal Card</div>"


def generate_webpage():
    """Generate the animals.html webpage using API data."""
    animal_name = input("Enter an animal name: ").strip()
    animals = fetch_animal_data(animal_name)

    if not animals:
        # Generate a message on the website instead of printing to CLI
        with open("animals_template.html", "r", encoding="utf-8") as template_file:
            template = template_file.read()
        
        error_message = "<div class='error-message'>No animals found.</div>"
        html_content = template.replace("{{ animals_content }}", error_message)
        
        with open("animals.html", "w", encoding="utf-8") as output_file:
            output_file.write(html_content)
        
        print("✅ animals.html generated with error message.")
        return

    cards = "".join(generate_animal_card(animal) for animal in animals)

    with open("animals_template.html", "r", encoding="utf-8") as template_file:
        template = template_file.read()

    html_content = template.replace("{{ animals_content }}", cards)

    with open("animals.html", "w", encoding="utf-8") as output_file:
        output_file.write(html_content)
    
    print("✅ animals.html generated successfully.")