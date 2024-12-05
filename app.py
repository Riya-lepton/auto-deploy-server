# from slack_bolt import Ack, Say, BoltContext, App
# from slack_sdk.errors import SlackApiError
# from slack_sdk import WebClient
# import pandas as pd
# from sqlalchemy import create_engine
# import os
# from urllib.parse import quote_plus
# import requests
# from shapely.geometry import Point
# import dabbas as db
# from dotenv import load_dotenv
# load_dotenv() 
# from slack_bolt.adapter.socket_mode import SocketModeHandler 

# # Initialize Slack app (make sure to use environment variables for token)
# app = App(token=os.getenv("SLACK_BOT_TOKEN"))

# BLOCK_ID_FILE_UPLOAD = "block_file_upload"
# ACTION_ID_FILE_UPLOAD = "action_file_upload"

# # Slash command to trigger file upload
# @app.command("/upload")
# def upload_callback(ack, body, client, logger):
#     """
#     This callback opens a modal asking the user to upload a file.
#     """
#     ack()  # Acknowledge the slash command

#     try:
#         # Open the modal asking the user to upload a file
#         client.views_open(
#             trigger_id=body["trigger_id"],
#             view={
# 	"type": "modal",
# 	"title": {
        
# 		"type": "plain_text",
# 		"text": "My App",
# 		"emoji": True
# 	},
# 	"submit": {
# 		"type": "plain_text",
# 		"text": "Submit",
# 		"emoji": True
# 	},
# 	"close": {
# 		"type": "plain_text",
# 		"text": "Cancel",
# 		"emoji": True
# 	},
# 	"blocks": [
# 		{
# 			"type": "section",
# 			"block_id": BLOCK_ID_FILE_UPLOAD,
# 			"text": {
# 				"type": "mrkdwn",
# 				"text": "Please upload your file by clicking the button below. You’ll be directed to the file upload interface."
# 			}
# 		},
# 		{
# 			"type": "actions",
# 			"elements": [
# 				{
# 					"type": "button",
# 					"text": {
# 						"type": "plain_text",
# 						"text": "Upload File"
# 					},
# 					"action_id": ACTION_ID_FILE_UPLOAD
# 				}
# 			]
# 		}
# 	]
# }
#         )
        
        
#     except SlackApiError as e:
#         logger.error(f"Error opening modal: {e.response['error']}")
#         client.chat_postEphemeral(channel=body["user"]["id"], user=body["user"]["id"], text="Error opening file upload modal.")


# @app.action(ACTION_ID_FILE_UPLOAD)
# def handle_file_upload(ack, body, client, logger):
#     """
#     Handle the file upload action.
#     This will be triggered when the user clicks on the 'Upload File' button.
#     """
#     ack()  # Acknowledge the action
    
#     # Log the event (optional)
#     logger.info(f"File upload button clicked. Event body: {body}")
    
#     # Send an ephemeral message indicating the user to upload a file
#     user_id = body["user"]["id"]
    
#     client.chat_postEphemeral(
#         channel=user_id,
#         user=body["user"]["id"],
#         text="Please upload a file using the interface."
#     )
    
    

# # Handle the submission of the file upload
# @app.view("file_upload_modal")
# def handle_file_submission(ack, body, client, logger):

#     ack()  # Acknowledge the view submission
#     print(body)
#     # Get the file ID from the modal submission
#     file_id = body["state"]["values"][BLOCK_ID_FILE_UPLOAD][ACTION_ID_FILE_UPLOAD].get("file")
    
#     if not file_id:
#         client.chat_postEphemeral(
#             channel=body["user"]["id"],
#             user=body["user"]["id"],
#             text="No file uploaded. Please try again."
#         )
#         return

#     # Once the file is uploaded, process the file
#     try:
#         # Fetch file details using Slack API
#         file_info = client.files_info(file=file_id)
#         file_name = file_info["file"]["name"]
#         file_url = file_info["file"]["url_private"]

