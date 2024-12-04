from slack_bolt import App
import logging
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
from shapely.geometry import Point
import dabbas as db
import requests
import tempfile

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a logger instance
logger = logging.getLogger(__name__)

# Example usage of logger
logger.info("This is an info message.")
logger.error("This is an error message.")
logger.setLevel(logging.INFO)  # Only capture INFO, WARNING, ERROR, CRITICAL messages

load_dotenv(dotenv_path=r'C:\Users\HP\Desktop\Riya\slack_bot\.env')

# Initialize Slack app
app = App(token=os.getenv("SLACK-BOT-TOKEN"))

TARGET_CHANNEL_ID = "C081N0N0U4S"  # The channel where the file will be uploaded

# Database connection string
connection_string = os.getenv("DB_CONNECTION_STRING")
print(f"Connection String: {connection_string}")  # Debug print

engine = create_engine(connection_string)

# Google Maps API key
api_key = os.getenv("GOOGLE_API_KEY")

@app.command("/upload")
def upload_callback(ack, body, client, logger):
    """
    Responds to the /upload command by providing file upload instructions.
    """
    ack()  # Acknowledge the slash command

    user_id = body["user_id"]  # Accessing user_id from the body of the slash command

    try:
        # Send an ephemeral message to the user, directing them to upload their file to the 'toll' channel
        client.chat_postEphemeral(
            channel=user_id,  # The channel is the user's DM
            user=user_id,  # The user receiving the message
            text=f"Hi <@{user_id}>, please upload your file containing the toll data to the channel <#C081N0N0U4S>."
        )

    except SlackApiError as e:
        logger.error(f"Error sending upload instructions: {e.response['error']}")

# Modify the file handling to listen to file uploads in the "toll" channel (C081N0N0U4S)
@app.event("file_shared")
def handle_file_submission(event, client, logger):
    """
    Handles file upload in the 'toll' channel (C081N0N0U4S).
    Downloads the file, processes it, and uploads the results to the database.
    """
    logger.info(f"File shared event: {event}")
    channel_id = event.get("channel_id")
    
    # Only process files shared in the 'toll' channel (C081N0N0U4S)
    if channel_id != TARGET_CHANNEL_ID:
        logger.info(f"Ignored file in channel {channel_id}")
        return  # Ignore files in other channels

    # Proceed with processing the file if it's in the correct channel
    file_id = event["file_id"]
    user_id = event["user_id"]

    try:
        # Fetch file details using Slack API
        file_info = client.files_info(file=file_id)
        logger.info(f"File info: {file_info}")  # Debug log
        file_name = file_info["file"]["name"]
        file_url = file_info["file"]["url_private_download"]

        if not (file_name.endswith(".xlsx") or file_name.endswith(".xls")):
            logger.error(f"File {file_name} is not an Excel file. Ignoring.")
            client.chat_postEphemeral(
                channel=user_id,
                user=user_id,  # Specify the user receiving the ephemeral message
                text="Sorry, only Excel files are supported."
            )
            return
        
        headers = {"Authorization": "Bearer xoxb-5560666307137-8050847874848-u1aDP4IGHXVYZ75hdTpKbKMk"}

        response = requests.get(file_url, headers=headers)
        logger.info(f"File download status: {response.status_code}")
        logger.info(f"File content type: {response.headers.get('Content-Type')}")

        if response.status_code == 200:
            logger.info(f"File content: {response.text[:500]}")  # Log part of the file content for debugging
            # Get a temporary directory
            temp_dir = tempfile.gettempdir()
            file_path = f"{temp_dir}/{file_name}"
            logger.info(f"File saved to: {file_path}")

            with open(file_path, "wb") as f:
                f.write(response.content)

            # Start processing the file
            processed_data = process_and_insert_to_db(file_path)

            # Notify success to the user via an ephemeral message in their app
            client.chat_postEphemeral(
                channel=user_id,  # Send ephemeral message to the user's DM
                user=user_id,  # Specify the user receiving the ephemeral message
                text=f"Hi <@{user_id}>, the file `{file_name}` has been processed successfully and the data has been uploaded to the database."
            )
        else:
            logger.error(f"Error: Received status code {response.status_code} when downloading the file.")
            raise Exception("File download failed.")

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        client.chat_postEphemeral(
            channel=user_id,  # Send ephemeral message to the user's DM
            user=user_id,  # Specify the user receiving the ephemeral message
            text="Sorry, there was an error processing your file."
        )



