from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Azure Blob and Search configurations
blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_BLOB_CONNECTION_STRING"))
container_name = "your-container-name"

# Use AzureKeyCredential for authentication
search_client = SearchClient(
    endpoint=f"https://{os.getenv('AZURE_SEARCH_SERVICE_NAME')}.search.windows.net",
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Upload a document to Azure Blob
@app.route('/upload', methods=['POST'])
def upload_document():
    file = request.files['file']
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file.filename)
    blob_client.upload_blob(file.read(), overwrite=True)
    
    return jsonify({"message": "File uploaded successfully!"}), 200

# Delete a document from Azure Blob
@app.route('/delete', methods=['DELETE'])
def delete_document():
    filename = request.args.get('filename')
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
    blob_client.delete_blob()
    
    return jsonify({"message": "File deleted successfully!"}), 200

# Search for documents in Azure Cognitive Search
@app.route('/search', methods=['POST'])
def search_documents():
    query = request.json.get("query")
    results = search_client.search(query)
    documents = [result['content'] for result in results]  # Extracting the content of the documents
    
    return jsonify(documents), 200

# Generate a response using RAG (Search + GPT)
@app.route('/chat', methods=['POST'])
def chat_with_gpt():
    try:
        data = request.get_json()  # Get the JSON input
        prompt = data.get("prompt", "")
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        # Step 1: Search for relevant documents in Azure Cognitive Search
        query = data.get("query", "")
        search_results = search_client.search(query)  # Search based on user query
        documents = [result['content'] for result in search_results]  # Collect the search results
        
        # Step 2: Combine the search results into a single context
        context = " ".join(documents)  # Merging all documents into one large context
        
        # Step 3: Create the prompt with context and send it to GPT-4
        full_prompt = f"Context: {context}\n\nPrompt: {prompt}"
        
        # Updated OpenAI API call using the new format
        response = openai.chat_completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=150
        )

        # Extract the response from the new structure
        gpt_response = response.choices[0]['message']['content'].strip()

        # Step 4: Return the generated response from GPT-4
        return jsonify({"response": gpt_response}), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to process request: {str(e)}"}), 400

if __name__ == '__main__':
    app.run(debug=True)
