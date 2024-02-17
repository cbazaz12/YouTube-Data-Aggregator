#Import GoogleApiClient for making API calls
import googleapiclient.discovery
from googleapiclient.discovery import build
import requests
import pandas as pd
from matplotlib import pyplot as plt
from urllib.parse import urlparse
import sys

#Api_Key
api_key = 'YOUR API KEY HERE'

# Function to fetch channel ID from channel name or link
def get_channel_id(channel_identifier):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.search().list(
        part='snippet',
        q=channel_identifier,
        type='channel',
        maxResults=1
    )
    response = request.execute()
    if response['items']:
        channel_id = response['items'][0]['snippet']['channelId']
        return channel_id
    else:
        return None

#ChannelData function send requests to youtube channel resource using list methods which 
#Returns a collection of zero or more channel resources that match the request criteria.
#Response is parsed and store in required format using list of dictionaries
def ChannelData(channels):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    request = youtube.channels().list(part="snippet,contentDetails,statistics",id=','.join(channels))
    response = request.execute()
    
    Channel_data = []
    for items in response['items']:
        data = dict(
            Channel_name = items['snippet']['title'], 
            Channel_Created = items['snippet']['publishedAt'],
            Channel_country = items['snippet'].get('country'),
            Channel_uploads = items['contentDetails']['relatedPlaylists']['uploads'],
            Channel_viewcount = items['statistics']['viewCount'],
            Channel_subcount = items['statistics']['subscriberCount'],
            Channel_vidcount = items['statistics']['videoCount']

        )
        Channel_data.append(data)
    return Channel_data

#VideoMetaDetails Function extracts playlist id and calls VideoMetaData function on each playlistId to extract details of all videos of a 
#particular channel from youtube playlistitems resource and stores the parsed data in Master_Videolist 

def VideoMetaDetails(Channel_Data):
    
    Master_Videolist = []

    for items in Channel_Data:
        Video_data = VideoMetaData(items['Channel_uploads'])
        
        for i in range(len(Video_data)):
            for item in Video_data[i]['items']:
                data = dict(
                    Video_id = item["contentDetails"]["videoId"],
                    Video_published_date = item["contentDetails"]["videoPublishedAt"],
                    Channel_name = item["snippet"]["channelTitle"],
                    Video_description = item['snippet']["description"],
                    Video_position = item['snippet']["position"]
                    )
                Master_Videolist.append(data)
    return Master_Videolist

#VideoMetaData Function - Make api calls to PlaylistItems where PlaylistId from each channel is passed as an arguement by VideoMetaDetails function
#The function handles pagination using NextPageToken extracted from response
#Video details for each playlist in appended and Video_data list of all video details of all channels is returned to VideoMetaDetails function for data extraction

def VideoMetaData(Channel_uploads, page_token=None):
    Video_data = []
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=50,
        playlistId=Channel_uploads,
        pageToken=page_token
    )

    response_playlist = request.execute()
    Video_data.append(response_playlist)

    # Continue fetching additional pages if nextPageToken is present
    while 'nextPageToken' in response_playlist:
        next_page_token = response_playlist['nextPageToken']
        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            maxResults=50,
            playlistId=Channel_uploads,
            pageToken=next_page_token
        )
        response_playlist = request.execute()
        Video_data.append(response_playlist)

    return Video_data


#Video_Details function makes api call for 50 VideoIds, VideoIds are passed as an arguement by GetVideoStats function
#Respective response is parsed and data is extracted for video Statistics
#Extracted video statistics details are returned as list datatype to GetVideoStats 
def Video_Details(video_id):
  Video_stats = []
  youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
  request = youtube.videos().list(part="snippet,contentDetails,statistics",
                                  id=','.join(video_id))
  response = request.execute()
  for item in response['items']:
    data = dict(
        Video_id = item['id'],
        Video_Channel_title = item['snippet'].get("channelTitle"),
        Stats_Comment = item['statistics'].get('commentCount'),
        Stats_Fav = item['statistics'].get("favoriteCount"),
        Stats_Like = item['statistics'].get("likeCount"),
        Stats_view =item['statistics'].get("viewCount")

    )
    Video_stats.append(data)
  
  return Video_stats

