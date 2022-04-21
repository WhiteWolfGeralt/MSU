#include "api.hpp"
#include <string>
#include <algorithm>
#include <utility>
#include <vector>
#include <cctype>
#include <stack>
#include <iostream>
#include <map>
#include <fstream>

using std::string;
using std::vector;
using std::set;
using std::move;
using std::map;
using std::stack;
using std::to_string;

class DFACreator {
private:
	enum Operation {
		EPSILON, // eps symbol
		END, // end symbol
		SYMBOL, // single char
		CONCAT, // "dot"
		ALTER, // |
		ITER, // *
		LBRACKET, // (
		RBRACKET // )
	};

	class Node {
	public:
		virtual bool isOperator() { return false; }

		virtual bool isOperand() { return false; }

		explicit Node(Operation op) { this->operation = op; }

		Operation operation;
		bool isNullable = false;

		set<int> firstPos = set<int>();
		set<int> lastPos = set<int>();
	};

	class Operator : public Node {
	public:
		bool isOperator() override { return true; }

		explicit Operator(Operation op) : Node(op) {}

		Node *leftList = nullptr;
		Node *rightList = nullptr;
	};

	class Operand : public Node {
	public:
		bool isOperand() override { return true; }

		explicit Operand(Operation op, int symNumber) : Node(op), symNumber(symNumber) {}

		int symNumber = 0;
	};

	class SymbolPool {
		static int count;
		static map<int, char> symbolMap;
	public:
		static int addSymbol(char sym) {
			symbolMap.try_emplace(++count, sym);
			return count;
		}
		static map<int, char> getMap() {
			return symbolMap;
		};
		static set<int> findByChar(char find) {
			auto ret = set<int>();
			for (auto pair : symbolMap) {
				if (pair.second == find) {
					ret.insert(pair.first);
				}
			}
			return ret;
		}
		static set<char> findByPos(const set<int>& positions) {
			auto ret = set<char>();
			for (auto pair : symbolMap) {
				for (auto find : positions) {
					if (pair.first == find && finishPos != find) {
						ret.insert(pair.second);
					}
				}
			}
			return ret;
		}
	};

	static vector<Node *> prepareRE(const string &s);

	Node *buildTree(const vector<Node *> &regExp);

	static void markNullable(Node* node);
	static void markFirstPos(Node* node);
	static void markLastPos(Node* node);
	static void markFollowPos(Node* node);

	static void buildDFA(Node* root, DFA &res);

	std::ofstream output;
	void tree2dot(Node* root);
	void tree2dotRec(Node* root);

	stack<Node *> operationStack{};
	stack<Node *> operandStack{};

	static map<int, set<int>> followPos;
	static int finishPos;
public:
	DFA create(const string &regExpr);
};

int DFACreator::SymbolPool::count = 0;
map<int, char> DFACreator::SymbolPool::symbolMap = map<int, char>();
map<int, set<int>> DFACreator::followPos = map<int, set<int>>();
int DFACreator::finishPos = 0;

DFA DFACreator::create(const string &regExpr) {
	vector<Node *> rawRE = prepareRE(regExpr);
	Node* root = buildTree(rawRE);
	markFirstPos(root);
	markLastPos(root);
	markFollowPos(root);

	tree2dot(root);

	DFA res = DFA(Alphabet(regExpr));
	buildDFA(root, res);
	return res;
}

vector<DFACreator::Node *> DFACreator::prepareRE(const string &s) {
	auto ret = vector<Node *>();
	ret.push_back((Node *) new Operator(LBRACKET));
	char prevChar = '\0';

	for (char currChar: s) {
		if ((isalpha(currChar) && (isalpha(prevChar) || prevChar == '*')) ||
			(currChar == '(' && (prevChar == ')' || prevChar == '*'))) {
			ret.push_back((Node *) new Operator(CONCAT));
		}

		if ((prevChar == '(' && (currChar == ')' || currChar == '|' || currChar == '*')) ||
			(prevChar == '|' && (currChar == '|' || currChar == ')' || currChar == '*'))) {
			auto *epsilon = new Operand(EPSILON, 'e');
			epsilon->isNullable = true;
			ret.push_back((Node *) epsilon);
		}

		switch (currChar) {
			case '(': {
				ret.push_back((Node *) new Operator(LBRACKET));
				break;
			}
			case ')': {
				ret.push_back((Node *) new Operator(RBRACKET));
				break;
			}
			case '*': {
				ret.push_back((Node *) new Operator(ITER));
				break;
			}
			case '|': {
				ret.push_back((Node *) new Operator(ALTER));
				break;
			}
			default: {
				int number = DFACreator::SymbolPool::addSymbol(currChar);
				ret.push_back((Node *) new Operand(SYMBOL, number));
				break;
			}
		}
		prevChar = currChar;
	}
	ret.push_back((Node *) new Operator(RBRACKET));
	ret.push_back((Node *) new Operator(CONCAT));
	int number = DFACreator::SymbolPool::addSymbol('#');
	DFACreator::finishPos = number;
	ret.push_back((Node *) new Operand(END, number));
	return ret;
}

