import google.generativeai as genai
import os
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.lang import Builder

Builder.load_string('''
<ScrollLabel>:
    Label:
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        text: root.text
''')

class ScrollLabel(ScrollView):
    text = StringProperty('')

class MealBuddy(App):
    def build(self):

        ## -- INITIALIZATION -- ##

        # Variables
        self.days = "3"
        self.meals = "lunch and dinner"
        self.budget = "30"
        self.add_info = ""
        self.change = "none"

        # Gemini API Setup
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        self.chat = model.start_chat()


        ## -- KIVY LAYOUT -- ##

        # Root Layout
        layout = BoxLayout(orientation='vertical')

        # Title Row
        title = Label(text="Let's Meal Prep!", font_size=50, bold=True, size_hint_y=0.5)
        layout.add_widget(title)

        # Input Settings Row
        full_settings_layout = BoxLayout(orientation='horizontal', size_hint_y=1)
        settings_layout = BoxLayout(orientation='vertical')

        days_layout = BoxLayout(orientation='horizontal')
        days_label = Label(text="# of Days: ", size_hint_x=1)
        days_in = TextInput(text="(e.g. 3)", size_hint_x=3)
        days_blank = Label(size_hint_x=0.5)
        days_layout.add_widget(days_label)
        days_layout.add_widget(days_in)
        days_layout.add_widget(days_blank)
        settings_layout.add_widget(days_layout)

        meals_layout = BoxLayout(orientation='horizontal')
        meals_label = Label(text="Meals: ", size_hint_x=1)
        meals_in = TextInput(text="(e.g. lunch and dinner)", size_hint_x=3)
        meals_blank = Label(size_hint_x=0.5)
        meals_layout.add_widget(meals_label)
        meals_layout.add_widget(meals_in)
        meals_layout.add_widget(meals_blank)
        settings_layout.add_widget(meals_layout)

        budget_layout = BoxLayout(orientation='horizontal')
        budget_label = Label(text="Budget: $", size_hint_x=1)
        budget_in = TextInput(text="(e.g. 30)", size_hint_x=3)
        budget_blank = Label(size_hint_x=0.5)
        budget_layout.add_widget(budget_label)
        budget_layout.add_widget(budget_in)
        budget_layout.add_widget(budget_blank)
        settings_layout.add_widget(budget_layout)
        full_settings_layout.add_widget(settings_layout)

        add_layout = BoxLayout(orientation='vertical')
        add_label = Label(text="Additional Information: ", size_hint_y=1)
        add_in = TextInput(text="""(e.g. "I'm gluten-free.", "I want to emphasize protein.")""", \
                                size_hint_y=4)
        add_layout.add_widget(add_label)
        add_layout.add_widget(add_in)
        full_settings_layout.add_widget(add_layout)

        layout.add_widget(full_settings_layout)

        # Generate Row
        generate_button = Button(text="Generate", size_hint_y=0.5)
        layout.add_widget(generate_button)

        # Output Row
        output_layout = BoxLayout(orientation='horizontal', size_hint_y=5) 
        meals_out = ScrollLabel(text="\n\n\n        Meals: ...")
        output_layout.add_widget(meals_out)
        grocer_out = ScrollLabel(text="\n\n\n        Groceries: ...")
        output_layout.add_widget(grocer_out)
        layout.add_widget(output_layout)

        # Change Row
        change_layout = BoxLayout(orientation='horizontal', size_hint_y=0.5) 
        change_label = Label(text="Any Changes?", size_hint_x=1)
        change_layout.add_widget(change_label)
        change_in = TextInput(text="""(e.g. "Change day 2's meals.", "Change my budget to $25.")""", size_hint_x=2)
        change_layout.add_widget(change_in)
        change_submit = Button(text="Change", size_hint_x=1)
        change_layout.add_widget(change_submit)
        layout.add_widget(change_layout)


        ## -- FUNCTIONS -- ##

        # Update Variables
        def upd_days(instance,value):
            self.days=value
        days_in.bind(text=upd_days)

        def upd_meals(instance,value):
            self.meals=value
        meals_in.bind(text=upd_meals)

        def upd_budget(instance,value):
            self.budget=value
        budget_in.bind(text=upd_budget)

        def upd_add_info(instance,value):
            self.add_info=value
        add_in.bind(text=upd_add_info)

        def upd_change(instance,value):
            self.change=value
        change_in.bind(text=upd_change)

        # Generate meals and groceries with Gemini 
        def generate(instance):
            model = genai.GenerativeModel("gemini-1.5-flash")
            self.chat = model.start_chat()
            prompt = "Meal prep for me for " + self.days + " days, with a budget of " + self.budget + \
                ". Include an itemized grocery list first called 'Grocery List', " + \
                "and then the total cost, and then list the meals under 'Meal Plan' for " + \
                self.meals + " for each day. " + self.add_info + " Do not include anything else."
            response = self.chat.send_message(prompt)
            try:
                grocer_start = response.text.index('## Grocery List')
                grocer_end = response.text.index('## Meal Plan')
                meals_out.text=response.text[grocer_end:-1]
                grocer_out.text=response.text[grocer_start:grocer_end]
            except:
                meals_out.text="There was an issue. Re-generate."
                grocer_out.text="There was an issue. Re-generate."
                print(response.text)
        generate_button.bind(on_release=generate)

        def change(instance):
            if self.change != "none" and self.change != "":
                response = self.chat.send_message(self.change)
                try:
                    grocer_start = response.text.index('## Grocery List')
                    grocer_end = response.text.index('## Meal Plan')
                    meals_out.text=response.text[grocer_end:-1]
                    grocer_out.text=response.text[grocer_start:grocer_end]
                except:
                    meals_out.text="There was an issue. Re-generate."
                    grocer_out.text="There was an issue. Re-generate."
                    print(response.text)
        change_submit.bind(on_release=change)

        return layout

if __name__ == "__main__":
    MealBuddy().run()