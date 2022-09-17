#include "api.hpp"
#include <iostream>
#include <fstream>
#include <string>

extern DFA re2dfa(const std::string &regExp);

int main() {
	std::ifstream infile("../re2dfa.in");
	std::ofstream outfile("../re2dfa.out");

	std::string line;
	std::getline(infile, line);

	outfile << re2dfa(line).to_string();

	return 0;
}
