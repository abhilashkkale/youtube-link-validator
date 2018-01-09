import urllib3
import json
import constants

''' This function reads input csv file which has the links to be validated '''
def read_file():
    try:
        file_object = open(constants.SOURCE_FILE, "r+")
        file_content = file_object.read()
        file_object.close()
        return file_content
    except IOError:
        print("File not found..Please create file")
        file_content=''
        return file_content


''' This function creates a list of youtube links read from input csv file i.e youtube-link-source.csv & returns the list '''
def get_youtube_links_list():
    youtube_links=[]
    if len(file_content)!=0:
        youtube_links = file_content.split("\n")
        if len(youtube_links[len(youtube_links)-1])==0 :
            del youtube_links[len(youtube_links)-1]
    # print("Youtube Links : ",youtube_links)
    return youtube_links


''' This function makes API call based on the provided video API link and returns status as valid or invalid basedon validation done'''
def make_api_call(api_link):
    http = urllib3.PoolManager()
    try:
        response_in_bytes = http.request('GET',api_link)
        response_in_json = response_in_bytes.data.decode('utf8')
        response_dict = json.loads(response_in_json)
        item_list = response_dict['items']
        if len(item_list) == 0:
            # print("Invalid video based on item list length being zero")
            return constants.INVALID
        else:
            items_dict = item_list[0]
            if 'contentDetails' in items_dict:
                # print("Content details are : ",items_dict['contentDetails'])
                content_details_dict = items_dict['contentDetails']
                if 'regionRestriction' in content_details_dict:
                    region_restriction = content_details_dict['regionRestriction']
                    if 'blocked' in region_restriction:
                        if "IN" in region_restriction['blocked']:
                            # print("Invalid video based on region restriction")
                            return constants.INVALID
                else:
                    # print("Valid URL")
                    return constants.VALID

    except urllib3.exceptions.NewConnectionError:
        print("Connection failed..")


''' This function provides final dictionary of youtube links as key and status as its value '''
def youtube_link_validator():

    link_status_dict = {}
    if len(youtube_links)!=0 :

        for link in youtube_links:

            link_parts = link.split('v=')
            video_id = link_parts[1]
            final_api_link = constants.BASE_API + video_id + constants.KEY_PARAM + constants.API_KEY
            status = make_api_call(final_api_link)
            link_status_dict[link] = status

    # print(link_status_dict)
    return link_status_dict


''' This  function writes the final dictionary of youtube links & its status in a destiantion csv i.e youtube-link-status.csv file '''
def write_link_status():
    try:
        file_object = open(constants.DESTINATION_FILE, "w")
        file_object.write(constants.LINK_TITLE + '\t' + constants.STATUS_TITLE + '\n')
        for key, value in link_status_dict.items():
            file_object.write(str(key) + '\t' + str(value) + '\n')
        print("Validation completed. Check contents in youtube-link-status.csv")
    except IOError:
        print(" Error while writing to file.")


if __name__ == "__main__":
    video_id = constants.VIDEO_ID
    file_content = read_file()
    youtube_links = get_youtube_links_list()
    link_status_dict = youtube_link_validator()
    write_link_status()