def process_and_insert_to_db(file_path):
    """
    Processes the Excel file and inserts the processed data into the database.
    """
    logger.info(f"Processing file: {file_path}")  
    # Load the uploaded file
    excel_dataframe = pd.read_excel(file_path, sheet_name=1, engine="openpyxl")
    excel_dataframe = excel_dataframe.drop_duplicates(subset='From-To ID')

    # Load the existing data from the database
    query = "SELECT * FROM toll_data_new"
    toll_data_new_df = pd.read_sql(query, engine)
    toll_data_new_df = toll_data_new_df.drop_duplicates(subset='From-To ID')

    # Create a set of "From-To ID" values from toll_data_new_df for comparison
    toll_data_ids = set(toll_data_new_df['From-To ID'])

    # Define the function to check if "From-To ID" from excel_dataframe exists in toll_data_new_df
    def check_from_to_id(row):
        if row['From-To ID'] in toll_data_ids:
            return "YES"
        else:
            return "NO"

    # Apply the function to create the 'remark' column
    excel_dataframe['remark'] = excel_dataframe.apply(check_from_to_id, axis=1)

    # Map 'From-To ID' to latitude and longitude from toll_data_new_df
    id_to_coords = toll_data_new_df.set_index('From-To ID')[['new_latitude', 'new_longitude']].to_dict(orient='index')
    for idx, row in excel_dataframe.iterrows():
        if row['remark'] == "YES" and row['From-To ID'] in id_to_coords:
            excel_dataframe.at[idx, 'new_latitude'] = id_to_coords[row['From-To ID']]['new_latitude']
            excel_dataframe.at[idx, 'new_longitude'] = id_to_coords[row['From-To ID']]['new_longitude']

    # Process rows with 'remark' == 'NO' using Google Maps Snap to Roads API
    excel_dataframe = process_dataframe(excel_dataframe, api_key)

    # Additional processing and calculations
    excel_dataframe['geometry'] = excel_dataframe.apply(lambda x: Point(x['new_longitude'], x['new_latitude']), axis=1)
    excel_dataframe = db.GeoDataFrame(excel_dataframe)
    excel_dataframe['dynamic_toll'] = excel_dataframe['POINT_ID'].apply(lambda x: True if x[:2] == 'CT' else False)
    excel_dataframe['numeric_part'] = excel_dataframe['POINT_ID'].str.extract(r'(\d+)')

    # Count frequency of numeric parts
    frequency = excel_dataframe['numeric_part'].value_counts()
    unique_numeric_parts = frequency[frequency == 1].index.tolist()
    excel_dataframe['single_toll'] = excel_dataframe['numeric_part'].isin(unique_numeric_parts)
    
    def split_from(x):
        if type(x)==str:
            split_list = x.split(',')
            if len(split_list)==2:
                return split_list[0][:7]
            else:
                None
        else:
            None

    # Handle entry and exit points
    excel_dataframe['entry_point'] = excel_dataframe.POINT_ID.apply(lambda x: True if x[-2:] == 'EN' else False)
    excel_dataframe['entry_id_for_exit'] = excel_dataframe['From-To ID'].apply(split_from)
    excel_dataframe['entry_point_id'] = excel_dataframe.POINT_ID.apply(lambda x: x[:7])


    columns_to_convert = ['2WVSJ', '2WVRJ', '2WVMP', 'CJVSJ', 'CJVRJ', 'CJVMP', 
                        'LCNSJ', 'LCVRJ', 'LCVMP', 'BTSJ', 'BTRJ', 'BTMP', 
                        '3AVSJ', '3AVRJ', '3AVMP', '4TO6ASJ', '4TO6ARJ', 
                        '4TO6AMJ', 'HCM_EME_SJ', 'HCM_EME_RJ', 'HCM_EME_MJ', 
                        '7AXLE_SJ', '7AXLE_RJ', '7AXLE_MJ']

    # Convert each column to numeric, coercing errors to NaN
    for col in columns_to_convert:
        excel_dataframe[col] = db.to_numeric(excel_dataframe[col], errors='coerce')

    excel_dataframe[['TOLL_NAME','2WVSJ','CJVSJ','LCNSJ','BTSJ','3AVSJ',
                '4TO6ASJ','7AXLE_SJ']] = excel_dataframe[[
        'TOLL_NAME','2WVSJ','CJVSJ','LCNSJ','BTSJ','3AVSJ','4TO6ASJ','7AXLE_SJ']].fillna(0)


    excel_dataframe.loc[excel_dataframe['LCNSJ'].isnull() | (excel_dataframe['LCNSJ']==0), 'LCNSJ'] = excel_dataframe['CJVSJ'][excel_dataframe['LCNSJ'].isnull() | (excel_dataframe['LCNSJ']==0)]
    excel_dataframe.loc[excel_dataframe['BTSJ'].isnull() | (excel_dataframe['BTSJ']==0), 'BTSJ'] = excel_dataframe['LCNSJ'][excel_dataframe['BTSJ'].isnull() | (excel_dataframe['BTSJ']==0)]
    excel_dataframe.loc[excel_dataframe['3AVSJ'].isnull() | (excel_dataframe['3AVSJ']==0), '3AVSJ'] = excel_dataframe['BTSJ'][excel_dataframe['3AVSJ'].isnull() | (excel_dataframe['3AVSJ']==0)]
    excel_dataframe.loc[excel_dataframe['4TO6ASJ'].isnull() | (excel_dataframe['4TO6ASJ']==0), '4TO6ASJ'] = excel_dataframe['3AVSJ'][excel_dataframe['4TO6ASJ'].isnull() | (excel_dataframe['4TO6ASJ']==0)]
    excel_dataframe.loc[excel_dataframe['HCM_EME_SJ'].isnull() | (excel_dataframe['HCM_EME_SJ']==0), 'HCM_EME_SJ'] = excel_dataframe['4TO6ASJ'][excel_dataframe['HCM_EME_SJ'].isnull() | (excel_dataframe['HCM_EME_SJ']==0)]
    excel_dataframe.loc[excel_dataframe['7AXLE_SJ'].isnull() | (excel_dataframe['7AXLE_SJ']==0), '7AXLE_SJ'] = excel_dataframe['4TO6ASJ'][excel_dataframe['7AXLE_SJ'].isnull() | (excel_dataframe['7AXLE_SJ']==0)]


    excel_dataframe.loc[excel_dataframe['2WVRJ'].isnull() | (excel_dataframe['2WVRJ'] == 0) |(excel_dataframe['2WVRJ'] <= excel_dataframe['2WVSJ']), '2WVRJ'] = 1.5 * excel_dataframe['2WVSJ'][excel_dataframe['2WVRJ'].isnull() | (excel_dataframe['2WVRJ'] == 0) |(excel_dataframe['2WVRJ'] <= excel_dataframe['2WVSJ'])]
    excel_dataframe.loc[excel_dataframe['CJVRJ'].isnull() | (excel_dataframe['CJVRJ'] == 0) |(excel_dataframe['CJVRJ'] <= excel_dataframe['CJVSJ']), 'CJVRJ'] = 1.5 * excel_dataframe['CJVSJ'][excel_dataframe['CJVRJ'].isnull() | (excel_dataframe['CJVRJ'] == 0)|(excel_dataframe['CJVRJ'] <= excel_dataframe['CJVSJ'])]
    excel_dataframe.loc[excel_dataframe['LCVRJ'].isnull() | (excel_dataframe['LCVRJ'] == 0) |(excel_dataframe['LCVRJ'] <= excel_dataframe['LCNSJ']), 'LCVRJ'] = 1.5 * excel_dataframe['LCNSJ'][excel_dataframe['LCVRJ'].isnull() | (excel_dataframe['LCVRJ'] == 0)|(excel_dataframe['LCVRJ'] <= excel_dataframe['LCNSJ'])]
    excel_dataframe.loc[excel_dataframe['BTRJ'].isnull() | (excel_dataframe['BTRJ'] == 0) |(excel_dataframe['BTRJ'] <= excel_dataframe['BTSJ']), 'BTRJ'] = 1.5 * excel_dataframe['BTSJ'][excel_dataframe['BTRJ'].isnull() | (excel_dataframe['BTRJ'] == 0)|(excel_dataframe['BTRJ'] <= excel_dataframe['BTSJ'])]
    excel_dataframe.loc[excel_dataframe['3AVRJ'].isnull() | (excel_dataframe['3AVRJ'] == 0) |(excel_dataframe['3AVRJ'] <= excel_dataframe['3AVSJ']), '3AVRJ'] = 1.5 * excel_dataframe['3AVSJ'][excel_dataframe['3AVRJ'].isnull() | (excel_dataframe['3AVRJ'] == 0)|(excel_dataframe['3AVRJ'] <= excel_dataframe['3AVSJ'])]
    excel_dataframe.loc[excel_dataframe['4TO6ARJ'].isnull() | (excel_dataframe['4TO6ARJ'] == 0) |(excel_dataframe['4TO6ARJ'] <= excel_dataframe['4TO6ASJ']), '4TO6ARJ'] = 1.5 * excel_dataframe['4TO6ASJ'][excel_dataframe['4TO6ARJ'].isnull() | (excel_dataframe['4TO6ARJ'] == 0)|(excel_dataframe['4TO6ARJ'] <= excel_dataframe['4TO6ASJ'])]
    excel_dataframe.loc[excel_dataframe['HCM_EME_RJ'].isnull() | (excel_dataframe['HCM_EME_RJ'] == 0) |(excel_dataframe['HCM_EME_RJ'] <= excel_dataframe['HCM_EME_SJ']), 'HCM_EME_RJ'] = 1.5 * excel_dataframe['HCM_EME_SJ'][excel_dataframe['HCM_EME_RJ'].isnull() | (excel_dataframe['HCM_EME_RJ'] == 0)|(excel_dataframe['HCM_EME_RJ'] <= excel_dataframe['HCM_EME_SJ'])]
    excel_dataframe.loc[excel_dataframe['7AXLE_RJ'].isnull() | (excel_dataframe['7AXLE_RJ'] == 0) |(excel_dataframe['7AXLE_RJ'] <= excel_dataframe['7AXLE_SJ']), '7AXLE_RJ'] = 1.5 * excel_dataframe['7AXLE_SJ'][excel_dataframe['7AXLE_RJ'].isnull() | (excel_dataframe['7AXLE_RJ'] == 0)|(excel_dataframe['7AXLE_RJ'] <= excel_dataframe['7AXLE_SJ'])]

    excel_dataframe.set_crs(epsg=4326, inplace=True)


    excel_dataframe.to_postgis('toll_data_new_demo', db.database(connection_string), if_exists='replace')
    
    logger.info("Data successfully inserted into the database.")


