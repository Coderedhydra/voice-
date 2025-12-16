from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)
CORS(app)  # allow Netlify frontend to call this backend

MODEL_NAME = "smollm-1.7b"  # small local model

print("Loading model:", MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)
print("Model loaded!")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("text", "").strip()
    if not question:
        return jsonify({"answer": "No question provided."})

    try:
        inputs = tokenizer(question, return_tensors="pt").to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.7)
        answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        answer = f"Error generating answer: {e}"

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