#         # Download the file using the URL
#         file_data = client.files_download(file=file_id)

#         # Process the file (assuming it is an Excel file and you want to use the provided logic)
#         excel_dataframe = pd.read_excel(file_data['file'], sheet_name=1)
#         processed_data = process_file(excel_dataframe)  # Your custom file processing function
        
#         excel_dataframe = process_dataframe(excel_dataframe, api_key)
        
#         # Insert processed data into PostgreSQL database
#         insert_data_into_db(processed_data)

#         # Send confirmation message after successful processing
#         client.chat_postMessage(
#             channel=body["user"]["id"],
#             user=body["user"]["id"],
#             text=f"Thank you! The file `{file_name}` has been successfully processed and inserted into the database."
#         )

#     except SlackApiError as e:
#         logger.error(f"Error fetching file details: {e.response['error']}")
#         client.chat_postEphemeral(
#             channel=body["user"]["id"],
#             user=body["user"]["id"],
#             text="Sorry, there was an error processing your file."
#         )

# # Function to insert processed data into the PostgreSQL database
# def insert_data_into_db(processed_data):
#     try:
#         # Connection string for PostgreSQL database
#         connection_string = 'postgresql://postgres:Alexandr1a@192.168.1.59:5432/leptonmaps'
#         engine = create_engine(connection_string)

#         # Insert processed data into the 'toll_data_new' table
#         processed_data.to_sql('toll_data_new__Demo', engine, if_exists='replace', index=False)
#         print("Data inserted into the database successfully.")

#     except Exception as e:
#         print(f"Error inserting data into the database: {e}")
#         raise



# # The file processing steps you provided (integrated into process_file)
# def process_file(excel_dataframe):
#     # Step 1: Drop duplicates
#     toll_data_new_df = pd.read_sql("SELECT * FROM toll_data_new", engine)
#     toll_data_new_df = toll_data_new_df.drop_duplicates(subset='From-To ID')
#     excel_dataframe = excel_dataframe.drop_duplicates(subset='From-To ID')

#     # Step 2: Create a set of "From-To ID" values from toll_data_new_df
#     toll_data_ids = set(toll_data_new_df['From-To ID'])

#     def check_from_to_id(row):
#         if row['From-To ID'] in toll_data_ids:
#             return "YES"
#         else:
#             return "NO"

#     # Apply the check function
#     excel_dataframe['remark'] = excel_dataframe.apply(check_from_to_id, axis=1)

#     # Step 3: Update latitude and longitude for matched "From-To ID"
#     id_to_coords = toll_data_new_df.set_index('From-To ID')[['new_latitude', 'new_longitude']].to_dict(orient='index')

#     for idx, row in excel_dataframe.iterrows():
#         if row['remark'] == "YES":
#             from_to_id = row['From-To ID']
#             if from_to_id in id_to_coords:
#                 excel_dataframe.at[idx, 'new_latitude'] = id_to_coords[from_to_id]['new_latitude']
#                 excel_dataframe.at[idx, 'new_longitude'] = id_to_coords[from_to_id]['new_longitude']

#     # Step 4: Apply Google Maps API for road snapping
    
#     import requests

# def batch_snap_to_road_google_maps(coordinates, api_key):
#     # Format coordinates as a single string for the API request
#     points_str = "|".join([f"{lat},{lng}" for lat, lng in coordinates])
#     url = f"https://roads.googleapis.com/v1/nearestRoads?points={points_str}&key={api_key}"
#     response = requests.get(url)
    
#     if response.status_code == 200:
#         data = response.json()
        
#         # Prepare a list with the same length as the input coordinates
#         snapped_points = [None] * len(coordinates)
        
#         for point in data.get('snappedPoints', []):
#             # Get the index of the original coordinate point
#             original_index = point.get('originalIndex')
            