def process_dataframe(df, api_key):
    def batch_snap_to_road_google_maps(coordinates):
        points_str = "|".join([f"{lat},{lng}" for lat, lng in coordinates])
        url = f"https://roads.googleapis.com/v1/nearestRoads?points={points_str}&key={api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            snapped_points = [None] * len(coordinates)
            for point in data.get('snappedPoints', []):
                original_index = point.get('originalIndex')
                if original_index is not None:
                    snapped_points[original_index] = {
                        'lat': point['location']['latitude'],
                        'lng': point['location']['longitude']
                    }
            return snapped_points
        return "Error"

    rows_to_process = df[df['remark'] == "NO"]
    chunks = [rows_to_process[i:i+100] for i in range(0, rows_to_process.shape[0], 100)]
    
    new_latitudes = []
    new_longitudes = []
    
    for chunk in chunks:
        coords = list(zip(chunk['LATITUDE'], chunk['LONGITUDE']))
        snapped_points = batch_snap_to_road_google_maps(coords)
        
        if snapped_points != "Error":
            for item in snapped_points:
                if item is not None and 'lat' in item and 'lng' in item:
                    new_latitudes.append(item['lat'])
                    new_longitudes.append(item['lng'])
                else:
                    # Fallback to original coordinates if snapping failed
                    new_latitudes.append(chunk['LATITUDE'].iloc[len(new_latitudes)])
                    new_longitudes.append(chunk['LONGITUDE'].iloc[len(new_longitudes)])
        else:
            # Fallback to original coordinates if snapping failed
            new_latitudes.extend(chunk['LATITUDE'].tolist())
            new_longitudes.extend(chunk['LONGITUDE'].tolist())
    
    # Update the DataFrame only for rows where 'remark' is 'NO'
    df.loc[rows_to_process.index, 'new_latitude'] = new_latitudes
    df.loc[rows_to_process.index, 'new_longitude'] = new_longitudes
    return df



if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK-SIGNING-SECRET"))
    handler.start()
