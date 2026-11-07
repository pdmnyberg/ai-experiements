FROM node:24-slim


RUN npm install -g @opencode/cli


RUN mkdir -p /home/node/.config/opencode && \
    cat > /home/node/.config/opencode/opencode.json <<'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "model": "scilifelab/qwen3",
  "providers": {
    "scilifelab": {
      "name": "SciLifeLab OpenLLM",
      "env": ["SCILIFELAB_API_KEY"],
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": {
        "baseURL": "https://openllm.scilifelab.se/api",
        "apiKey": "{env:SCILIFELAB_API_KEY}"
      },
      "models": {
        "qwen3": {
          "modelID": "Qwen3-235B-A22B"
        }
      }
    }
  }
}
EOF

RUN chown -R node:node /home/node/.config/opencode

USER node

WORKDIR /workspace


ENTRYPOINT ["opencode"]