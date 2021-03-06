import gym
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sys

from collections import defaultdict
if "../" not in sys.path:
  sys.path.append("../") 
from blackjack import BlackjackEnv
import plot

matplotlib.style.use('ggplot')

env = BlackjackEnv()

def make_epsilon_greedy_policy(Q, epsilon, nA):

    def policy_fn(observation):
        A = np.ones(nA, dtype=float) * epsilon / nA
        best_action = np.argmax(Q[observation])
        A[best_action] += (1.0 - epsilon)
        return A
    return policy_fn


def train(env, train_episodes, discount_factor=1.0, epsilon=0.1):
    
    # Keeps track of sum and count of returns for each state
    # to calculate an average. We could use an array to save all
    # returns (like in the book) but that's memory inefficient.
    returns_sum = defaultdict(float)
    returns_count = defaultdict(float)
    
    # The final action-value function.
    # A nested dictionary that maps state -> (action -> action-value).
    Q = defaultdict(lambda: np.zeros(env.action_space.n))
    
    # The policy we're following
    policy = make_epsilon_greedy_policy(Q, epsilon, env.action_space.n)

    # Print episode-winning ratio curve
    record = []
    episode_array = []
    
    # Total reward
    reward_total = 0

    # Train
    for i_episode in range(1, train_episodes + 1):
        # Print out which episode we're on, useful for debugging.
        if i_episode % 100 == 0:
            print("\rEpisode {}/{}.".format(i_episode, train_episodes), end="")
            sys.stdout.flush()

        # Generate an episode.
        # An episode is an array of (state, action, reward) tuples
        episode = []
        state = env.reset()
        for t in range(100):
            probs = policy(state)
            action = np.random.choice(np.arange(len(probs)), p=probs)
            next_state, reward, done, _ = env.step(action)
            episode.append((state, action, reward))
            if done:
                reward_total += reward
                break
            state = next_state

        # Find all (state, action) pairs we've visited in this episode
        # We convert each state to a tuple so that we can use it as a dict key
        sa_in_episode = set([(tuple(x[0]), x[1]) for x in episode])
        for state, action in sa_in_episode:
            sa_pair = (state, action)
            # Find the first occurance of the (state, action) pair in the episode
            first_occurence_idx = next(i for i,x in enumerate(episode)
                                       if x[0] == state and x[1] == action)
            # Sum up all rewards since the first occurance
            G = sum([x[2]*(discount_factor**i) for i,x in enumerate(episode[first_occurence_idx:])])
            # Calculate average return for this state over all sampled episodes
            returns_sum[sa_pair] += G
            returns_count[sa_pair] += 1.0
            Q[state][action] = returns_sum[sa_pair] / returns_count[sa_pair]

    return Q

# Q = train(env, train_episodes=10000)

def test(test_episodes, Q, epsilon=0.1):
    # Test

    # The policy we're following
    policy = make_epsilon_greedy_policy(Q, epsilon, env.action_space.n)

    reward_total = 0
    for i_episode in range(1, test_episodes + 1):
        state = env.reset()

        for t in range(100):
            probs = policy(state)
            action = np.random.choice(np.arange(len(probs)), p=probs)
            next_state, reward, done, _ = env.step(action)
            if done:
                reward_total += reward
                break
            state = next_state

    return reward_total

# For plot: Create value function from action-value function
# by picking the best action at each state
# V = defaultdict(float)
# for state, actions in Q.items():
#     action_value = np.max(actions)
#     V[state] = action_value
# plot.plot_value_function(V, title="Optimal Value Function (10000 episodes)")