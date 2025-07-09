client<llm> CustomGenericProvider {
  provider openai-generic
  retry_policy Constant
  options {
    base_url "https://api.studio.nebius.com/v1/"
    model "meta-llama/Meta-Llama-3.1-70B-Instruct" // 
    api_key env.NEBIUS_API_KEY
    temperature 0.0
  }
}


// https://docs.boundaryml.com/docs/snippets/clients/retry
retry_policy Constant {
  max_retries 3
  // Strategy is optional
  strategy {
    type constant_delay
    delay_ms 200
  }
}
