import google.generativeai as genai
from kivy.app import App
import os


def main():
    days = input("How many days are you meal prepping for? ")
    budget = input("What is your budget? ")
    add_info = input("""Any other notes? (i.e. "I'm gluten-free", "I want to prioritize protein.") """)
    meals = "breakfast and lunch"

    prompt = "Meal prep for me for " + days + " days, with a budget of " + budget + ". Include an itemized grocery list first, " \
        + "and then the total cost, and then meals for " + meals + " for each day. " + add_info + " Do not include anything else."
    print(prompt)

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    print(response.text)

if __name__ == '__main__':
    main()