#             if original_index is not None:
#                 # Map snapped point back to its original index
#                 snapped_points[original_index] = {
#                     'original': {'lat': coordinates[original_index][0], 'lng': coordinates[original_index][1]},
#                     'original_index': point['originalIndex'],
#                     'snapped': {
#                         'lat': point['location']['latitude'],
#                         'lng': point['location']['longitude']
#                     }
#                 }
#         return snapped_points
#     else:
#         # Return an error message if the API request fails
#         return "Error: Unable to snap to road."

# def process_dataframe(df, api_key):
#     # Filter rows where 'remark' is 'NO'
#     rows_to_process = df[df['remark'] == "NO"]
    
#     # Divide the filtered rows into chunks of 100
#     chunks = [rows_to_process[i:i+100] for i in range(0, rows_to_process.shape[0], 100)]
    
#     new_latitudes = []
#     new_longitudes = []
    
#     for chunk in chunks:
#         # Get coordinates as a list of tuples (lat, lng)
#         coordinates = list(zip(chunk['LATITUDE'], chunk['LONGITUDE']))
        
#         snapped_points = batch_snap_to_road_google_maps(coordinates, api_key)
        
#         if snapped_points != "Error: Unable to snap to road.":
#             # Append the snapped latitude and longitude, or None if snapping failed
#             for item in snapped_points:
#                 if item is not None:
#                     new_latitudes.append(item['snapped']['lat'])
#                     new_longitudes.append(item['snapped']['lng'])
#                 else:
#                     # If snapping fails, use the original LATITUDE and LONGITUDE values
#                     new_latitudes.append(chunk['LATITUDE'].iloc[len(new_latitudes)])
#                     new_longitudes.append(chunk['LONGITUDE'].iloc[len(new_longitudes)])
#         else:
#             # If snapping fails, fallback to the original LATITUDE and LONGITUDE
#             new_latitudes.extend(chunk['LATITUDE'].tolist())
#             new_longitudes.extend(chunk['LONGITUDE'].tolist())
    
#     # Update the DataFrame only for rows where 'remark' is 'NO'
#     df.loc[rows_to_process.index, 'new_latitude'] = new_latitudes
#     df.loc[rows_to_process.index, 'new_longitude'] = new_longitudes
    
#     return df

# api_key = 'AIzaSyByraLO7WVzW-9K-H6NErKftVydyJK2058'

# excel_dataframe = process_dataframe(excel_dataframe, api_key)



# Step 5: Additional transformations
# excel_dataframe['geometry'] = excel_dataframe.apply(lambda x: Point(x['new_longitude'], x['new_latitude']), axis=1)
# excel_dataframe = db.GeoDataFrame(excel_dataframe)

#     # Additional column transformations
# excel_dataframe['dynamic_toll'] = excel_dataframe['POINT_ID'].apply(lambda x: True if x[:2] == 'CT' else False)
# excel_dataframe['numeric_part'] = excel_dataframe['POINT_ID'].str.extract('(\d+)')

#     # Step 6: Count frequency of numeric parts and identify unique parts
# frequency = excel_dataframe['numeric_part'].value_counts()
# unique_numeric_parts = frequency[frequency == 1].index.tolist()
# excel_dataframe['single_toll'] = excel_dataframe['numeric_part'].isin(unique_numeric_parts)


# def split_from(x):
#     if type(x) == str:
#         split_list = x.split(',')
#         if len(split_list) == 2:
#             return split_list[0][:7]
#         else:
#             None
#     else:
#         None
    
#     # Step 7: Split From-To ID for entry point logic
# excel_dataframe['entry_point'] = excel_dataframe.POINT_ID.apply(lambda x: True if x[-2:] == 'EN' else False)
# excel_dataframe['entry_id_for_exit'] = excel_dataframe['From-To ID'].apply(split_from)
# excel_dataframe['entry_point_id'] = excel_dataframe.POINT_ID.apply(lambda x: x[:7])

# excel_dataframe = excel_dataframe