DFACreator::Node *DFACreator::buildTree(const vector<Node *> &regExp) {
	for (auto token: regExp) {
		if (token->isOperand()) {
			operandStack.push(token);
			continue;
		}

		//now token is only an operator

		Operation opType = token->operation;
		switch (opType) {
			case CONCAT:
			case LBRACKET: {
				operationStack.push(token);
				break;
			}

			case RBRACKET: {
				while (operationStack.top()->operation != LBRACKET) {
					auto operation = (Operator *) operationStack.top();
					operationStack.pop();

					operation->rightList = operandStack.top();
					operandStack.pop();

					operation->leftList = operandStack.top();
					operandStack.pop();

					markNullable(operation);
					operandStack.push((Node *) operation);
				}
				operationStack.pop();
				break;
			}

			case ITER: {
				auto starNode = (Operator *) token;

				starNode->leftList = operandStack.top();
				operandStack.pop();

				markNullable(starNode);
				operandStack.push((Node *) starNode);
				break;
			}

			case ALTER: {
				while (!operationStack.empty() && operationStack.top()->operation == CONCAT) {
					auto *concatNode = (Operator *) operationStack.top();
					operationStack.pop();

					concatNode->rightList = operandStack.top();
					operandStack.pop();

					concatNode->leftList = operandStack.top();
					operandStack.pop();

					markNullable(concatNode);
					operandStack.push((Node *) concatNode);
					break;
				}
				operationStack.push(token);
				break;
			}
			default: {
				//unreachable code
				std::cout << "unreachable code";
			}
		}
	}

	while (!operationStack.empty()) {
		auto operation = (Operator *) operationStack.top();
		operationStack.pop();

		operation->rightList = operandStack.top();
		operandStack.pop();

		operation->leftList = operandStack.top();
		operandStack.pop();

		markNullable(operation);
		operandStack.push((Node *) operation);
	}

	return operandStack.top();
}

void DFACreator::markNullable(DFACreator::Node *node) {
	if (node->isOperand()) {
		return;
	}
	if (node->operation == ITER) {
		node->isNullable = true;
		return;
	}
	auto op = (Operator *) node;
	bool left = op->leftList->isNullable,
		right = op->rightList->isNullable;
	if (op->operation == CONCAT) {
		op->isNullable = (left and right);
	} else {
		op->isNullable = (left or right);
	}
}

void DFACreator::markFirstPos(DFACreator::Node *node) {
	set<int> ret = set<int>{};
	if (node->isOperand() || node->operation == END) {
		if (node->operation == EPSILON) {
			return;
		}
		ret.insert(((Operand *) node)->symNumber);
		node->firstPos = ret;
		return;
	}

	auto op = (Operator *) node;
	if (op->leftList != nullptr) {
		markFirstPos(op->leftList);
	}
	if (op->rightList != nullptr) {
		markFirstPos(op->rightList);
	}

	switch (op->operation) {
		case ITER: {
			for (int sym : op->leftList->firstPos) {
				ret.insert(sym);
			}
			break;
		}
		case CONCAT: {
			for (int sym : op->leftList->firstPos) {
				ret.insert(sym);
			}
			if (op->leftList->isNullable) {
				for (int sym : op->rightList->firstPos) {
					ret.insert(sym);
				}
			}
			break;
		}

		case ALTER: {
			for (int sym : op->leftList->firstPos) {
				ret.insert(sym);
			}
			for (int sym : op->rightList->firstPos) {
				ret.insert(sym);
			}
			break;
		}

		default: {
			//unreachable code
			std::cout << "unreachable code";
		}
	}

	op->firstPos = ret;
}

void DFACreator::markLastPos(DFACreator::Node *node) {
	set<int> ret = set<int>{};
	if (node->isOperand() || node->operation == END) {
		if (node->operation == EPSILON) {
			return;
		}
		ret.insert(((Operand *) node)->symNumber);
		node->lastPos = ret;
		return;
	}

	auto op = (Operator *) node;
	if (op->leftList != nullptr) {
		markLastPos(op->leftList);
	}
	if (op->rightList != nullptr) {
		markLastPos(op->rightList);
	}

	switch (op->operation) {
		case ITER: {
			for (int sym : op->leftList->lastPos) {
				ret.insert(sym);
			}
			break;
		}
		case CONCAT: {
			for (int sym : op->rightList->lastPos) {
				ret.insert(sym);
			}
			if (op->rightList->isNullable) {
				for (int sym : op->leftList->lastPos) {
					ret.insert(sym);
				}
			}
			break;
		}

		case ALTER: {
			for (int sym : op->leftList->lastPos) {
				ret.insert(sym);
			}
			for (int sym : op->rightList->lastPos) {
				ret.insert(sym);
			}
			break;
		}

		default: {
			//unreachable code
			std::cout << "unreachable code";
		}
	}

	op->lastPos = ret;
}

