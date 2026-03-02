# 7. Time Series Analysis (Trend Chart)
st.subheader("Crime Trends Over Time")

if 'date' in filtered_df.columns:
    try:
        # Convert date column to actual datetime objects
        filtered_df['date'] = pd.to_datetime(filtered_df['date'])
        
        # Group by date and count number of crimes
        # 'D' means daily. You can change to 'W' for weekly if it's too messy.
        crime_trend = filtered_df.resample('D', on='date').size().reset_index(name='Crime Count')
        
        # Display a Line Chart
        st.line_chart(data=crime_trend, x='date', y='Crime Count')
        
    except Exception as e:
        st.write("Could not generate trend chart. Ensure 'Date' column is formatted correctly.")
else:
    st.info("Date column not found. Add a 'Date' column to see trends over time.")

# 8. Category Breakdown (Bar Chart)
st.subheader("Crimes by Category")
category_counts = filtered_df[column_to_filter].value_counts()
st.bar_chart(category_counts)
