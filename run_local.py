import os
from dotenv import load_dotenv
from agents.acord_extractor.agent import create_agent

if __name__ == "__main__":
    load_dotenv()  # load .env variables

    agent = create_agent()
    
    pdf_path = "samples/ACORD-125-sample.pdf"  # change path

    result = agent({"pdf_path": pdf_path})
    print(result)
