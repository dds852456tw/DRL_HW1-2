from flask import Flask, render_template, request, jsonify
import numpy as np
import random

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    n = data.get('n', 5)
    obstacles = data.get('obstacles', [])
    terminals = data.get('terminals', [])
    policy = data.get('policy', {})
    
    # Initialize V to zeros
    V = np.zeros((n, n))
    gamma = 0.9
    threshold = 1e-4
    
    # We map string coordinates to list of actions
    # e.g., "r,c" -> ["up", "down", ...]
    
    iteration = 0
    while True:
        delta = 0
        new_V = np.copy(V)
        for r in range(n):
            for c in range(n):
                state_str = f"{r},{c}"
                
                # If it's an obstacle or terminal, value is fixed to 0
                if state_str in obstacles or state_str in terminals:
                    continue
                
                actions = policy.get(state_str, [])
                if not actions:
                    continue
                
                prob = 1.0 / len(actions)
                v_sum = 0
                
                for a in actions:
                    nr, nc = r, c
                    if a == 'up':
                        nr -= 1
                    elif a == 'down':
                        nr += 1
                    elif a == 'left':
                        nc -= 1
                    elif a == 'right':
                        nc += 1
                        
                    reward = -1  # default step reward
                    
                    # Check physical boundaries
                    if nr < 0 or nr >= n or nc < 0 or nc >= n:
                        nr, nc = r, c  # bounce back
                        reward = -1
                    elif f"{nr},{nc}" in obstacles:
                        nr, nc = r, c  # bounce back
                        reward = -1
                    elif f"{nr},{nc}" in terminals:
                        reward = 10    # positive reward for reaching the goal!
                        
                    v_sum += prob * (reward + gamma * V[nr, nc])
                
                new_V[r, c] = v_sum
                delta = max(delta, abs(new_V[r, c] - V[r, c]))
                
        V = new_V
        iteration += 1
        if delta < threshold or iteration > 1000:
            break
            
    # Round V for display
    V_list = np.round(V, 2).tolist()
    return jsonify({'values': V_list, 'iterations': iteration})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
