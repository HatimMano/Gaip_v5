import torch #type: ignore
import torch.nn as nn #type: ignore
import torch.optim as optim #type: ignore
import torch.nn.functional as F #type: ignore
import numpy as np
from torch_geometric.data import Data #type: ignore
from torch_geometric.nn import GCNConv #type: ignore
from core.base_agent import BaseAgent 

class GNNQNetwork(nn.Module):
    """
    A simple Graph Neural Network to predict Q-values for each node (cell).
    The network uses two GCNConv layers followed by a linear layer.
    """
    def __init__(self, in_channels=3, hidden_channels=64, out_channels=2):
        super(GNNQNetwork, self).__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.lin = nn.Linear(hidden_channels, out_channels)
    
    def forward(self, data: Data):
        x, edge_index = data.x, data.edge_index
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        q_values = self.lin(x)  
        return q_values

class GNNAgent(BaseAgent):
    """
    An agent that uses a Graph Neural Network to estimate Q-values for actions in a grid-based puzzle.
    
    For each cell (node) in the grid, the network outputs Q-values for placing either 'O' or 'C'.
    The action chosen is (row, col, symbol) from one of the empty cells.
    """
    def __init__(self, learning_rate=0.001, gamma=0.99, 
                 epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        super().__init__(num_actions=None)
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = GNNQNetwork().to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()
        self.initialized = False
        self.symbols = ['O', 'C']

    def initialize(self, env, game: str):
        """
        Initialize the agent with the given environment.
        """
        self.env = env
        self.initialized = True

    def state_to_graph(self, state: np.ndarray) -> Data:
        """
        Converts a 2D grid state into a graph representation.
        
        Each cell becomes a node with a 3-dimensional one-hot feature:
          - 'O'   -> [1, 0, 0]
          - 'C'   -> [0, 1, 0]
          - Empty -> [0, 0, 1]
        
        Nodes are connected with their 4-neighbors (up, down, left, right).
        """
        N = state.shape[0]
        num_nodes = N * N
        x_list = []
        for i in range(N):
            for j in range(N):
                cell = state[i, j]
                if cell == 'O':
                    feat = [1, 0, 0]
                elif cell == 'C':
                    feat = [0, 1, 0]
                else:
                    feat = [0, 0, 1]
                x_list.append(feat)
        x = torch.tensor(x_list, dtype=torch.float)
        
        edge_index = []
        def node_index(i, j):
            return i * N + j
        for i in range(N):
            for j in range(N):
                idx = node_index(i, j)
                if i > 0:
                    edge_index.append([idx, node_index(i-1, j)])
                if i < N - 1:
                    edge_index.append([idx, node_index(i+1, j)])
                if j > 0:
                    edge_index.append([idx, node_index(i, j-1)])
                if j < N - 1:
                    edge_index.append([idx, node_index(i, j+1)])
        edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
        
        data = Data(x=x, edge_index=edge_index)
        return data.to(self.device)
    
    def get_action(self, state: np.ndarray, is_inferencing: bool = False):
        """
        Select an action (row, col, symbol) using an epsilon-greedy policy.
        
        The action is chosen among the empty cells in the grid based on the Q-values predicted by the GNN.
        """
        eps = self.epsilon_min if is_inferencing else self.epsilon
        N = state.shape[0]
        empty_cells = [(i, j) for i in range(N) for j in range(N) if state[i, j] is None]
        if not empty_cells:
            i, j = np.random.randint(0, N), np.random.randint(0, N)
            symbol = np.random.choice(self.symbols)
            return (i, j, symbol)
        
        if np.random.rand() < eps:
            i, j = empty_cells[np.random.randint(len(empty_cells))]
            symbol = np.random.choice(self.symbols)
            return (i, j, symbol)
        
        self.model.eval()
        with torch.no_grad():
            graph = self.state_to_graph(state)
            q_values = self.model(graph)  
        q_values_np = q_values.cpu().numpy()
        
        best_action = None
        best_q = -float('inf')
        for (i, j) in empty_cells:
            idx = i * N + j
            for action_index, symbol in enumerate(self.symbols):
                q_val = q_values_np[idx, action_index]
                if q_val > best_q:
                    best_q = q_val
                    best_action = (i, j, symbol)
        return best_action

    def update(self, state: np.ndarray, action, reward, next_state: np.ndarray):
        """
        Performs a Q-learning update.
        
        Args:
            state (np.ndarray): Current grid state.
            action (tuple): The action taken (row, col, symbol).
            reward (float): Reward received.
            next_state (np.ndarray): Next grid state after the action.
        """
        self.model.train()
        graph = self.state_to_graph(state)
        q_values = self.model(graph)
        
        N = state.shape[0]
        i, j, symbol = action
        idx = i * N + j
        
        if np.all(next_state != None):
            target = reward
        else:
            with torch.no_grad():
                next_graph = self.state_to_graph(next_state)
                next_q_values = self.model(next_graph)
                target = reward + self.gamma * torch.max(next_q_values).item()
        
        current_q = q_values[idx, self.symbols.index(symbol)]
        target_tensor = torch.tensor(target, dtype=torch.float, device=self.device)
        loss = self.criterion(current_q, target_tensor)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)

    def _load_model(self):
        try:
            self.model.load_state_dict(torch.load("gnn_agent_model.pth", map_location=self.device))
            self.model.to(self.device)
            print("✅ GNN model loaded successfully.")
        except Exception as e:
            print(f"❌ Error loading GNN model: {e}")

    def save_model(self):
        torch.save(self.model.state_dict(), "gnn_agent_model.pth")
        print("✅ GNN model saved successfully.")