void DFACreator::markFollowPos(DFACreator::Node *node) {
	if (node->isOperand()) {
		return;
	}
	auto op = (Operator *) node;
	if (op->leftList != nullptr) {
		markFollowPos(op->leftList);
	}
	if (op->rightList != nullptr) {
		markFollowPos(op->rightList );
	}
	if (op->operation == ITER) {
		for (int sym : op->leftList->lastPos) {
			for (int val : op->leftList->firstPos) {
				followPos[sym].insert(val);
			}
		}
	}
	if (op->operation == CONCAT) {
		for (int sym : op->leftList->lastPos) {
			for (int val : op->rightList->firstPos) {
				followPos[sym].insert(val);
			}
		}
	}
}

void DFACreator::buildDFA(DFACreator::Node *root, DFA &res) {
	auto statesPool = map<set<int>, int>();
	auto statesMarks = map<set<int>, bool>();
	int count = 0;
	auto currState = root->firstPos;
	statesPool[currState] = count;

	res.create_state(to_string(count));
	res.set_initial(to_string(count));

	if (currState.find(finishPos) != currState.end()) {
		res.create_state(to_string(count), true);
	}

	count++;

	bool wasAdded = true;
	while (wasAdded) {
		wasAdded = false;
		statesMarks[currState] = true;
		auto charSet = DFACreator::SymbolPool::findByPos(currState);
		for (char symbol : charSet) {
			bool isFinish = false;
			auto newState = set<int>();
			auto followPosSet = DFACreator::SymbolPool::findByChar(symbol);
			for (auto followPos_ : followPosSet) {
				if (currState.find(followPos_) != currState.end()) {
					for (int pos: followPos[followPos_]) {
						if (pos == DFACreator::finishPos) {
							isFinish = true;
						}
						newState.insert(pos);
					}
				}
			}
			auto findState = statesPool.find(newState);

			if (findState == statesPool.end()) { //new state
				wasAdded = true;
				statesPool[newState] = count;
				statesMarks[newState] = false;
				res.create_state(to_string(count), isFinish);
				res.set_trans(to_string(statesPool.find(currState)->second),symbol, to_string(count));
			} else { //state already exists
				int oldState = statesPool[findState->first];
				res.set_trans(to_string(statesPool.find(currState)->second), symbol, to_string(oldState));
			}
			count++;
		}

		for (const auto& states : statesMarks) {
			if (!states.second) {
				currState = states.first;
				wasAdded = true;
			}
		}
	}
}

DFA re2dfa(const string &s) {
	DFA res = DFACreator().create(s);
	return res;
}

void DFACreator::tree2dot(Node *root) {
	output.open("../tree4re.dot");
	output << "digraph G {\n";

	tree2dotRec(root);

	output << "}";
	output.close();
}

void DFACreator::tree2dotRec(Node *root) {
	auto address_par = (unsigned long) root;
	string node_info;
	switch (root->operation) {
		case ITER: {
			node_info += "*";
			break;
		}
		case EPSILON: {
			node_info += "eps";
			break;
		}
		case END: {
			node_info += "#";
			break;
		}
		case SYMBOL: {
			set<char> ch = DFACreator::SymbolPool::findByPos(set<int>{((Operand *) root)->symNumber});
			node_info += *(ch.begin());
			break;
		}
		case CONCAT:{
			node_info += "•";
			break;
		}
		case ALTER:{
			node_info += "|";
			break;
		}
	}

	node_info += root->isNullable ? "  T\\n" : "  F\\n";

	node_info += "first: ";
	for (const auto &iter: root->firstPos) {
		node_info += " " + std::to_string(iter);
	}
	node_info += "\\n";

	node_info += "last: ";
	for (const auto &iter: root->lastPos) {
		node_info += " " + std::to_string(iter);
	}
	if (root->isOperand()) {
		output << "\t" << address_par << " [label=\"" << node_info << "\"] [shape=triangle]\n";
		return;
	}
	auto op = (Operator *) root;
	output << "\t" << address_par << " [label=\"" << node_info << "\"] [shape=box]\n";

	if (op->leftList != nullptr) {
		auto address_child = (unsigned long) op->leftList;
		output << "\t" << address_par << " -> " << address_child << "\n";
		tree2dotRec(op->leftList);
	}
	if (op->rightList != nullptr) {
		auto address_child = (unsigned long) op->rightList;
		output << "\t" << address_par << " -> " << address_child << "\n";
		tree2dotRec(op->rightList);
	}
}
