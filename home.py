import streamlit as st
import pandas as pd
from data_processing import load_data, get_districts_for_state
from prediction import predict_yield, load_model
from maps import create_india_map
from styling import custom_css, custom_footer
from genrate_charts import generate_single_charts, generate_comparison_charts
import os
from state_coords import state_coords

@st.cache_data
def memoized_load_data(file_path):
    return load_data(file_path)

# Use the new resource caching API for model loading
@st.cache_resource
def memoized_load_model():
    return load_model()

def main():
    st.markdown(custom_css(), unsafe_allow_html=True)

    # Create tabs before the title to move them to the top
    tabs = st.tabs(["Crop Yields Prediction", "Distribution Across India", "Analysis & Comparison"])

    # Define the path to your dataset
    package_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(package_dir, 'CompleteDataset.csv')

    # Use the memoized functions to load data and model
    data = memoized_load_data(file_path)
    model = memoized_load_model()
    states_list = list(sorted(data['State'].unique()))

    # Create tabs
    with tabs[0]:
        st.header('Welcome to the Crop Yields Prediction app!')
        # Place the content of "Crop Yields Prediction" inside this block
        state = st.selectbox('Select State', [''] + states_list)
        if state:
            districts = get_districts_for_state(data, state)
            district = st.selectbox('Select District', [''] + districts)
        else:
            district = ''

        year = st.number_input('Enter Year', min_value=2018, max_value=2021, step=1)
        season = st.selectbox('Select Season', ['Autumn', 'Kharif', 'Rabi', 'Summer', 'Whole Year', 'Winter'])
        area = st.number_input('Enter Area (Hectare)', min_value=0.0)
        production = st.number_input('Enter Production (Tonnes)', min_value=0.0)

        if st.button('Predict Yield'):
            if not state or not district or not year or not season or not area or not production:
                st.warning('Please fill in all the fields')
            else:
                model = load_model()
                predicted_yield = predict_yield(model, data, state, district, year, season, area, production)
                st.success(f'Predicted yield for {state}, {district} in {year} ({season}): {predicted_yield}')


    with tabs[1]:
        st.header('Explore Crop Yield Distribution Across India')
        # Place the content of "Distribution Across India" inside this block
        crop_options = ['Maize', 'Rice', 'Green Gram', 'Urad', 'Sesamum', 'Groundnut', 'Onion', 'Pigeon Pea',
                        'Potato',
                        'Gram', 'Wheat', 'Rapeseed & Mustard', 'Jowar', 'Sugarcane', 'Bajra']
        crop = st.selectbox('Select Crop:', crop_options)
        year = st.number_input('Enter Year', min_value=2018, max_value=2021, step=1, value=2020)

        if st.button('Show Map'):
            st.write(f"Showing crop yield information for {crop} in {year}")
            map_html = create_india_map(data, crop, year)._repr_html_()
            with st.container():
                st.components.v1.html(map_html, width=None, height=500)

    # st.markdown(custom_footer(), unsafe_allow_html=True)
    with tabs[2]:
        st.header('Analyze the Time-Series Trends over the Years')
        st.subheader('Single Crop Analysis')

        package_dir2 = os.path.dirname(os.path.abspath(__file__))
        file_path2 = os.path.join(package_dir2, 'FinalDataSet(2005-2021).csv')

        # Use the memoized functions to load data and model
        new_data = memoized_load_data(file_path2)
        crop_options = list(new_data.Crop.unique())
        crop = st.selectbox('Select Crop:', crop_options)

        line_chart, area_chart, bar_chart = generate_single_charts(new_data, crop)
        tab1, tab2, tab3 = st.tabs(["Line Chart", "Area Chart", "Bar Chart"])

        with tab1:
            st.plotly_chart(line_chart, theme="streamlit", use_container_width=True)

        with tab2:
            st.plotly_chart(area_chart, theme="streamlit", use_container_width=True)

        with tab3:
            st.plotly_chart(bar_chart, theme="streamlit", use_container_width=True)

        st.subheader('Compare Different Crops')
        selected_crops = st.multiselect('Select Crops:', crop_options, default=['Wheat'])
        line_chart, stacked_area_chart, group_bar_chart = generate_comparison_charts(new_data, selected_crops)
        tab4, tab5, tab6 = st.tabs(["Line Chart", "Area Chart", "Bar Chart"])

        with tab4:
            st.plotly_chart(line_chart, theme="streamlit", use_container_width=True)

        with tab5:
            st.plotly_chart(stacked_area_chart, theme="streamlit", use_container_width=True)

        with tab6:
            st.plotly_chart(group_bar_chart, theme="streamlit", use_container_width=True)

if __name__ == "__main__":
    main()