#GetVideoStats --- Extract VideoIDs length for a particular channel and pass VideoIds as arguement to Video_details function in batch of 50ids per call
#Recived response is converted to Dataframe and concatinated in batches of each individual channel video statistics
def GetVideoStats(Colname):
    limit = len(list(MasterVideoDF[MasterVideoDF['Channel_name'] == Colname]['Video_id']))
    MasterVideoStats = []
    for i in range(0,limit, 50):
        if i >= (limit - 50):
            Video_list = list(MasterVideoDF[MasterVideoDF['Channel_name'] == Colname ]['Video_id'])[i:limit]
        else:
            Video_list = list(MasterVideoDF[MasterVideoDF['Channel_name'] == Colname ]['Video_id'])[i:i+50]
        
        VideoStats = Video_Details(Video_list)
        MasterVideoStats.append(VideoStats)

    length_videostats = len(MasterVideoStats)
    for i in range(length_videostats):
        if i == 0 :
            MasterStatistics = pd.DataFrame(MasterVideoStats[i])
        else:
            MasterStatistics = pd.concat([MasterStatistics,pd.DataFrame(MasterVideoStats[i])])

    return MasterStatistics

if __name__ == '__main__':
    channels = []
    num_channels = int(input("Enter the number of YouTube channels: "))
    for _ in range(num_channels):
        channel_identifier = input("Enter YouTube Channel Name or Link: ")
        channels.append(channel_identifier)

    channel_ids = []
    for channel_identifier in channels:
        # Extract channel ID from link if provided
        parsed_url = urlparse(channel_identifier)
        if parsed_url.netloc == 'www.youtube.com':
            if parsed_url.path == '/channel/':
                channel_id = parsed_url.path.split('/')[-1]
            elif parsed_url.path.startswith('/user/') or parsed_url.path.startswith('/c/'):
                channel_id = parsed_url.path.split('/')[-1]
            else:
                # Handle custom URL format like https://www.youtube.com/@DoaenelYT
                # Extracting the channel ID from the query parameters
                query_params = parse_qs(parsed_url.query)
                if 'channel' in query_params:
                    channel_id = query_params['channel'][0]
                else:
                    channel_id = None
        else:
            channel_id = get_channel_id(channel_identifier)

        if channel_id:
            channel_ids.append(channel_id)
        else:
            print(f"Channel {channel_identifier} not found.")
            
    if not channel_ids:
        print("No channel IDs found. Exiting...")
        sys.exit()
        
    print("Creating csv files...")
    #Create data frames
    Channel_Data = ChannelData(channel_ids)
    Channel_DataDF = pd.DataFrame(Channel_Data)
    Master_Videolist = VideoMetaDetails(Channel_Data)
    MasterVideoDF = pd.DataFrame(Master_Videolist)

    #Call GetVideoStats function on each channel to get Video Statistics Details
    VideoStatistics = pd.DataFrame()
    for i in MasterVideoDF.Channel_name.unique():
        videodf = GetVideoStats(i)
        VideoStatistics = pd.concat([VideoStatistics,videodf])

    #Extract to csv files
    Channel_DataDF.columns = ['Channel Name', 'Date Created', 'Country', 'Uploads', 'Total Viewcount', 'Sub Count', 'Video Count']
    MasterVideoDF.columns = ['Video ID', 'Publish Date', 'Channel Name', 'Video Description', 'Position']
    VideoStatistics.columns = ['Video ID', 'Channel Name', 'Total Comments', 'Total Favorites', 'Total Likes', 'Total Views']
    Channel_DataDF.to_csv('D:\YouTube Data Aggregator\ChannelData.csv')
    MasterVideoDF.to_csv('D:\YouTube Data Aggregator\VideoDetails.csv')
    VideoStatistics.to_csv('D:\YouTube Data Aggregator\VideoStatistics.csv')
    print('Success')