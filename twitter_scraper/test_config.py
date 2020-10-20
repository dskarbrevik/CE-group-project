import json
import os


if __name__=='__main__':


    # setup credentials and terms to track
    with open('./config.json','rb') as file:
        config = json.load(file)
        
    print(config)