from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats
from faicons import icon_svg

#update interval = 3 seconds
UPDATE_INTERVAL_SECS: int = 5

DEQUE_SIZE: int = 20

reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

@reactive.calc()
def reactive_calc_combined():
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)
    north_temp = round(random.uniform(-18, -16), 1)
    south_temp = round(random.uniform(-18, -16), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"northtemp":north_temp,"southtemp":south_temp, "timestamp":timestamp}

    # get the deque and append the new entry
    reactive_value_wrapper.get().append(new_dictionary_entry)

    # Get a snapshot of the current deque for any further processing
    deque_snapshot = reactive_value_wrapper.get()

    # For Display: Convert deque to DataFrame for display
    df = pd.DataFrame(deque_snapshot)

    # For Display: Get the latest dictionary entry
    latest_dictionary_entry = new_dictionary_entry

    # Return a tuple with everything we need
    # Every time we call this function, we'll get all these values
    return deque_snapshot, df, latest_dictionary_entry
    

ui.page_opts(title="PyShiny Express: Live Data Example", fillable=True)

with ui.sidebar(open="open"):

    ui.h2("Antarctic Explorer", class_="text-center")
    ui.p(
        "A demonstration of real-time temperature readings in Antarctica.",
        class_="text-center",
    )
    ui.hr()
    ui.h6("Links:")
    ui.a(
        "GitHub Source",
        href="https://github.com/cartertrumansmith/cintel-05-cintel",
        target="_blank",
    )
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")
    ui.a(
        "PyShiny Express",
        href="hhttps://shiny.posit.co/blog/posts/shiny-express/",
        target="_blank",
    )

# In Shiny Express, everything not in the sidebar is in the main panel

with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("sun"),
        theme="bg-gradient-blue-purple",
    ):

        "Current Antarctic Temperature"

        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['southtemp']} C"

        "warmer than usual"

    with ui.card(full_screen=True):
        ui.card_header("Current Date and Time")

        @render.text
        def warmer():
            """Compare temps and display wheter the arctic or antarctic is warmer"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            n_temp = latest_dictionary_entry['northtemp']
            s_temp = latest_dictionary_entry['southtemp']

            if n_temp > s_temp:
                return f"At {latest_dictionary_entry['timestamp']} it is warmer in the Arctic"
            elif n_temp < s_temp:
                return f"At {latest_dictionary_entry['timestamp']} it is warmer in Antarctica"
            else: 
                return f"At {latest_dictionary_entry['timestamp']} it is the same temperature in the Arctic and Antarctica"
            return f"{latest_dictionary_entry['timestamp']}"
        
    with ui.value_box(
        showcase=icon_svg("sun"),
        theme="bg-gradient-red-purple",
    ):

        "Current Arctic Temperature"

        @render.text
        def display_arctic_temp():
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['northtemp']} C"

        "warmer than usual"

#with ui.card(full_screen=True, min_height="40%"):
with ui.card(full_screen=True):
    ui.card_header("Most Recent Readings")

    @render.data_frame
    def display_df():
        """Get the latest reading and return a dataframe with current readings"""
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        pd.set_option('display.width', None)        # Use maximum width
        return render.DataGrid( df,width="100%")

with ui.card():
    ui.card_header("Chart with Current Trend")

    @render_plotly
    def display_plot():
        # Fetch from the reactive calc function
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

        # Ensure the DataFrame is not empty before plotting
        if not df.empty:
            # Convert the 'timestamp' column to datetime for better plotting
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # Create scatter plot for readings
            # pass in the df, the name of the x column, the name of the y column,
            # and more
        
            fig = px.scatter(df,
            x="timestamp",
            y="southtemp",                
            title="Temperature Readings with Regression Line",
            labels={"temp": "Temperature (°C)", "timestamp": "Time"} )

            fig.add_scatter(x=df["timestamp"], y=df['northtemp'], mode='lines', name='Arctic Temperature')
            fig.add_scatter(x=df["timestamp"], y=df['southtemp'], mode='lines', name='Antarctic Temperature')
            
            sequence = range(len(df))
            x_vals = list(sequence)
            #y_vals = df["southtemp"]
