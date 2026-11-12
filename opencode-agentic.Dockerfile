FROM node:24-slim


RUN npm install -g @opencode/cli
RUN apt-get update && apt-get install -y git python3 python3-pip python3-venv


RUN mkdir -p /home/node/.config/opencode && \
    cat > /home/node/.config/opencode/opencode.json <<'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "model": "scilifelab/qwen3",
  "plugins": [
    "superpowers@git+https://github.com/obra/superpowers.git"
  ],
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
RUN mkdir -p /workspace
RUN chown -R node:node /workspace

USER node

WORKDIR /workspace

RUN opencode plugin add "superpowers@git+https://github.com/obra/superpowers.git"

ENTRYPOINT ["opencode"]