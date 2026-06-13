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
    
    # Read custom MDP parameters
    gamma = float(data.get('gamma', 0.9))
    step_reward = float(data.get('step_reward', -1.0))
    terminal_reward = float(data.get('terminal_reward', 10.0))
    transition_type = data.get('transition_type', 'deterministic')
    
    # Initialize V to zeros
    V = np.zeros((n, n))
    threshold = 1e-4
    max_iterations = 1000
    
    actions_list = ['up', 'down', 'left', 'right']
    action_dirs = {
        'up': (-1, 0),    # row decreases (upwards in visual grid)
        'down': (1, 0),   # row increases (downwards in visual grid)
        'left': (0, -1),  # col decreases (leftwards in visual grid)
        'right': (0, 1)   # col increases (rightwards in visual grid)
    }
    perpendiculars = {
        'up': ['left', 'right'],
        'down': ['left', 'right'],
        'left': ['up', 'down'],
        'right': ['up', 'down']
    }
    
    iteration = 0
    while True:
        delta = 0
        new_V = np.copy(V)
        
        for r in range(n):
            for c in range(n):
                state_str = f"{r},{c}"
                
                # If it's an obstacle or terminal, its value is fixed (not updated, remains 0.0)
                if state_str in obstacles or state_str in terminals:
                    continue
                
                # Get policy actions for this state.
                # policy is a dictionary: "r,c" -> list of actions, e.g., ["up", "right"]
                state_actions = policy.get(state_str, [])
                if not state_actions:
                    # If no actions are set, default to uniform policy over all actions
                    state_actions = actions_list
                
                p_action = 1.0 / len(state_actions)
                expected_v = 0.0
                
                for a in state_actions:
                    if transition_type == 'deterministic':
                        outcomes = [(a, 1.0)]
                    else:
                        # Stochastic: 0.8 probability of success, 0.1 for each perpendicular direction
                        outcomes = [
                            (a, 0.8),
                            (perpendiculars[a][0], 0.1),
                            (perpendiculars[a][1], 0.1)
                        ]
                    
                    for act, prob in outcomes:
                        dr, dc = action_dirs[act]
                        nr, nc = r + dr, c + dc
                        
                        reward = step_reward
                        
                        # Check boundaries
                        if nr < 0 or nr >= n or nc < 0 or nc >= n:
                            nr, nc = r, c
                        # Check obstacles
                        elif f"{nr},{nc}" in obstacles:
                            nr, nc = r, c
                        
                        # Check terminal
                        if f"{nr},{nc}" in terminals:
                            expected_v += prob * p_action * terminal_reward
                        else:
                            expected_v += prob * p_action * (reward + gamma * V[nr, nc])
                
                new_V[r, c] = expected_v
                delta = max(delta, abs(new_V[r, c] - V[r, c]))
                
        V = new_V
        iteration += 1
        if delta < threshold or iteration > max_iterations:
            break
            
    # Extract greedy policy based on evaluated V
    greedy_policy = {}
    for r in range(n):
        for c in range(n):
            state_str = f"{r},{c}"
            if state_str in obstacles or state_str in terminals:
                continue
                
            best_actions = []
            max_v = -float('inf')
            
            for a in actions_list:
                if transition_type == 'deterministic':
                    outcomes = [(a, 1.0)]
                else:
                    outcomes = [
                        (a, 0.8),
                        (perpendiculars[a][0], 0.1),
                        (perpendiculars[a][1], 0.1)
                    ]
                
                v_val = 0.0
                for act, prob in outcomes:
                    dr, dc = action_dirs[act]
                    nr, nc = r + dr, c + dc
                    
                    reward = step_reward
                    if nr < 0 or nr >= n or nc < 0 or nc >= n:
                        nr, nc = r, c
                    elif f"{nr},{nc}" in obstacles:
                        nr, nc = r, c
                        
                    if f"{nr},{nc}" in terminals:
                        v_val += prob * terminal_reward
                    else:
                        v_val += prob * (reward + gamma * V[nr, nc])
                
                # Floating point epsilon comparison
                if v_val > max_v + 1e-6:
                    max_v = v_val
                    best_actions = [a]
                elif abs(v_val - max_v) <= 1e-6:
                    best_actions.append(a)
                    
            greedy_policy[state_str] = best_actions
            
    V_list = np.round(V, 2).tolist()
    return jsonify({'values': V_list, 'iterations': iteration, 'greedy_policy': greedy_policy})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
