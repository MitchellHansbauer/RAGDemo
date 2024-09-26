import React, { useState } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState('');
  const [prompt, setPrompt] = useState('');
  const [context, setContext] = useState('');
  const [chatResponse, setChatResponse] = useState('');
  
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleFileUpload = async () => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData
      });
      alert('File uploaded successfully');
    } catch (error) {
      console.error(error);
      alert('Failed to upload file');
    }
  };

  const handleFileDelete = async () => {
    try {
      await fetch(`http://localhost:5000/delete?filename=${filename}`, {
        method: 'DELETE'
      });
      alert('File deleted successfully');
    } catch (error) {
      console.error(error);
      alert('Failed to delete file');
    }
  };

  const handleChatGPT = async () => {
    setChatResponse(''); // Reset the chat response before starting

    try {
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt, query: context })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      while (!done) {
        const { value, done: streamDone } = await reader.read();
        done = streamDone;
        const chunk = decoder.decode(value, { stream: true });
        setChatResponse((prev) => prev + chunk); // Append the new chunk to the response
      }
    } catch (error) {
      console.error(error);
      alert('Failed to get response');
    }
  };

  return (
    <div className="App">
      <h1>RAG Solution with Azure & ChatGPT</h1>

      {/* Upload File */}
      <h2>Upload Document</h2>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleFileUpload}>Upload</button>

      {/* Delete File */}
      <h2>Delete Document</h2>
      <input 
        type="text" 
        placeholder="Enter filename to delete" 
        value={filename} 
        onChange={(e) => setFilename(e.target.value)} 
      />
      <button onClick={handleFileDelete}>Delete</button>

      {/* ChatGPT Prompt */}
      <h2>Chat with GPT</h2>
      <textarea 
        rows="4" 
        placeholder="Enter prompt" 
        value={prompt} 
        onChange={(e) => setPrompt(e.target.value)} 
      />
      <textarea 
        rows="4" 
        placeholder="Enter context (optional)" 
        value={context} 
        onChange={(e) => setContext(e.target.value)} 
      />
      <button onClick={handleChatGPT}>Ask ChatGPT</button>

      {/* ChatGPT Response */}
      <h3>ChatGPT Response:</h3>
      <p>{chatResponse}</p>
    </div>
  );
}

export default App;