#     # Step 8: Convert specified columns to numeric
# columns_to_convert = ['2WVSJ', '2WVRJ', '2WVMP', 'CJVSJ', 'CJVRJ', 'CJVMP', 
#                           'LCNSJ', 'LCVRJ', 'LCVMP', 'BTSJ', 'BTRJ', 'BTMP', 
#                           '3AVSJ', '3AVRJ', '3AVMP', '4TO6ASJ', '4TO6ARJ', 
#                           '4TO6AMJ', 'HCM_EME_SJ', 'HCM_EME_RJ', 'HCM_EME_MJ', 
#                           '7AXLE_SJ', '7AXLE_RJ', '7AXLE_MJ']
    
# for col in columns_to_convert:
#     excel_dataframe[col] = db.to_numeric(excel_dataframe[col], errors='coerce')

#     # Fill missing values and apply further transformations as specified
# excel_dataframe[['TOLL_NAME','2WVSJ','CJVSJ','LCNSJ','BTSJ','3AVSJ',
#                      '4TO6ASJ','7AXLE_SJ']] = excel_dataframe[[
#         'TOLL_NAME','2WVSJ','CJVSJ','LCNSJ','BTSJ','3AVSJ','4TO6ASJ','7AXLE_SJ']].fillna(0)
    
    
# excel_dataframe.loc[excel_dataframe['LCNSJ'].isnull() | (excel_dataframe['LCNSJ']==0), 'LCNSJ'] = excel_dataframe['CJVSJ'][excel_dataframe['LCNSJ'].isnull() | (excel_dataframe['LCNSJ']==0)]
# excel_dataframe.loc[excel_dataframe['BTSJ'].isnull() | (excel_dataframe['BTSJ']==0), 'BTSJ'] = excel_dataframe['LCNSJ'][excel_dataframe['BTSJ'].isnull() | (excel_dataframe['BTSJ']==0)]
# excel_dataframe.loc[excel_dataframe['3AVSJ'].isnull() | (excel_dataframe['3AVSJ']==0), '3AVSJ'] = excel_dataframe['BTSJ'][excel_dataframe['3AVSJ'].isnull() | (excel_dataframe['3AVSJ']==0)]
# excel_dataframe.loc[excel_dataframe['4TO6ASJ'].isnull() | (excel_dataframe['4TO6ASJ']==0), '4TO6ASJ'] = excel_dataframe['3AVSJ'][excel_dataframe['4TO6ASJ'].isnull() | (excel_dataframe['4TO6ASJ']==0)]
# excel_dataframe.loc[excel_dataframe['HCM_EME_SJ'].isnull() | (excel_dataframe['HCM_EME_SJ']==0), 'HCM_EME_SJ'] = excel_dataframe['4TO6ASJ'][excel_dataframe['HCM_EME_SJ'].isnull() | (excel_dataframe['HCM_EME_SJ']==0)]
# excel_dataframe.loc[excel_dataframe['7AXLE_SJ'].isnull() | (excel_dataframe['7AXLE_SJ']==0), '7AXLE_SJ'] = excel_dataframe['4TO6ASJ'][excel_dataframe['7AXLE_SJ'].isnull() | (excel_dataframe['7AXLE_SJ']==0)]


