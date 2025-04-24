# Store Monitoring Task 

For debugging, download this ZIP file which contains all the CSV data files. The CSV files are too large to push to GitHub, so they are provided in this ZIP archive: [Download Link](https://drive.google.com/file/d/15MdirrFn8al-Po-DIsKbGg2pyoipkjqi/view?usp=drive_link)

## Features

- Imports and stores raw CSV data into a database (`store_status`, `menu_hours`, `timezones`)
- Triggers report generation asynchronously with `/trigger_report`
- Polls report status with `/get_report`
- Downloads generated report CSV via `/download/{report_id}`
- Calculates uptime and downtime based on:
  - Business hours
  - Timezone
  - Smart interpolation between status pings

## How It Works

1. **Load Data**: Run `load_data.py` to insert CSV files into the database.
2. **Trigger Report**: Call `/trigger_report` to start report generation in the background.
3. **Check Status**: Poll `/get_report?report_id=...` until it returns `"Complete"`.
4. **Download CSV**: Access `/download/{report_id}` to get the final report.

## Sample Output

[Download CSV Report](https://github.com/andoriyaprashant/prashant_24april/tree/main/store_monitoring/reports)

## Ideas for Improvement

- Add authentication for the endpoints
- Store report status in the database instead of memory
- Add pagination and filtering support for large datasets
- Add automatic refresh of reports on data update

## Demo Video

[Click to Watch Demo](https://drive.google.com/file/d/1YfjYtNFhDgJsiO0phbVVjsKscaiByE0P/view?usp=drive_link)  
