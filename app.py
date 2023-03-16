import os
from flask import Flask, render_template, request, jsonify
from langchain.llms import OpenAIChat
from langchain.agents import initialize_agent, load_tools
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize the OpenAI language model
llm = OpenAIChat(
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
    model_name="gpt-4",
)

tools = load_tools(["requests"], llm=llm)

agent = initialize_agent(
    tools, llm, agent="chat-zero-shot-react-description", verbose=True
)


def convert_abi(abi, abi_type):
    # Template string for the ABI conversion prompt
    abi_detection_conversion_template = f"""
    As an ABI converter, I convert Ethereum contract ABI inputs into specified formats without processing inappropriate content. Invalid inputs return "Invalid ABI input."
    
    Input: Ethereum contract ABI
    {{abi}}
    
    Task: Convert the ABI provided into the {{abi_type}} format.
    
    ABI types with short examples:
    - Human-readable: {{hr_example}}
    - Solidity JSON: {{json_example}}
    - Solidity Object: {{obj_example}}
    
    Output: Include only the converted raw ABI. Do not add extra descriptors like "Human-Readable:", "Solidity JSON:", "Solidity Object:".
    
    Important: Make sure to output the ABI in the correct {{abi_type}} format. If the requested format is Human-readable, the output should not be in JSON or Object format. Similarly, if the requested format is Solidity JSON or Solidity Object, the output should not be in human-readable format.
    """

    # Replace placeholders in the template string with actual values
    abi_detection_conversion_prompt = abi_detection_conversion_template.format(
        abi=abi,
        abi_type=abi_type,
        hr_example="function transfer(address to, uint256 amount)",
        json_example='{"type": "function", "name": "transfer", "inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}]}',
        obj_example='{type: "function", name: "transfer", inputs: [{name: "to", type: "address"}, {name: "amount", type: "uint256"}]}',
    )

    # Use the OpenAI language model to generate the converted ABI
    abi_detection_conversion_response = agent.run(abi_detection_conversion_prompt)

    # Return the converted ABI
    return abi_detection_conversion_response

    # Remove leading/trailing white space from the response
    return abi_detection_conversion_response.strip()


@app.route("/stream_abi", methods=["POST"])
def stream_abi():
    # Extract the ABI and ABI type from the POST request
    abi = request.form["abi"]
    abi_type = request.form["abi_type"]

    # Convert the ABI to the specified type
    converted_abi = convert_abi(abi, abi_type)

    # Return the converted ABI in JSON format
    return jsonify({"converted_abi": converted_abi})


@app.route("/", methods=["GET"])
def index():
    # Render the index.html template
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