# excel_dataframe.loc[excel_dataframe['2WVRJ'].isnull() | (excel_dataframe['2WVRJ'] == 0) |(excel_dataframe['2WVRJ'] <= excel_dataframe['2WVSJ']), '2WVRJ'] = 1.5 * excel_dataframe['2WVSJ'][excel_dataframe['2WVRJ'].isnull() | (excel_dataframe['2WVRJ'] == 0) |(excel_dataframe['2WVRJ'] <= excel_dataframe['2WVSJ'])]
# excel_dataframe.loc[excel_dataframe['CJVRJ'].isnull() | (excel_dataframe['CJVRJ'] == 0) |(excel_dataframe['CJVRJ'] <= excel_dataframe['CJVSJ']), 'CJVRJ'] = 1.5 * excel_dataframe['CJVSJ'][excel_dataframe['CJVRJ'].isnull() | (excel_dataframe['CJVRJ'] == 0)|(excel_dataframe['CJVRJ'] <= excel_dataframe['CJVSJ'])]
# excel_dataframe.loc[excel_dataframe['LCVRJ'].isnull() | (excel_dataframe['LCVRJ'] == 0) |(excel_dataframe['LCVRJ'] <= excel_dataframe['LCNSJ']), 'LCVRJ'] = 1.5 * excel_dataframe['LCNSJ'][excel_dataframe['LCVRJ'].isnull() | (excel_dataframe['LCVRJ'] == 0)|(excel_dataframe['LCVRJ'] <= excel_dataframe['LCNSJ'])]
# excel_dataframe.loc[excel_dataframe['BTRJ'].isnull() | (excel_dataframe['BTRJ'] == 0) |(excel_dataframe['BTRJ'] <= excel_dataframe['BTSJ']), 'BTRJ'] = 1.5 * excel_dataframe['BTSJ'][excel_dataframe['BTRJ'].isnull() | (excel_dataframe['BTRJ'] == 0)|(excel_dataframe['BTRJ'] <= excel_dataframe['BTSJ'])]
# excel_dataframe.loc[excel_dataframe['3AVRJ'].isnull() | (excel_dataframe['3AVRJ'] == 0) |(excel_dataframe['3AVRJ'] <= excel_dataframe['3AVSJ']), '3AVRJ'] = 1.5 * excel_dataframe['3AVSJ'][excel_dataframe['3AVRJ'].isnull() | (excel_dataframe['3AVRJ'] == 0)|(excel_dataframe['3AVRJ'] <= excel_dataframe['3AVSJ'])]
# excel_dataframe.loc[excel_dataframe['4TO6ARJ'].isnull() | (excel_dataframe['4TO6ARJ'] == 0) |(excel_dataframe['4TO6ARJ'] <= excel_dataframe['4TO6ASJ']), '4TO6ARJ'] = 1.5 * excel_dataframe['4TO6ASJ'][excel_dataframe['4TO6ARJ'].isnull() | (excel_dataframe['4TO6ARJ'] == 0)|(excel_dataframe['4TO6ARJ'] <= excel_dataframe['4TO6ASJ'])]
# excel_dataframe.loc[excel_dataframe['HCM_EME_RJ'].isnull() | (excel_dataframe['HCM_EME_RJ'] == 0) |(excel_dataframe['HCM_EME_RJ'] <= excel_dataframe['HCM_EME_SJ']), 'HCM_EME_RJ'] = 1.5 * excel_dataframe['HCM_EME_SJ'][excel_dataframe['HCM_EME_RJ'].isnull() | (excel_dataframe['HCM_EME_RJ'] == 0)|(excel_dataframe['HCM_EME_RJ'] <= excel_dataframe['HCM_EME_SJ'])]
# excel_dataframe.loc[excel_dataframe['7AXLE_RJ'].isnull() | (excel_dataframe['7AXLE_RJ'] == 0) |(excel_dataframe['7AXLE_RJ'] <= excel_dataframe['7AXLE_SJ']), '7AXLE_RJ'] = 1.5 * excel_dataframe['7AXLE_SJ'][excel_dataframe['7AXLE_RJ'].isnull() | (excel_dataframe['7AXLE_RJ'] == 0)|(excel_dataframe['7AXLE_RJ'] <= excel_dataframe['7AXLE_SJ'])]

# excel_dataframe.set_crs(epsg=4326, inplace=True)

# Run the Slack bot

# if __name__ == "__main__":
#     SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()





















# from slack_bolt import App
# from slack_sdk.errors import SlackApiError
# import os
# from dotenv import load_dotenv
# load_dotenv() 
# from slack_bolt.adapter.socket_mode import SocketModeHandler

# # Initialize Slack app
# app = App(token=os.getenv("SLACK_BOT_TOKEN"))

# TARGET_CHANNEL_ID = "C080LTFMBT8"  # The channel where the file will be uploaded

