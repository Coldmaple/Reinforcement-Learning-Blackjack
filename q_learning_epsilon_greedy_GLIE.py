import gym
import matplotlib
import numpy as np
import sys
import itertools

from collections import defaultdict
if "../" not in sys.path:
  sys.path.append("../") 
from blackjack import BlackjackEnv
import plot

env = BlackjackEnv()

def make_epsilon_greedy_policy(Q, epsilon, nA):

    def policy_fn(observation):
        A = np.ones(nA, dtype=float) * epsilon / nA
        best_action = np.argmax(Q[observation])
        A[best_action] += (1.0 - epsilon)
        return A
    return policy_fn

def train(env, train_episodes, discount_factor=1.0, epsilon=0.1):
    
    # The final action-value function.
    # A nested dictionary that maps state -> (action -> action-value).
    Q = defaultdict(lambda: np.zeros(env.action_space.n))

    # Keeps track of useful statistics
    stats = plot.EpisodeStats(
        episode_lengths=np.zeros(train_episodes),
        episode_rewards=np.zeros(train_episodes))    
    
    # The policy we're following
    policy = make_epsilon_greedy_policy(Q, epsilon, env.action_space.n)

    # Total reward
    reward_total = 0

    # (state, action) key
    counter_state_action = defaultdict(int)
    
    for i_episode in range(train_episodes):
        # Print out which episode we're on, useful for debugging.
        if (i_episode + 1) % 100 == 0:
            print("\rEpisode {}/{}.".format(i_episode, train_episodes), end="")
            sys.stdout.flush()
        
        # Reset the environment and pick the first action
        state = env.reset()
        
        # One step in the environment
        # total_reward = 0.0
        for t in itertools.count():
            # Take a step
            action_probs = policy(state)
            action = np.random.choice(np.arange(len(action_probs)), p=action_probs)
            next_state, reward, done, _ = env.step(action)

            # Update statistics
            stats.episode_rewards[i_episode] += reward
            stats.episode_lengths[i_episode] = t
            
            # TD Update
            best_next_action = np.argmax(Q[next_state])    
            td_target = reward + discount_factor * Q[next_state][best_next_action]
            td_delta = td_target - Q[state][action]
            # Update learning rate
            counter_state_action[state, action] += 1
            alpha = 1 / (1 + counter_state_action[state, action])
            Q[state][action] += alpha * td_delta
                
            if done:
                # Add reward
                reward_total += reward
                break
                
            state = next_state

    return reward_total

# Q, stats, reward_total, counter_state_action = train(env, train_episodes=10000)

# For plot: Create value function from action-value function
# by picking the best action at each state
# V = defaultdict(float)
# for state, actions in Q.items():
#     action_value = np.max(actions)
#     V[state] = action_value
# plot.plot_value_function(V, title="Optimal Value Function (10000 episodes)")

def test(test_episodes, Q, epsilon=0.1):
    # Test

    # The policy we're following
    policy = make_epsilon_greedy_policy(Q, epsilon, env.action_space.n)

    wins = 0
    for i_episode in range(1, test_episodes + 1):
        state = env.reset()

        for t in range(100):
            probs = policy(state)
            action = np.random.choice(np.arange(len(probs)), p=probs)
            next_state, reward, done, _ = env.step(action)
            if done:
                if reward > 0:
                    wins += 1
                    break
                else: break
            state = next_state

    print('\nWinning ratio: %.4f%%' % ((float(wins) / test_episodes * 100)))

# test(1000000, Q)
# plot.plot_episode_stats(stats)
# print(counter_state_action)