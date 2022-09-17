#include "api.hpp"
#include <string>
#include <vector>
#include <stack>
#include <map>

using std::string;
using std::vector;
using std::set;
using std::move;
using std::map;
using std::stack;
using std::to_string;

struct TreeNode {
	explicit TreeNode(char type) {
		this->token_type = type;
	}

	explicit TreeNode(char type, int symbol) {
		this->token_type = type;
		this->symbol = symbol;
	}

	bool is_operand() const {
		char t = this->token_type;
		return ((t == 'e') || (t == '#') || (t == 's'));
	}

	char token_type;
	bool nullable = false;
	int symbol = -1;

	set<int> first_pos = set<int>{};
	set<int> last_pos = set<int>{};

	TreeNode *left_tree = nullptr;
	TreeNode *right_tree = nullptr;
};

auto follow_pos = map<int, set<int>>{};
int finish_sym = 0;

int symbol_count;
auto symbol_map = map<int, char>{};

auto sym_add(char sym) {
	symbol_map.emplace(++symbol_count, sym);
	return symbol_count;
}

auto sym_find(char sym) {
	auto res = set<int>{};
	for (auto pair: symbol_map) {
		if (pair.second == sym) {
			res.insert(pair.first);
		}
	}
	return res;
}

template<typename T>
auto union_sets(set<T> set1, set<T> set2) {
	auto res = set<T>{};
	for (T item: set1) {
		res.insert(item);
	}
	for (T item: set2) {
		res.insert(item);
	}
	return res;
}

auto create_tokens_vector(const string &s) {
	auto tok_vector = vector<TreeNode *>();
	tok_vector.push_back(new TreeNode('('));
	char prev_char = '(';

	for (char curr_char: s) {
		if (curr_char == '(' && prev_char == ')' ||
		    curr_char == '(' && prev_char == '*' ||
		    curr_char == '(' && isalnum(prev_char) ||
		    isalnum(curr_char) && isalnum(prev_char) ||
		    isalnum(curr_char) && prev_char == '*' ||
		    isalnum(curr_char) && prev_char == ')') {
			tok_vector.push_back(new TreeNode('+'));
		}

		if (prev_char == '|' && curr_char == '*' ||
		    prev_char == '(' && curr_char == ')' ||
		    prev_char == '|' && curr_char == ')' ||
		    prev_char == '(' && curr_char == '|' ||
		    prev_char == '(' && curr_char == '*' ||
		    prev_char == '|' && curr_char == '|') {
			auto *epsilon = new TreeNode('e');
			epsilon->nullable = true;
			tok_vector.push_back(epsilon);
		}
		if (curr_char == '(' || curr_char == ')' || curr_char == '*' || curr_char == '|') {
			tok_vector.push_back(new TreeNode(curr_char));
		} else {
			tok_vector.push_back(new TreeNode('s', sym_add(curr_char)));
		}
		prev_char = curr_char;
	}
	tok_vector.push_back(new TreeNode(')'));
	tok_vector.push_back(new TreeNode('+'));
	finish_sym = sym_add('#');
	tok_vector.push_back(new TreeNode('#', finish_sym));
	return tok_vector;
}

void set_nullable(TreeNode *node) {
	if (node->is_operand()) {
		return;
	}
	if (node->token_type == '*') {
		node->nullable = true;
		return;
	} else if (node->token_type == '+') {
		node->nullable = (node->left_tree->nullable and node->right_tree->nullable);
	} else {
		node->nullable = (node->left_tree->nullable or node->right_tree->nullable);
	}
}

void set_first_last(TreeNode *node) {
	if (node->is_operand() || node->token_type == '#') {
		if (node->token_type == 'e') {
			return;
		}
		node->first_pos = set<int>{node->symbol};
		node->last_pos = set<int>{node->symbol};
		return;
	}

	auto first_pos = set<int>{};
	auto last_pos = set<int>{};

	switch (node->token_type) {
		case '*': {
			first_pos = union_sets(first_pos, node->left_tree->first_pos);
			last_pos = union_sets(last_pos, node->left_tree->last_pos);
			break;
		}
		case '+': {
			first_pos = union_sets(first_pos, node->left_tree->first_pos);
			if (node->left_tree->nullable) {
				first_pos = union_sets(first_pos, node->right_tree->first_pos);
			}

			last_pos = union_sets(last_pos, node->right_tree->last_pos);
			if (node->right_tree->nullable) {
				last_pos = union_sets(last_pos, node->left_tree->last_pos);
			}
			break;
		}
		case '|': {
			first_pos = union_sets(first_pos, node->left_tree->first_pos);
			first_pos = union_sets(first_pos, node->right_tree->first_pos);

			last_pos = union_sets(last_pos, node->left_tree->last_pos);
			last_pos = union_sets(last_pos, node->right_tree->last_pos);
			break;
		}
	}
	node->first_pos = first_pos;
	node->last_pos = last_pos;
}