# # Slash command to trigger file upload instructions
# @app.command("/upload")
# def upload_callback(ack, body, client, logger):
#     """
#     Responds to the /upload command by providing file upload instructions.
#     """
#     ack()  # Acknowledge the slash command

#     user_id = body["user_id"]  # Accessing user_id from the body of the slash command

#     try:
#         # Send a message to the user directing them to the toll_data channel
#         client.chat_postMessage(
#             channel=user_id,  # Send direct message to the user
#             text=f"Hi <@{user_id}>, please upload your file to the *toll_data* channel here: <#{TARGET_CHANNEL_ID}>. I'll process it for you once you upload the file there."
#         )

#     except SlackApiError as e:
#         logger.error(f"Error sending upload instructions: {e.response['error']}")
#         client.chat_postEphemeral(
#             channel=user_id,  # Send ephemeral message to the user
#             text="There was an issue sending the upload instructions. Please try again later."
#         )

# # Handle file submission (once the file is uploaded in the channel)
# @app.event("file_shared")
# def handle_file_submission(event, client, logger):
#     """
#     Handle file upload submission.
#     This will be triggered when the user uploads a file in the `toll_data` channel.
#     """
#     file_id = event["file_id"]
#     user_id = event["user_id"]

#     try:
#         # Fetch file details using Slack API
#         file_info = client.files_info(file=file_id)
#         file_name = file_info["file"]["name"]
#         file_url = file_info["file"]["url_private"]

#         # Respond with the file name and URL in the same channel
#         client.chat_postMessage(
#             channel=TARGET_CHANNEL_ID,  # Respond in the toll_data channel
#             text=f"Thank you! The file `{file_name}` has been successfully uploaded and you can access it here: {file_url}. I'll process it shortly!"
#         )

#     except SlackApiError as e:
#         logger.error(f"Error fetching file details: {e.response['error']}")
#         client.chat_postMessage(
#             channel=TARGET_CHANNEL_ID,
#             text="Sorry, there was an error processing your file."
#         )

# # Start the app with Socket Mode handler
# if __name__ == "__main__":
#     handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
#     handler.start()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
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

TARGET_CHANNEL_ID = "C080LTFMBT8"  # The channel where the file will be uploaded

# Database connection string
connection_string = os.getenv("DB_CONNECTION_STRING")
print(f"Connection String*******************************************************************************: {connection_string}")  # Debug print

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
        # Send a message to the user directing them to the toll_data channel
        client.chat_postMessage(
            channel=user_id,  # Send direct message to the user
            text=f"Hi <@{user_id}>, please upload your file to the *toll_data* channel here: <#{TARGET_CHANNEL_ID}>. I'll process it for you once you upload the file there."
        )

    except SlackApiError as e:
        logger.error(f"Error sending upload instructions: {e.response['error']}")


@app.event("file_shared")
def handle_file_submission(event, client, logger):
    """
    Handles file upload in the 'toll_data' channel.
    Downloads the file, processes it, and uploads the results to the database.
    """
    logger.info(f"File shared event: {event}")
    
    
    # file_id = event["file_id"]
    # user_id = event["user_id"]
    
    channel_id = event.get("channel")
    
    # Only process files shared in the target channel
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
        file_url = file_info["file"]["url_private"]

        # Download the file
        headers = {"Authorization": f"Bearer {os.getenv('SLACK_BOT_TOKEN')}"}
        response = requests.get(file_url, headers=headers)
        logger.info(f"File download status: {response.status_code}")

        if response.status_code == 200:
            file_path = f"/tmp/{file_name}"
            with open(file_path, "wb") as f:
                f.write(response.content)

            # Start processing the file
            processed_data = process_and_insert_to_db(file_path)

            # Notify success
            client.chat_postMessage(
                channel=TARGET_CHANNEL_ID,
                text=f"The file `{file_name}` has been processed successfully and uploaded to the database."
            )
        else:
            raise Exception("File download failed.")

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        client.chat_postMessage(
            channel=TARGET_CHANNEL_ID,
            text="Sorry, there was an error processing your file."
        )


