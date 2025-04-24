import requests
import json
import config
from typing import Dict, Any, Optional, Union, Iterator # Added Iterator and Union

class OpenRouterAPI:
    """
    Plugin for connecting to OpenRouter API to access various AI models
    """

    def __init__(self):
        self.api_key = config.openrouter_key
        self.model = config.openrouter_model
        self.base_url = "https://openrouter.ai/api/v1"
        # Increased default timeout slightly for streaming
        self.timeout = int(config.timeout) if config.timeout else 60 

    # Modified return type hint
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, stream: bool = False) -> Union[Dict[Any, Any], requests.Response]:
        """
        Generate a response from the AI model using OpenRouter

        Args:
            prompt: The user's message/prompt
            system_prompt: Optional system instructions
            stream: Whether to stream the response

        Returns:
            If stream=False, Dict containing the response data or error information.
            If stream=True, the raw requests.Response object for iteration or error Dict.
        """
        if not self.api_key or self.api_key == "your_openrouter_api_key":
            return {"error": "OpenRouter API key not configured"}

        if not self.model or self.model == "your_ai_model":
            return {"error": "OpenRouter model not configured"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/usif-x/IGController" # Optional: Add your specific app URL/name if desired
            # "X-Title": "Your App Name" # Optional: Can help OpenRouter identify traffic
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1500, # Consider adjusting based on expected response length
            "stream": stream
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout, # Ensure timeout is sufficient for streaming
                stream=stream # CRITICAL: Pass stream=True to requests
            )

            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

            # --- Critical Change Here ---
            if stream:
                # Return the raw response object for iteration when streaming
                return response
            else:
                # Return the parsed JSON for non-streaming responses
                return response.json()
            # --- End Critical Change ---

        except requests.exceptions.RequestException as e:
            # Catch specific request exceptions
            error_details = f"Request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                 error_details += f" | Status Code: {e.response.status_code} | Body: {e.response.text[:500]}" # Log part of the error body
            return {"error": error_details}
        except Exception as e:
            # Catch other potential errors
             return {"error": f"An unexpected error occurred: {str(e)}"}

    # Modified return type hint
    def get_text_response(self, prompt: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        """Get text response (now supports streaming correctly)"""
        response_or_error = self.generate_response(prompt, system_prompt, stream=True)

        # Check if generate_response returned an error dictionary
        if isinstance(response_or_error, dict) and "error" in response_or_error:
            yield f"Error: {response_or_error['error']}"
            return # Stop iteration

        # Check if it's a successful streaming response object
        if isinstance(response_or_error, requests.Response):
            try:
                # Use iter_lines to handle streaming chunks delimited by newlines
                for line in response_or_error.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        # OpenAI compatible streams often prefix with 'data: '
                        if decoded_line.startswith('data: '):
                            json_str = decoded_line[len('data: '):].strip()
                            if json_str == '[DONE]': # Check for stream termination signal
                                break
                            try:
                                data = json.loads(json_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta and delta["content"] is not None:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                print(f"Warning: Could not decode JSON chunk: {json_str}")
                                continue # Skip malformed lines
                        # Handle potential plain text lines if the format differs (less common for chat completions)
                        # elif decoded_line.strip():
                        #    yield decoded_line # Or process as needed

            except requests.exceptions.ChunkedEncodingError as e:
                print(f"Streaming connection error: {e}")
                yield "Error: Connection issue during streaming."
            except Exception as e:
                print(f"Error processing stream: {e}")
                yield f"Error: Failed to process streaming response - {str(e)}"
            finally:
                 # Ensure the response connection is closed
                 response_or_error.close()
        else:
            # Handle unexpected return type from generate_response
            yield "Error: Unexpected response type from API."