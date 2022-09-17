#include "api.hpp"
#include <string>
#include <fstream>
#include <iostream>
#include <utility>
#include <vector>
#include <set>
#include <algorithm>
#include <map>

using std::string;
using std::cout;
using std::vector;
using std::set;
using std::pair;
using std::map;

namespace {
	class MyDFA {
	private:
		string const EPSILON = "epsilon";
		string const FAKE_START = "FAKE_START";
		string const FAKE_FINISH = "FAKE_FINISH";
		string initState;

		struct State {
			int inputRule = 0;
			map<string, string> rules = map<string, string>();
		};

		map<string, State> mainRules = map<string, State>();

		template<class STL, typename T>
		bool findInSTL(STL stl, T elem) {
			return std::find(stl.begin(), stl.end(), elem) != stl.end();
		}

		void fillRules(const DFA &dfa) {
			auto finishStates = dfa.get_final_states();
			initState = dfa.get_initial_state();
			mainRules[FAKE_START].rules[initState] = EPSILON;

			for (const string &outState: dfa.get_states()) {
				for (char symbol: dfa.get_alphabet()) {
					if (dfa.has_trans(outState, symbol)) {
						string inState = dfa.get_trans(outState, symbol);
						mainRules[inState].inputRule++;
						if (mainRules[outState].rules.count(inState)) {
							mainRules[outState].rules[inState] += "|" + string(1, symbol);
						} else {
							mainRules[outState].rules[inState] = string(1, symbol);
						}
					}
					if (findInSTL(finishStates, outState)) {
						mainRules[outState].rules[FAKE_FINISH] = EPSILON;
					}
				}
			}
		}

		map<string, string> getAndDeleteInput(const string &delState) {
			auto ret = map<string, string>();
			for (const auto &state: mainRules) {
				auto newMap = map<string, string>();
				for (const auto &rule: state.second.rules) {
					if (rule.first != delState) {
						newMap[rule.first] = rule.second;
					} else {
						ret[state.first] = rule.second;
					}
				}
				mainRules[state.first].rules = newMap;
			}
			return ret;
		}

		string getAndDeleteR(const string &q, const string &p) {
			string R;
			auto newMap = map<string, string>();
			for (const auto &state: mainRules) {
				if (state.first == q) {
					for (const auto &rule: state.second.rules) {
						if (rule.first == p) {
							R = rule.second;
						} else {
							newMap[rule.first] = rule.second;
						}
					}
					mainRules[q].rules = newMap;
				}
			}
			return R;
		}

		static string getLoop(const map<string, string> &input, const string &s) {
			for (const auto &state: input) {
				if (state.first == s) {
					return state.second;
				}
			}
			return "";
		}

		string getNextState() {
			int minSum = -1;
			string minState;
			for (const auto &state: mainRules) {
				if (state.first == FAKE_START) {
					continue;
				}
				auto rule = state.second;
				if (minSum != -1) {
					int mayBe = rule.inputRule + rule.rules.size();
					if (mayBe < minSum) {
						minSum = mayBe;
						minState = state.first;
					}
				} else {
					minSum = rule.inputRule + rule.rules.size();
					minState = state.first;
				}
			}
			return minState;
		}

	public:
		string buildRE() {
			string currState = getNextState();
			while (!currState.empty()) {
				auto q_i = getAndDeleteInput(currState);
				auto p_i = mainRules[currState].rules;
				string S = getLoop(q_i, currState);
				for (const auto &q: q_i) {
					for (const auto &p: p_i) {
						string Q_i = q.second, P_i = p.second;
						string newTrans;
						string R = getAndDeleteR(q.first, p.first);
						if (!R.empty()) {
							if (R == EPSILON) {
								R = "";
							}
							newTrans += "(" + R + ")|";
						}
						newTrans += "((" + (q.second == EPSILON ? "" : q.second) + ")" + "(" + S + ")*" +
								"(" + (p.second == EPSILON ? "" : p.second) + "))";
						mainRules[q.first].rules[p.first] = newTrans;
					}
				}
				mainRules.erase(currState);
				currState = getNextState();
			}
			return mainRules[FAKE_START].rules[FAKE_FINISH];
		}

		static string build(const DFA &d) {
			MyDFA myDfa;
			myDfa.fillRules(d);
			return myDfa.buildRE();
		}
	};
}

std::string dfa2re(DFA &d) {
	return MyDFA::build(d);
}