void set_follow_pos(TreeNode *node) {
	if (node == nullptr || node->is_operand()) {
		return;
	}
	set_follow_pos(node->left_tree);
	set_follow_pos(node->right_tree);

	if (node->token_type == '*') {
		for (int sym: node->left_tree->last_pos) {
			follow_pos[sym] = union_sets(follow_pos[sym], node->left_tree->first_pos);
		}
	}
	if (node->token_type == '+') {
		for (int sym: node->left_tree->last_pos) {
			follow_pos[sym] = union_sets(follow_pos[sym], node->right_tree->first_pos);
		}
	}
}

void fill_node(stack<TreeNode *> *operands, stack<TreeNode *> *operators) {
	auto node = operators->top();
	operators->pop();

	if (node->token_type != '*') {
		node->right_tree = operands->top();
		operands->pop();
	}

	node->left_tree = operands->top();
	operands->pop();

	set_nullable(node);
	set_first_last(node);

	operands->push(node);
}

auto create_tree(const string &s) {
	auto tok_vector = create_tokens_vector(s);

	stack<TreeNode *> operation_stack{};
	stack<TreeNode *> operand_stack{};

	for (auto token: tok_vector) {
		if (token->is_operand()) {
			token->first_pos = set<int>{token->symbol};
			token->last_pos = set<int>{token->symbol};
			operand_stack.push(token);
			continue;
		}
		char op = token->token_type;

		if (op == '+' || op == '(') {
			operation_stack.push(token);
		} else if (op == ')') {
			while (operation_stack.top()->token_type != '(') {
				fill_node(&operand_stack, &operation_stack);
			}
			operation_stack.pop();
		} else if (op == '|') {
			while (!operation_stack.empty() && operation_stack.top()->token_type == '+') {
				fill_node(&operand_stack, &operation_stack);
			}
			operation_stack.push(token);
		} else {
			operation_stack.push(token);
			fill_node(&operand_stack, &operation_stack);
		}
	}

	while (!operation_stack.empty()) {
		fill_node(&operand_stack, &operation_stack);
	}

	auto root = operand_stack.top();
	set_follow_pos(root);

	return root;
}

void set_final(DFA &dfa, const string &name, set<int> state) {
	if (state.find(finish_sym) != state.end()) {
		dfa.create_state(name, true);
	}
}

void create_dfa(const string &s, DFA &dfa) {
	auto root = create_tree(s);

	auto all_states = map<set<int>, int>();
	auto visited_states = map<set<int>, bool>();
	int count = 1;
	bool add;
	auto cur_state = root->first_pos;
	all_states[cur_state] = count;

	dfa.create_state(to_string(count));
	dfa.set_initial(to_string(count));
	set_final(dfa, to_string(count++), cur_state);

	do {
		add = false;
		visited_states[cur_state] = true;
		for (char symbol: dfa.get_alphabet()) {
			auto new_state = set<int>();
			for (auto follow: sym_find(symbol)) {
				if (cur_state.find(follow) != cur_state.end()) {
					new_state = union_sets(new_state, follow_pos[follow]);
				}
			}
			if (all_states.find(new_state) != all_states.end()) {
				dfa.set_trans(to_string(all_states.find(cur_state)->second), symbol,
				              to_string(all_states[all_states.find(new_state)->first]));
			} else {
				add = true;
				all_states[new_state] = count;
				visited_states[new_state] = false;
				dfa.create_state(to_string(count));
				set_final(dfa, to_string(count), new_state);
				dfa.set_trans(to_string(all_states.find(cur_state)->second), symbol,
				              to_string(count++));
			}
		}
		for (const auto &states: visited_states) {
			if (!states.second) {
				cur_state = states.first;
				add = true;
			}
		}
	} while (add);
}

auto re2dfa(const string &s) {
	DFA res = DFA(Alphabet(s));
	create_dfa(s, res);
	return res;
}