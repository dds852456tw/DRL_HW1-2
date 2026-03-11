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
    actions_list = ['up', 'down', 'left', 'right']
    
    while True:
        delta = 0
        new_V = np.copy(V)
        
        for r in range(n):
            for c in range(n):
                state_str = f"{r},{c}"
                
                # If it's an obstacle or terminal, value is fixed to 0
                if state_str in obstacles or state_str in terminals:
                    continue
                
                max_v = -float('inf')
                
                for a in actions_list:
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
                        
                    # Check if next state is obstacle
                    elif f"{nr},{nc}" in obstacles:
                        nr, nc = r, c
                    
                    # Check if next state is terminal
                    elif f"{nr},{nc}" in terminals:
                        reward = 0    # Reward 0 for reaching terminal
                    
                    v_val = reward + gamma * V[nr, nc]
                    if v_val > max_v:
                        max_v = v_val
                
                new_V[r, c] = max_v
                delta = max(delta, abs(new_V[r, c] - V[r, c]))
                
        V = new_V
        iteration += 1
        if delta < threshold or iteration > 1000:
            break
            
    # Extract greedy policy
    optimal_policy = {}
    for r in range(n):
        for c in range(n):
            state_str = f"{r},{c}"
            if state_str in obstacles or state_str in terminals:
                continue
                
            best_actions = []
            max_v = -float('inf')
            
            for a in actions_list:
                nr, nc = r, c
                if a == 'up':
                    nr -= 1
                elif a == 'down':
                    nr += 1
                elif a == 'left':
                    nc -= 1
                elif a == 'right':
                    nc += 1
                    
                reward = -1
                
                if nr < 0 or nr >= n or nc < 0 or nc >= n:
                    nr, nc = r, c
                elif f"{nr},{nc}" in obstacles:
                    nr, nc = r, c
                elif f"{nr},{nc}" in terminals:
                    reward = 0
                    
                v_val = reward + gamma * V[nr, nc]
                
                # We use a small epsilon for floating point comparison
                if v_val > max_v + 1e-6:
                    max_v = v_val
                    best_actions = [a]
                elif abs(v_val - max_v) <= 1e-6:
                    best_actions.append(a)
                    
            optimal_policy[state_str] = best_actions
            
    # Round V for display
    V_list = np.round(V, 2).tolist()
    return jsonify({'values': V_list, 'iterations': iteration, 'policy': optimal_policy})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