def process_and_insert_to_db(file_path):
    """
    Processes the Excel file and inserts the processed data into the database.
    """
    logger.info(f"Processing file: {file_path}")  
    # Load the uploaded file
    excel_dataframe = pd.read_excel(file_path, sheet_name=1)
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
            # for i, snapped in enumerate(snapped_points):
            #     if snapped:
            #         df.loc[chunk.index[i], 'new_latitude'] = snapped['lat']
            #         df.loc[chunk.index[i], 'new_longitude'] = snapped['lng']
            
            for item in snapped_points:
                if item is not None:
                    new_latitudes.append(item['snapped']['lat'])
                    new_longitudes.append(item['snapped']['lng'])
                else:
                    # If snapping fails, use the original LATITUDE and LONGITUDE values
                    new_latitudes.append(chunk['LATITUDE'].iloc[len(new_latitudes)])
                    new_longitudes.append(chunk['LONGITUDE'].iloc[len(new_longitudes)])
        else:
            # If snapping fails, fallback to the original LATITUDE and LONGITUDE
            new_latitudes.extend(chunk['LATITUDE'].tolist())
            new_longitudes.extend(chunk['LONGITUDE'].tolist())
    
    # Update the DataFrame only for rows where 'remark' is 'NO'
    df.loc[rows_to_process.index, 'new_latitude'] = new_latitudes
    df.loc[rows_to_process.index, 'new_longitude'] = new_longitudes
    return df



if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()






















# from slack_bolt import App
# from slack_sdk.errors import SlackApiError
# import pandas as pd
# from sqlalchemy import create_engine
# import os
# from dotenv import load_dotenv
# load_dotenv()
# from slack_bolt.adapter.socket_mode import SocketModeHandler
# import logging

# logging.basicConfig(filename='now_slack.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# # Initialize the Slack app
# app = App(token=os.getenv("SLACK_BOT_TOKEN"))

# BLOCK_ID_FILE_UPLOAD = "block_file_upload"
# ACTION_ID_FILE_UPLOAD = "action_file_upload"
# CALLBACK_ID = "file_upload_modal"

# # Slash command to trigger file upload
# @app.command("/upload")
# def upload_callback(ack, body, client, logger):
#     """
#     This callback opens a modal asking the user to upload a file.
#     """
#     ack()  # Acknowledge the slash command

#     try:
#         # Open the modal asking the user to upload a file
#         client.views_open(
#             trigger_id=body["trigger_id"],
#             view={
#                 "type": "modal",
#                 "title": {
#                     "type": "plain_text",
#                     "text": "My App",
#                     "emoji": True
#                 },
#                 "submit": {
#                     "type": "plain_text",
#                     "text": "Submit",
#                     "emoji": True
#                 },
#                 "close": {
#                     "type": "plain_text",
#                     "text": "Cancel",
#                     "emoji": True
#                 },
#                 "blocks": [
#                     {
#                         "type": "section",
#                         "block_id": BLOCK_ID_FILE_UPLOAD,
#                         "text": {
#                             "type": "mrkdwn",
#                             "text": "Please upload your file by clicking the button below. You’ll be directed to the file upload interface."
#                         }
#                     },
#                     {
#                         "type": "actions",
#                         "elements": [
#                             {
#                                 "type": "button",
#                                 "text": {
#                                     "type": "plain_text",
#                                     "text": "Upload File"
#                                 },
#                                 "action_id": ACTION_ID_FILE_UPLOAD  # Action ID for the button
#                             }
#                         ]
#                     }
#                 ]
#             }
#         )
#     except SlackApiError as e:
#         logger.error(f"Error opening modal: {e.response['error']}")
#         client.chat_postEphemeral(
#             channel=body["user"]["id"], 
#             text="Error opening file upload interface."
#         )

# # Handle the button click action (Upload File button click)





