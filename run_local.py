import os
import json
from dotenv import load_dotenv
from agents.acord_extractor.agent import create_agent

if __name__ == "__main__":
    load_dotenv()  # load .env variables

    agent = create_agent()
    
    pdf_path = "samples/140-Property-Acord-1.pdf"  # change path

    result = agent({"pdf_path": pdf_path})
    
    # Print to console
    print(result)
    
    # Save to JSON file
    output_file = "output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"\n✓ Output saved to {output_file}")
