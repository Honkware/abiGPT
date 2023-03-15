import os
from flask import Flask, render_template, request, jsonify
from langchain.llms import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize the OpenAI language model
llm = OpenAI(
    openai_api_key=os.environ.get('OPENAI_API_KEY'),
    model_name="gpt-3.5-turbo",
    temperature=0.3,
)

def convert_abi(abi, abi_type):
    # Template string for the ABI conversion prompt
    abi_detection_conversion_template = f"""
    As an ABI converter program, my purpose is to convert valid Ethereum contract Application Binary Interface (ABI) inputs into the specified formats. I will not engage in any conversation, discussion, or process inappropriate content. If the input is invalid, unsupported, or inappropriate, I will return a simple error message stating, "Invalid ABI input."
    
    Input: Ethereum contract ABI
    {{abi}}
    
    Task: Detect and convert the ABI provided into the {{abi_type}} format.
    
    For reference, the available ABI types and their explanation are as follows:
    
    - Human-readable: A human-readable string that describes the function signature or event.
    - Solidity JSON: A JSON representation of the ABI used by the Solidity compiler.
    - Solidity Object: A JavaScript object that represents the ABI, used by ethers.js library.
    
    Output: Only include the converted ABI in your response. Do not include any additional explanations or descriptors before or after the converted ABI.
    """

    # Replace placeholders in the template string with actual values
    abi_detection_conversion_prompt = abi_detection_conversion_template.format(abi=abi, abi_type=abi_type)

    # Use the OpenAI language model to generate the converted ABI
    abi_detection_conversion_response = llm(abi_detection_conversion_prompt)

    # Remove leading/trailing white space from the response
    return abi_detection_conversion_response.strip()


@app.route('/stream_abi', methods=['POST'])
def stream_abi():
    # Extract the ABI and ABI type from the POST request
    abi = request.form['abi']
    abi_type = request.form['abi_type']

    # Convert the ABI to the specified type
    converted_abi = convert_abi(abi, abi_type)

    # Return the converted ABI in JSON format
    return jsonify({"converted_abi": converted_abi})


@app.route('/', methods=['GET'])
def index():
    # Render the index.html template
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
