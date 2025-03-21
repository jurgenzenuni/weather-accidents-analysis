# Overview 
This project aims to analyze the relationship between weather conditions and traffic accidents in New York City over a period of four years (2013-2024). The goal is to identify whether specific weather conditions—such as temperature, precipitation, and other meteorological factors—have a measurable impact on the frequency and severity of traffic accidents.

# Data
[https://catalog.data.gov/dataset/motor-vehicle-collisions-crashes](https://open-meteo.com/en/docs)
[https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/explore/query/SELECT%0A%20%20%60crash_date%60%2C%0A%20%20%60crash_time%60%2C%0A%20%20%60borough%60%2C%0A%20%20%60zip_code%60%2C%0A%20%20%60latitude%60%2C%0A%20%20%60longitude%60%2C%0A%20%20%60location%60%2C%0A%20%20%60on_street_name%60%2C%0A%20%20%60off_street_name%60%2C%0A%20%20%60cross_street_name%60%2C%0A%20%20%60number_of_persons_injured%60%2C%0A%20%20%60number_of_persons_killed%60%2C%0A%20%20%60number_of_pedestrians_injured%60%2C%0A%20%20%60number_of_pedestrians_killed%60%2C%0A%20%20%60number_of_cyclist_injured%60%2C%0A%20%20%60number_of_cyclist_killed%60%2C%0A%20%20%60number_of_motorist_injured%60%2C%0A%20%20%60number_of_motorist_killed%60%2C%0A%20%20%60contributing_factor_vehicle_1%60%2C%0A%20%20%60contributing_factor_vehicle_2%60%2C%0A%20%20%60contributing_factor_vehicle_3%60%2C%0A%20%20%60contributing_factor_vehicle_4%60%2C%0A%20%20%60contributing_factor_vehicle_5%60%2C%0A%20%20%60collision_id%60%2C%0A%20%20%60vehicle_type_code1%60%2C%0A%20%20%60vehicle_type_code2%60%2C%0A%20%20%60vehicle_type_code_3%60%2C%0A%20%20%60vehicle_type_code_4%60%2C%0A%20%20%60vehicle_type_code_5%60/page/filter](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data)
# Key Objectives:

Data Collection and Processing:

- Weather Data: Historical weather data, including average temperature, rainfall, and other relevant meteorological conditions, was collected for NYC from 2019 to 2022.
- Accident Data: Traffic accident data, including the number of accidents per day and their associated severity, was obtained from official NYC traffic accident databases.

Data Analysis:

- The weather data was aggregated monthly to calculate average temperatures and other key weather metrics.
- Traffic accident data was grouped by month to track trends in the number of accidents.
Both datasets were merged based on the corresponding months to compare the changes in weather conditions with accident occurrences.

Visualizations:
![dashboardss](https://github.com/user-attachments/assets/512b9f92-619c-4fb4-b347-dc5e2f43de73)
![totalsbyear](https://github.com/user-attachments/assets/b461c2ca-b122-436a-b37e-07844c0238cc)
![monthlyaccsbyweather](https://github.com/user-attachments/assets/42c71d7e-0b74-426d-878a-60f2212676ab)
![heatmap](https://github.com/user-attachments/assets/154da33d-5d73-428d-b188-c77f09bdb00d)

Findings:

- Preliminary observations aim to identify whether higher temperatures or more severe weather conditions correlate with an increase or decrease in accidents.
By analyzing trends over the four years, the study investigates whether weather patterns show consistent patterns in influencing accidents or if other factors (e.g., traffic volume, holidays, special events) may also play a role.
