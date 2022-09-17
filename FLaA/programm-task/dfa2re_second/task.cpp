#include "api.hpp"
#include <string>
#include <set>
#include <map>

using std::string;
using std::set;
using std::map;

auto transitions = map<string, map<string, string>>{};

void add_transition(const DFA &dfa, const string& first_state, char trans_symbol)
{
	string second_state = dfa.get_trans(first_state, trans_symbol);
	unsigned count_trans = transitions[first_state].count(second_state);
	if (count_trans > 0)
	{
		transitions[first_state][second_state] += "|" + string(1, trans_symbol);
	}
	else
	{
		transitions[first_state][second_state] = string(1, trans_symbol);
	}
}

void read_dfa(const DFA &dfa)
{
	transitions["new_init_state"][dfa.get_initial_state()] = "epsilon_symbol";
	for (const string &first_state: dfa.get_states())
	{
		for (char trans_symbol: dfa.get_alphabet())
		{
			if (dfa.has_trans(first_state, trans_symbol))
			{
				add_transition(dfa, first_state, trans_symbol);
			}
		}
	}
	for (const string& finish_state : dfa.get_final_states())
	{
		transitions[finish_state]["new_finish_state"] = "epsilon_symbol";
	}
}

string get_curr_state(const set<string>& state_pool)
{
	auto count_trans = map<string, unsigned>();
	for(const auto& state: state_pool)
	{
		count_trans[state] = 0;
	}
	for (const auto &state: transitions)
	{
		if (state.first == "new_init_state")
		{
			continue;
		}
		count_trans[state.first] += state.second.size();
		for (const auto& trans : state.second)
		{
			if (trans.first == "new_finish_state")
			{
				continue;
			}
			count_trans[trans.first] += 1;
		}
	}
	string min_state = count_trans.begin()->first;
	unsigned min_trans = count_trans.begin()->second;
	for (const auto& state : count_trans)
	{
		if (state.second < min_trans)
		{
			min_state = state.first;
			min_trans = state.second;
		}
	}
	return min_state;
}

map<string, string> get_input_trans(const string &curr_state)
{
	auto result = map<string, string>();
	for (const auto &state: transitions)
	{
		auto trans = map<string, string>();
		for (const auto &transition: state.second)
		{
			if (transition.first != curr_state)
			{
				trans[transition.first] = transition.second;
			}
			else
			{
				result[state.first] = transition.second;
			}
		}
		transitions[state.first] = trans;
	}
	return result;
}

string get_loop_trans(const string &s, const map<string, string> &all_states)
{
	auto find_loop = all_states.find(s);
	return find_loop != all_states.end() ? find_loop->second : "";
}

string get_q_p_trans(const string &q_i, const string &p_i)
{
	string result;
	auto trans = map<string, string>();
	for (const auto &state: transitions)
	{
		if (state.first == q_i)
		{
			for (const auto &transition: state.second)
			{
				if (transition.first == p_i)
				{
					result = transition.second;
				}
				else
				{
					trans[transition.first] = transition.second;
				}
			}
			transitions[q_i] = trans;
		}
	}
	return result;
}

string dfa2re(DFA &d)
{
	read_dfa(d);
	set<string> remaining_states = d.get_states();
	do
	{
		string curr_state = get_curr_state(remaining_states); //s
		auto input_trans = get_input_trans(curr_state); //q_i
		auto output_trans = transitions[curr_state]; //p_i
		string loop_trans = get_loop_trans(curr_state, input_trans); //S

		for (const auto &q_i: input_trans)
		{
			for (const auto &p_i: output_trans)
			{
				string transition;
				string q_p_trans = get_q_p_trans(q_i.first, p_i.first);
				if (!q_p_trans.empty())
				{
					transition += q_p_trans == "epsilon_symbol" ? "|" : "(" + q_p_trans + ")|";
				}
				transition += "(";
				if (q_i.second == "epsilon_symbol")
				{
					transition += "";
				}
				else
				{
					transition += "(" + q_i.second + ")";
				}
				transition += "(" + loop_trans + ")*";
				if (p_i.second == "epsilon_symbol")
				{
					transition += "";
				}
				else
				{
					transition += "(" + p_i.second + ")";
				}
				transition += ")";

				transitions[q_i.first][p_i.first] = transition;
			}
		}
		transitions.erase(curr_state);
		remaining_states.erase(curr_state);
	} while (!remaining_states.empty());
	return transitions["new_init_state"]["new_finish_state"];
}
