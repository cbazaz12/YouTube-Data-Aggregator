# YouTube-Data-Aggregator

Before Running:
1. install google api if needed:
    'pip install google-api-python-client pandas'
2. Update the code on line 10 to include your API key (replace 'YOUR API KEY HERE')
3. If running in Jupyter Notebook, use the .ipynb version
4. Else, use the .py version

Features:
- Program will first for a number of inputs
- You will be prompted to enter the specified amount of inputs
- Inputs can be the channel name, or in the form youtube.com/ChannelName
- 3 csv files will be created: ChannelData.csv, VideoDetails.csv, VideoStatistics.csv
- ChannelData includes a DataFrame containing channel name, date created, country, uploads, viewvount, subcount, and video count
- VideoDetails includes a DataFrame containing video ID, publish date, channel name, video description, and position
- VideoStatistics includes a DataFrame containing video ID, channel name, total comments, total favorites, total likes, and total views
- If a channel could not be found, a message "Channel {channel_identifier} not found" will be printed
- Upon completion, the program will print "Success!"
