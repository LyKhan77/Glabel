// frontend/src/api/llmService.js
export async function askGlabelAssistant(userPrompt, config) {
  const { baseUrl, apiKey, model } = config;
  
  // Clean up baseUrl (ensure no trailing slash, add /v1/chat/completions if not present)
  let endpoint = baseUrl;
  if (!endpoint.endsWith('/v1/chat/completions')) {
    endpoint = endpoint.replace(/\/+$/, '') + '/v1/chat/completions';
  }

  const systemPrompt = `You are the Glabel Assistant, an expert Computer Vision Engineer.
Based on the user's description, recommend the most appropriate task_type.
Valid task types: classification, object_detection, segmentation, pose_estimation.
Also generate a short project name (max 4 words).

Reply ONLY with a valid JSON object in this exact format, with no markdown formatting or extra text:
{
  "task_type": "...",
  "project_name": "..."
}`;

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(apiKey ? { 'Authorization': `Bearer ${apiKey}` } : {})
      },
      body: JSON.stringify({
        model: model || 'llama3', // Default or provided model
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ],
        temperature: 0.1
      })
    });

    if (!response.ok) {
      throw new Error(`LLM API error: ${response.statusText}`);
    }

    const data = await response.json();
    const resultText = data.choices[0].message.content.trim();
    
    // Attempt to parse JSON
    try {
      const parsed = JSON.parse(resultText);
      return parsed;
    } catch (e) {
      console.error("Failed to parse LLM response as JSON:", resultText);
      throw new Error("Assistant response was not valid JSON");
    }
  } catch (error) {
    console.error("askGlabelAssistant error:", error);
    throw error;
  }
}