# @app.action(ACTION_ID_FILE_UPLOAD)
# def handle_file_upload(ack, body, client, logger):
#     ack()  # Acknowledge the button click
    
#     logger.info(f"Button clicked: {body}")

#     try:
#         # Open the file upload modal after the button click
#         client.views_open(
#             user=body['user']['id'],
#             trigger_id=body["trigger_id"],
#             view={
#                 "type": "modal",
#                 "callback_id": CALLBACK_ID,  # Proper callback_id for file upload modal
#                 "title": {
#                     "type": "plain_text",
#                     "text": "File Upload",
#                     "emoji": True
#                 },
#                 "submit": {
#                     "type": "plain_text",
#                     "text": "Submit",
#                     "emoji": True
#                 },
#                 "close": {
#                     "type": "plain_text",
#                     "text": "Cancel",
#                     "emoji": True
#                 },
#                 "blocks": [
#                     {
#                         "type": "section",
#                         "block_id": "file_upload_section",
#                         "text": {
#                             "type": "mrkdwn",
#                             "text": "Please upload your file."
#                         },
#                         "accessory": {
#                             "type": "file",
#                             "action_id": "file_upload",  # Correct action_id for file input
#                             "block_id": BLOCK_ID_FILE_UPLOAD
#                         }
#                     }
#                 ]
#             }
#         )
#     except SlackApiError as e:
#         logger.error(f"Error opening file upload modal: {e.response['error']}")
#         client.chat_postEphemeral(
#             user=body["user"]["id"],
#             channel=body["user"]["id"], 
#             text="Error opening file upload interface."
#         )

# # Handle file submission from the modal (after the user uploads the file)
# @app.view(CALLBACK_ID)
# def handle_file_submission(ack, body, client, logger):
#     ack()  # Acknowledge the view submission
#     logger.info(f"Modal submission received: {body}")

#     try:
#         # Get the file_id from the uploaded file in the modal's state values
#         file_id = body["state"]["values"][BLOCK_ID_FILE_UPLOAD]["file"].get("file")

#         if not file_id:
#             client.chat_postEphemeral(
#                 channel=body["user"]["id"],
#                 text="No file uploaded. Please try again."
#             )
#             return

#         # Fetch file details using Slack API
#         file_info = client.files_info(file=file_id)
#         file_name = file_info["file"]["name"]
#         file_url = file_info["file"]["url_private"]

#         # Download the file using the URL
#         file_data = client.files_download(file=file_id)

#         # Process the file (assuming it is an Excel file)
#         excel_dataframe = pd.read_excel(file_data['file'], sheet_name=1)
#         processed_data = process_file(excel_dataframe)  # Your custom file processing function

#         # Insert processed data into PostgreSQL database
#         insert_data_into_db(processed_data)

#         # Send confirmation message after successful processing
#         client.chat_postEphemeral(
#             channel=body["user"]["id"], 
#             text=f"Thank you! The file `{file_name}` has been successfully processed and inserted into the database."
#         )

#     except SlackApiError as e:
#         logger.error(f"Error fetching file details: {e.response['error']}")
#         client.chat_postEphemeral(
#             channel=body["user"]["id"], 
#             text="Sorry, there was an error processing your file."
#         )

# # Function to insert processed data into the PostgreSQL database
# def insert_data_into_db(processed_data):
#     try:
#         # Connection string for PostgreSQL database
#         connection_string = 'postgresql://postgres:Alexandr1a@192.168.1.59:5432/leptonmaps'
#         engine = create_engine(connection_string)

#         # Insert processed data into the 'toll_data_new' table
#         processed_data.to_sql('toll_data_new__Demo', engine, if_exists='replace', index=False)
#         print("Data inserted into the database successfully.")

#     except Exception as e:
#         print(f"Error inserting data into the database: {e}")
#         raise

# # The file processing steps you provided (integrated into process_file)
# def process_file(excel_dataframe):
#     # Your file processing logic here...
#     return excel_dataframe

# if __name__ == "__main__":
#     handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
#     handler.start()